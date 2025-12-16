# ruff: noqa: E701, N806, N802, UP031, E501, I001
from functools import reduce

import regex

# fmt: off
from funcparserlib.parser import (NoParseError, Parser, a, finished, forward_decl,
                                  many, maybe, oneplus, pure, some)

from .cypher_ast import (Atom, Either, Existential, Expr, Formula, Id, Option,
                         Pattern, Query, T, Types, UpdatingClause)
from .util import (bind, compose, const, delay_decorator, filter, forkr, fst, identity,
                   map, maybe_lazy, not_empty, pair_with, raise_, snd, splice)

concat = ''.join

def fix_aux(f):
    self = forward_decl()
    aux, fixed = f(self)
    self.define(fixed)
    return aux, self

def fix(f): return snd(fix_aux(compose(pair_with(()), f)))
def fail(m): return Parser(lambda _, s: raise_(NoParseError(m, s)))

@delay_decorator(Parser)
def consumed(p, tokens, s1):
    _, s2 = p.run(tokens, s1)
    return tokens[s1.pos:s2.pos], s2

@delay_decorator(Parser)
def reg_(r, tokens, s1):
    m = r.match(tokens, pos=s1.pos)
    return (string(m[0]) if m else fail('REGEX(%s)' % r)).run(tokens, s1)

def reg(r): return reg_(regex.compile(r))
def pair(a, b):
    return ((a >> Id.ID) + (b >> Id.ID)) >> splice(lambda x, y: (x.get(), y.get()))

char = a
def string(s): return reduce(lambda p, q: p + q, map(char, s)) >> concat
def one_of(s): return some(lambda c: c in s)
def none_of(q): return some(lambda c: c not in q)
def filt(m, f, p): return p.bind(lambda x: pure(x) if f(x) else fail(m))
def either(p, q): return p >> Either.LEFT | q >> Either.RIGHT
def opt(p): return maybe(p) >> bind(maybe_lazy, Option.NONE, Option.SOME)
def opt_bool(p): return p >> const(True) | pure(False)
def opt_or(q, p): return p >> Option.SOME | q >> const(Option.NONE())
def or_ret(y, p): return p | pure(y)
def choices(ps): return reduce(lambda p, q: p | q, ps)
def sep_by1(sep, p): return pair(p, many(-sep + p)) >> splice(lambda h, t: [h, *t])
def sep_by0(sep, p): return sep_by1(sep, p) | pure([])
def wrap(p,q): return -char(p) + q + -char(p)
def tag(p, x): return p >> pair_with(x)

def translate(pairs): return choices([a(i) >> const(o) for i, o in pairs])

escape_code = translate(
    [ ('"', '"'), ('\'', '\''), ('\\', '\\'), ('n', '\n'),
      ('r', '\r'), ('t', '\t'), ('b', '\b'), ('f', '\012') ])

def quoted_char(q): return -char('\\') + escape_code | char('\\') | none_of(q)
def inside(q): return many(quoted_char(q)) >> concat
quoted = wrap("'", inside("'")) | wrap('"', inside('"'))

back_quoted_char = -char('`') + char('`') | none_of('`')
inside_back_quote = many(back_quoted_char) >> concat
back_quoted = wrap('`', inside_back_quote)

word =  reg(r'[a-zA-Z]\w*')
integer = reg(r'\d+') >> int
float_ = reg(r'\d*\.\d+([eE][+-]?\d+|)') >> float

def any_str(strings): return choices(map(string, strings))

punct = ( any_str([ '+=', '>=', '<=', '<>', '=~', '..' ])
        | one_of('{}()[],+-!&|:^*/%<>=.$')
        )

token = ( tag(word   ,'Word')
        | tag(quoted ,'Quoted')
        | tag(float_ ,'Float')
        | tag(integer,'Int')
        | tag(punct  ,'Punct')
        | tag(back_quoted,    'BackQuoted')
        | tag(reg(r'\s+'), 'Space')
        )

tokens = many(token) >> bind(filter, lambda tok: tok[0] != 'Space')

def tokenize(s: str): return (tokens + -finished).parse(s)
def parse(p, string): return (p + -finished).parse(tokenize(string))
def token(types): return some(lambda t: t[0] in types) >> snd

def punct(s): return a(('Punct', s))
def bracket(op, cl, p): return -punct(op) + p + -punct(cl)

paren = bind(bracket, '(', ')')
brace = bind(bracket, '{', '}')
sqbr  = bind(bracket, '[', ']')

comma_sep = bind(sep_by1, punct(','))
comma_sep0 = bind(sep_by0, punct(','))

colon, star, bar, equ, dot = map(punct, ':*|=.')

identifier = token(['Word','BackQuoted'])
namespace = -identifier + dot
variable = identifier

def tok_is_kw(s): return lambda c, t: c == 'Word' and t.upper() == s
def kw(s): return some(splice(tok_is_kw(s.upper()))) >> const(())

opt_var = opt(variable + -equ)
float_literal = token(['Float'])
int_literal = token(['Int'])

Variable = str
Identifier = str

def formula_inc(f2):
    atom = identifier >> Formula.ATOM
    ops = { 1: punct('&') >> const(Formula.AND),
            2: punct('|') >> const(Formula.OR)}
    def f(n):
        def app(x, o, y): return o(x,y)
        def not_(f0): return -punct('!') + f0 >> Formula.NOT
        return (fix(lambda f0: paren(f2) | not_(f0) | atom) if n == 0 else
                fix(lambda f1: f(n-1) + ops[n] + f1 >> splice(app) | f(n-1)))
    return f(2)

formula = fix(formula_inc)

def and_labels(l1, ls): return reduce(Formula.AND, map(Formula.ATOM, [l1, *ls]))
label_and_list = identifier + -colon + sep_by0(colon, identifier) >> splice(and_labels)
label_match = -colon + (label_and_list | formula)

property_lookup = -punct('.') + identifier
qualified_name = opt(namespace) + identifier


def PatternP(expr):
    Arrow = Pattern.Arrow
    map_literal = brace(comma_sep0 (identifier + -colon + expr))

    def element_with(px):
        def mk(var, form, x, props): return {'variable':var, 'formula':form, 'properties':props}, x
        return opt(variable) + opt(-colon + formula) + px + or_ret([], map_literal) >> splice(mk)

    def arrow_pattern(e, q):
        dq = bracket('-', '-', or_ret(e, sqbr(q)))
        return ( -punct('<') + dq >> Arrow.LEFT
               | dq + punct('>') >> fst >> Arrow.RIGHT
               | dq >> Arrow.BIDI
               )

    range = -star + opt(int_literal) + opt(-punct('..') + opt(int_literal))
    empty = Option.NONE(), Option.NONE(), []
    element = paren(element_with(pure(()))) >> fst
    link = arrow_pattern((empty, Option.NONE()), (element_with(opt(range)))) + element
    chain = element + many(link)
    pattern = comma_sep(opt_var + chain)

    def includes_relation(x): return not_empty(snd(x))

    return {'chain': chain, 'pattern': pattern, 'includes_relation': includes_relation}

def AtomP(expr, subquery):
    map_literal = brace(comma_sep0(identifier + -colon + expr))
    where = -kw('WHERE') + expr

    Literal = Atom.Literal
    Quant = Atom.Quant

    Pat = PatternP(expr)
    boolean = kw('FALSE') >> const(False) | kw('TRUE') >> const(True)

    literal = ( kw('NULL')        >> const(Literal.NULL())
              | boolean           >> Literal.BOOL
              | float_literal     >> Literal.FLOAT
              | int_literal       >> Literal.INT
              | token(['Quoted']) >> Literal.QUOTED
              | sqbr(comma_sep0(expr)) >> Literal.LIST
              | map_literal       >> Literal.MAP
              )

    case_alt = -kw('WHEN') + expr + -kw('THEN') + expr
    tail = oneplus(case_alt) + (opt(-kw('ELSE') + expr) + -kw('END'))
    case_expression = -kw('CASE') + ((expr >> Option.SOME) + tail | (pure(Option.NONE()) + tail))
    filter_expression = pair(variable + -kw('IN') + expr, opt(where))
    pattern_comprehension = pair(pair(pair(opt_var, Pat['chain']), opt(where)), -bar + expr)
    pattern_predicate = filt('patt pred', Pat['includes_relation'], Pat['chain'])
    function_call = pair(qualified_name, paren(opt_bool(kw('DISTINCT')) + comma_sep0(expr)))

    def k(w, r): return kw(w) >> const(r())
    quant = (k('ALL', Quant.ALL) | k('ANY', Quant.ANY) | k('NONE' , Quant.NONE)
             | k('SINGLE', Quant.SINGLE))
    existential = either(subquery, Pat['pattern'] + opt(where))

    return ( -kw('COUNT') + paren(star) >> const(Atom.COUNT())
           | -kw('EXISTS') + brace(existential) >> Atom.EXISTENTIAL
           | -kw('EXISTS') + paren(expr) >> Atom.EXISTS
           | -punct('$') + identifier >> Atom.PARAMETER
           | quant + paren(filter_expression) >> Atom.QUANTIFIER
           | case_expression >> Atom.CASE_EXPR
           | sqbr(pair(filter_expression, opt(-bar + expr))) >> Atom.LIST_COMP
           | sqbr(pattern_comprehension) >> Atom.PATTERN_COMP
           | function_call >> Atom.FUNCTION_CALL
           | literal >> Atom.LITERAL
           | variable >> Atom.VARIABLE
           | pattern_predicate >> Atom.PATTERN_PREDICATE
           | paren(expr) >> Atom.EXPRESSION
           )


def UpdatingP(expr):
    Pat = PatternP(expr)

    node_labels = -colon + sep_by1(colon, identifier)
    action = kw('MATCH') >> const(True) | kw('CREATE') >> const(False)

    def updating_clause(atom):
        U = UpdatingClause[str,Expr]
        property_expr = atom + property_lookup
        remove_item = either(variable + node_labels, property_expr)
        def op_expr(op): return -punct(op) + expr

        S = U.SetItem
        set_item = ( pair(property_expr, op_expr('=')) >> S.SET_PROPERTY
                   | variable + op_expr('=')      >> S.SET_VARIABLE
                   | variable + op_expr('+=')     >> S.INCREMENT
                   | variable + node_labels       >> S.LABEL
                   )
        set = -kw('SET') + comma_sep(set_item)
        merge_action = (-kw('ON') + action) + set

        return ( -kw('REMOVE') + comma_sep(remove_item) >> U.REMOVE
               | -kw('CREATE') + Pat['pattern'] >> U.CREATE
               | -kw('MERGE') + pair(opt_var + Pat['chain'], many(merge_action)) >> U.MERGE
               | opt_bool(kw('DETACH')) + -kw('DELETE') + comma_sep(expr) >> U.DELETE
               | set >> U.SET
               )

    return {'updating_clause': updating_clause}

def Top(expr):
    where = -kw('WHERE') + expr
    Tp = Types[Expr]

    def projection_body():
        projection_item = expr + opt(-kw('AS') + variable)
        projection_items = \
        ( (star >> const(True)) + (-punct(',') + comma_sep(projection_item))
        | star >> const((True, []))
        | pure(False) + comma_sep(projection_item)
        )
        sort_order = ( (kw('ASCENDING') | kw('ASC')) >> const(False)
                     | (kw('DESCENDING') | kw('DESC')) >> const(True)
                     )
        sort_item = expr + opt(sort_order)
        order = -kw('ORDER') + -kw('BY') + comma_sep(sort_item)
        limit = -kw('LIMIT') + expr
        skip = -kw('SKIP') + expr

        def proj(a,b,c,d,e) -> Tp.ProjectionBody:
            return {'distinct':a, 'projection_items':b, 'order':c, 'skip':d, 'limit':e}
        return (opt_bool(kw('DISTINCT')) + projection_items + opt(order) + opt(skip) + opt(limit)
                >> splice(proj))

    def procedure_call(wrap_args, wrap_yields):
        yield_items = comma_sep(opt(identifier + -kw('AS')) + variable) + opt(where)
        return pair(pair(-kw('CALL') + qualified_name,
                         wrap_args(paren(comma_sep0(expr)))),
                    opt(-kw('YIELD') + wrap_yields(yield_items)))

    def reading_clause():
        RC = Tp.ReadingClause
        match_clause = PatternP(expr)['pattern'] + opt(where)
        return ( opt_bool(kw('OPTIONAL')) + -kw('MATCH') + match_clause >> RC.MATCH_
               | -kw('UNWIND') + expr + -kw('AS') + variable >> RC.UNWIND
               | procedure_call(identity, identity) >> RC.IN_QUERY_CALL
               )

    standalone_call = procedure_call(opt, bind(opt_or, star))
    with_clause = -kw('WITH') + projection_body() + opt(where)

    def union(p):
        union_tail = ( pure(True) + oneplus(-kw('UNION') + -kw('ALL') + p)
                     | pure(False) + oneplus(-kw('UNION') + p)
                     | pure((False, []))
                     )
        def mk_union(head, union_tail):
            union_all, tail = union_tail
            return (union_all, [head, *tail])
        return p + union_tail >> splice(mk_union)

    def exists_query():
        def reading_query(read_q):
            RQ = Existential[Expr]
            Succeed = pure(RQ.SUCCEED())
            return ( reading_clause() + (read_q | Succeed) >> RQ.READ
                   | pair(with_clause, read_q | Succeed) >> RQ.WITH
                   | -(kw('RETURN') + projection_body()) + Succeed
                   )
        return union(fix(reading_query))

    atom = AtomP(expr, exists_query())

    def regular_query():
        Q =  Query[T,Expr]
        updating_clause = UpdatingP(expr)['updating_clause'](atom)
        def updating_query(read_q, upd_q):
            return ( -kw("RETURN") + projection_body() >> Q.RETURN
                   | updating_clause + upd_q >> Q.UPD
                   | pair(with_clause, read_q) >> Q.WITH
                   | pure(Q.STOP())
                   )

        def reading_query(read_q):
            upd_q = fix(bind(updating_query, read_q))
            return ( -kw("RETURN") + projection_body() >> Q.RETURN
                   | updating_clause + upd_q >> Q.UPD
                   | reading_clause() + read_q >> Q.READ
                   | pair(with_clause, read_q) >> Q.WITH
                   )

        return union(fix(reading_query))

    return {'projection_body': projection_body(),
            'regular_query':   regular_query(),
            'atom':            atom,
            'standalone_call': standalone_call}


def expression(atom, expr):
    def prefix_op(n):
        match n:
            case 7: return kw('NOT')
            case 1: return punct('+') | punct('-')
            case _: return fail('NO-PRE-OP')

    def binary_op(n):
        match n:
            case 10: return kw('OR')
            case 9: return kw('XOR')
            case 8: return kw('AND')
            case 6: return choices(map(punct, [ '<>', '<=', '>=', '=~', '=', '<', '>' ]))
            case 5: return (kw('STARTS') + kw('WITH') | kw('ENDS') + kw('WITH')
                            | kw('CONTAINS') | kw('IN'))
            case 4: return punct('+') | punct('-')
            case 3: return choices(map(punct, [ '*', '/', '%' ]))
            case 2: return punct('^')
            case _: return fail('NO-BIN-OP')

    def postfix_op(n):
        match n:
            case 5: return kw('IS') + kw('NULL') | kw('IS') + kw('NOT') + kw('NULL')
            case _: return fail('NO-POST-OP')

    def expr_(n):
        match n:
            case 0:
                range = either(opt(expr) + (-punct('..') + opt(expr)), expr)
                def apply_op(e,x):
                    return x.match(LEFT=compose(Expr.LIST_REF, pair_with(e)),
                                   RIGHT=compose(Expr.PROP_REF, pair_with(e)))

                return (atom + many(either(sqbr(range), property_lookup)) >>
                        splice(lambda a, ops: reduce(apply_op, ops, Expr.ATOM(a))))
            case 1:
                return expr_(0) + label_match >> Expr.LABEL_IS | expr_(0)
            case n:
                em = expr_(n - 1)
                def apply_op(e1,x):
                    return x.match(LEFT=splice(lambda o, e2: Expr.BINOP(o, e1, e2)),
                                   RIGHT=lambda o: Expr.POSTOP(o, e1))
                return fix(lambda expr:
                    ( consumed(prefix_op(n - 1)) + expr >> splice(Expr.PREOP)
                    | (em + many(either(consumed(binary_op(n - 1)) + em,
                                        consumed(postfix_op(n - 1))))
                        >> splice(lambda e, ops: reduce(apply_op, ops, e)))
                    ))
    return expr_(11)

top, expr = fix_aux(lambda e: forkr(lambda t: expression(t['atom'], e))(Top(e)))
statement = either(top['regular_query'], top['standalone_call'])
