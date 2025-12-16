# fmt: off
# ruff: noqa: N802, UP031, N806, E501
import operator as op

from . import cypher_parser as cp
from .cypher_ast import Atom, Either, Option, Pattern
from .util import bind, compose, const, delay, identity, map, reduce, splice


def cons_when(b, x, xs): return [x, *xs] if b else xs

class PP:
    def __init__(self, f): self.f = f
    def __mod__(self, other): return PP(compose(self.f, other.f))
    def __and__(self, other): return PP(compose(self.f, other.f))
    def __add__(self, other): return PP(Either.fold(self, other))
    def __lshift__(self, other): return PP(lambda x: (self(x) & other))
    def __rshift__(self, other): return PP(lambda x: (self & other(x)))
    def __mul__(self, other): return PP(lambda p: (self(p[0]) & other(p[1])))
    def __call__(self, x): return self.f(x)
    def __neg__(self): return self('')

def delay_PP(f): return PP(compose(PP, delay(f)))

def if_(y,z): return PP(lambda x: y if x else z)

nil = PP(identity)

string = PP(lambda s: PP(lambda t: s + t))
char = string

def many(p): return PP(lambda xs: reduce(op.and_, map(p, xs), nil))
many1 = many

def opt_bool(ds): return PP(lambda x: ds if x else nil)
def opt_or(q, p): return PP(Option.map_or(q, p))
opt = bind(opt_or, nil)

def id_if_eq(e, p): return PP(lambda x: (nil if x==e else p(x)))

def wrap(o, c): return PP(lambda p: (char(o) & p & char(c)))
sp    = char(' ')
sqbr  = wrap('[', ']')
paren = wrap('(', ')')
brace = wrap('{', '}')

def to_string(x): return x('')
def print_(x): print('%s\n' % to_string(x))

def sep_by(sep, p):
    def p_and_sep(t, x): return p(x)(sep(t))
    return PP(lambda xs:
              nil if xs == [] else
              PP(lambda t: reduce(p_and_sep, reversed(xs[:-1]), p(xs[-1])(t))))

comma_sep = bind(sep_by, string(','))

def formula(x):
    @delay
    def formula(n, x):
        def p(m, q): return (paren if m > n else identity)(q(formula(m)))
        return x.match(
            ATOM=string,
            NOT=lambda x: p(0, lambda f: char('!') & f(x)),
            AND=lambda x, y: p(1, lambda f: f(x) & char('&') & f(y)),
            OR=lambda x, y: p(2, lambda f: f(x) & char('|') & f(y)))

    return formula(2)(x)

def kw(x): return string(' %s ' % x)

p = string
identifier = string
variable = string

dash = p('-')
colon = p(':')
dot = p('.')
star = p('*')
equ = p('=')
bar = p('|')
opt_var = opt(variable << equ)

qualified_name = opt(identifier << dot) * identifier

def int_lit(x): return string(str(x))
def range_(expr): return opt(expr) * (p('..') >> opt(expr)) + expr

escapes = \
    { '\\' : '\\\\'
    , '\n' : '\\n'
    , '\t' : '\\t'
    , '\r' : '\\r'
    , '\b' : '\\b'
    , '\'' : "\\'"
    }

def escaped(s):
    def esc_char(c): return escapes.get(c, c)
    return ''.join(map(esc_char, s))


def Top(expr):
    where = kw('WHERE') >> expr
    map_literal = brace % comma_sep(identifier * (colon >> expr))

    def PatternPrinters():
        @delay_PP
        def element_with(px, ex):
            e, x = ex
            return (opt(identifier)(e['variable'])
                    & opt(colon >> formula)(e['formula']) & px(x)
                    & id_if_eq([], map_literal)(e['properties']))

        element = PP(lambda p: paren(element_with(const(nil))((p, ()))))

        def arrow_pattern(e, q):
            dq = dash >> id_if_eq(e, sqbr % q) << dash
            return PP(lambda x: x.match(LEFT=lambda x: p('<') & dq(x),
                                        RIGHT=lambda x: dq(x) & p('>'),
                                        BIDI=dq))

        relationship = element_with(opt(star >> opt(int_lit) * opt(p('..') >> opt(int_lit))))
        link = arrow_pattern((Pattern.empty, Option.NONE()), relationship) * element
        chain = element * many(link)
        pattern = comma_sep(opt_var * chain)
        return locals()

    Pat = PatternPrinters()

    def AtomP():
        def literal(x):
            return x.match(
                Null = lambda:kw('NULL'),
                Bool = if_(kw('TRUE'), kw('FALSE')),
                Quoted = compose(wrap('\'','\'') % string, escaped),
                Float = compose(string, str),
                Int = int_lit,
                List = sqbr % comma_sep(expr),
                Map = map_literal)

        alt = (kw('WHEN') >> expr) * (kw('THEN') >> expr)
        case_expression = ((kw('CASE') >> opt(expr))
                           * ((many1(alt) * opt(kw('ELSE') >> expr)) << kw('END')))
        filter_expression = variable * (kw('IN') >> expr) * opt(where)
        function_args = opt_bool(kw('DISTINCT')) * comma_sep(expr)

        def quant(x):
            return kw(x.match(
                ALL=lambda:'ALL',
                ANY=lambda:'ANY',
                NONE=lambda:'NONE',
                SINGLE=lambda:'SINGLE'))

        def existential(rq): return rq + (Pat['pattern'] * opt(kw('WHERE') >> expr))


        @delay_PP
        def atom(subquery, x):
            def exists(x):
                def if_variant_else(thunk, f, key, x):
                    return f(x._value) if x._key == key else thunk()
                def x_not_null(): return paren(expr(x) + string(' IS NOT NULL '))
                def exists_atom(a):
                    exist_patt_pred = kw('EXISTS') >> (paren % Pat['chain'])
                    def not_expr():
                        return if_variant_else(x_not_null, exist_patt_pred,
                                               a._Key.PATTERN_PREDICATE, a)
                    return if_variant_else(not_expr, compose(atom(subquery), Atom.EXISTS),
                                           a._Key.EXPRESSION, a)
                return if_variant_else(x_not_null, exists_atom, x._Key.ATOM, x)

            return x.match(
                PARAMETER=lambda x: string('$' + x),
                CASE_EXPR=case_expression,
                COUNT=lambda: string('COUNT (*)'),
                EXISTENTIAL=lambda x: kw('EXISTS') & brace(existential(subquery)(x)),
                LIST_COMP=sqbr % (filter_expression * opt(bar >> expr)),
                PATTERN_COMP=sqbr % (opt_var * Pat['chain'] * opt(where) * (bar >> expr)),
                QUANTIFIER=PP(quant) * (paren % filter_expression),
                FUNCTION_CALL=qualified_name * (paren % function_args),
                VARIABLE=variable,
                PATTERN_PREDICATE=Pat['chain'],
                EXPRESSION=paren % expr,
                LITERAL=PP(literal),
                EXISTS=PP(exists)
            )

        return locals()

    @PP
    def projection_body(b):
        sort_order = if_(kw('DESC'), kw('ASC'))
        sort_item = expr * opt(sort_order)
        skip = kw('SKIP') >> expr
        limit = kw('LIMIT') >> expr
        order = (kw('ORDER') & kw('BY')) >> comma_sep(sort_item)

        @compose(PP, splice)
        def projection_items(has_star, items):
            projection_item = expr * opt(kw('AS') >> string)
            return comma_sep(identity)(cons_when(has_star, star, map(projection_item, items)))

        return (opt_bool(kw('DISTINCT'))(b['distinct'])
                & projection_items(b['projection_items'])
                & opt(order)(b['order']) & opt(skip)(b['skip']) & opt(limit)(b['limit']))

    yield_items = comma_sep(opt(identifier << kw('AS')) * variable) * opt(where)

    def procedure_call(wrap_args, wrap_yields):
        return ((kw('CALL') >> qualified_name)
                * wrap_args(paren % comma_sep(expr))
                * opt(kw('YIELD') >> wrap_yields(yield_items)))

    standalone_call = procedure_call(opt, bind(opt_or, star))

    with_clause = kw('WITH') >> projection_body * opt(where)

    @delay_PP
    def union(sq, x):
        sep = if_(kw('UNION ALL'), kw('UNION'))
        union_all, single_queries = x
        return sep_by(sep(union_all), sq)(single_queries)

    @PP
    def reading_clause(x):
        return x.match(
            MATCH_=opt_bool(kw('OPTIONAL')) * ((kw('MATCH') >> Pat['pattern']) * opt(where)),
            IN_QUERY_CALL=kw('CALL') >> (qualified_name * (paren % comma_sep(expr))) * opt(yield_items),
            UNWIND=(kw('UNWIND') >> expr) * (kw('AS') >> string))

    def exists_query(q):
        @PP
        def query(x):
            return x.match(
                SUCCEED=lambda: kw('RETURN TRUE'),
                READ=reading_clause * query,
                WITH=with_clause * query
            )
        return union(query)(q)

    atom = AtomP()['atom'](PP(exists_query))

    @PP
    def updating_clause(x):
        property_lookup = dot >> string
        property_expression = atom * property_lookup
        node_labels = colon >> sep_by(colon, string)
        remove_item = string * node_labels + property_expression
        def set_item(x):
            return x.match(
                SET_PROPERTY=property_expression * (equ >> expr),
                SET_VARIABLE=variable * (equ >> expr),
                INCREMENT=variable * (p('+=') >> expr),
                LABEL=variable * node_labels
            )
        set = kw('SET') >> comma_sep(set_item)
        merge_action = kw('ON') >> if_(kw('MATCH'), kw('CREATE')) * set
        return x.match(
            REMOVE = kw('REMOVE') >> comma_sep(remove_item),
            MERGE  = kw('MERGE') >> opt_var * Pat['chain'] * many(merge_action),
            DELETE = opt_bool(kw('DETACH')) * (kw('DELETE') >> comma_sep(expr)),
            CREATE = kw('CREATE') >> Pat['pattern'],
            SET    = set)

    @PP
    def regular_query(q):
        @PP
        def query(x):
            return x.match(
                STOP=lambda: nil,
                RETURN=kw('RETURN') >> projection_body,
                READ=reading_clause * query,
                UPD=updating_clause * query,
                WITH=with_clause * query)
        return union(query)(q)

    return locals()

@PP
def expr(x):
    def op_token(x):
        kind, x = x
        return {'Word': string, 'Punct': string}[kind](x)

    op_tokens = sep_by(sp, PP(op_token))
    top = Top(expr)
    atom = top['atom']
    return x.match(
        ATOM=atom,
        BINOP=lambda op, x, y: expr(x) & sp & op_tokens(op) & sp & expr(y),
        PREOP=lambda op, x: op_tokens(op) & sp & expr(x),
        POSTOP=lambda op, x: expr(x) & sp & op_tokens(op),
        LABEL_IS=expr * (char(':') >> formula),
        PROP_REF=expr * (char('.') >> string),
        LIST_REF=expr * (sqbr % range_(expr)))

top = Top(expr)
statement = top['regular_query'] + top['standalone_call']

def test_(parser, printer, s, f=identity):
    ast = cp.parse(parser, s)
    print('AST   : %s' % repr(ast))
    s2 = -printer(f(ast))
    print('String: %s' % s2)

test_expr = bind(test_, cp.expr, expr)
test_st = bind(test_, cp.statement, statement)
