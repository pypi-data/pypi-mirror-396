# fmt: off
# ruff: noqa: E702, N806, I001, E501
from .cypher_ast import Atom, Either, Existential, Expr, Option, Pattern, Query, Types
from .util import (bind, compose as c, const, delay, fboth, ffst, fkey, flip, # fmt: skip
                   foldr, fsnd, fst, identity, map, prod, snd, splice, uniq)  # fmt: skip

id = identity

def cons(x): return lambda xs: [x, *xs]
def fold_right(f): return lambda xs: lambda s: foldr(lambda x, y: f(x)(y), xs, s)

def fold_props(f): return lambda x: fold_right(f)(x['properties'])

def fold_statement(label_is,  prop_ref,  binding, node_prop, frel):
    def fold_pair(f,g): return splice(lambda x, y: c(f(x), g(y)))
    @delay
    def fexpr_tuple(g, t): (_, x), xo = t; return c(opt_fex(xo), g(x))
    def fopt(f): return Option.map_or(identity, f)

    def fex(x):
        return x.match(
            ATOM=fat,
            BINOP=lambda _, x, y: c(fex(y), fex(x)),
            PREOP=lambda _, x: fex(x),
            POSTOP=lambda _, x: fex(x),
            LABEL_IS=c(label_is, ffst(fex)),
            PROP_REF=c(prop_ref, ffst(fex)),
            LIST_REF=c(fex, fst))

    opt_fex = fopt(fex)
    def fpair(xy): x, y = xy; return c(fex(y), fex(x))
    def fat(x):
        return x.match(
            COUNT=lambda: id,
            LITERAL=flit,
            EXPRESSION=fex,
            FUNCTION_CALL=c(fold_right(fex), snd, snd),
            QUANTIFIER=c(fexpr_tuple(fex), snd),
            PATTERN_PREDICATE=fchain,
            PATTERN_COMP=fold_pair(fexpr_tuple(fchain), fex),
            LIST_COMP=fold_pair(fexpr_tuple(fex), opt_fex),
            CASE_EXPR=fold_pair(opt_fex, fold_pair(fold_right(fpair), opt_fex)),
            EXISTENTIAL=Either.fold(fexst, fm),
            EXISTS=fex,
            VARIABLE=const(id),
            PARAMETER=const(id))

    def flit(x):
        return x.match(
            NULL=lambda: id,
            BOOL=const(id),
            INT= const(id),
            FLOAT= const(id),
            QUOTED= const(id),
            LIST=fold_right(fex),
            MAP=fold_right(c(binding, fsnd(fex))))

    def fchain(xy):
        x, y= xy
        fnd = fold_props(c(node_prop, fsnd(fex)))
        def farr(f): return lambda x: x.match(LEFT=f, RIGHT=f, BIDI=f)
        return c(fold_right(splice(lambda x, y: c(farr(c(frel(fex), fst))(x), fnd(y))))(y), fnd(x))

    fm = fold_pair(fold_right(c(fchain, snd)), opt_fex)
    def frd(x):
        return x.match(
            MATCH_=c(fm, snd),
            IN_QUERY_CALL=fold_pair(c(fold_right(fex), snd), fopt(c(opt_fex, snd))),
            UNWIND=c(fex, fst))

    def fproj(p):
        return c(fopt(fold_right(c(fex, fst)))(p['order']),
                 fold_right(c(fex, fst))(snd(p['projection_items'])))
    def fwith(pxo): p, xo = pxo; return c(opt_fex(xo), fproj(p))
    def fexst(x):
        def fold_query(x):
            return x.match(
                READ=fold_pair(frd, fold_query),
                WITH=fold_pair(fwith, fold_query),
                SUCCEED=lambda: id)
        return fold_right(fold_query)(snd(x))
    def freg(x):
        fpi = fold_right(c(fex, fst))
        def fupd(_): raise Exception("Unexpected update clause")
        def fold_query(x):
            return x.match(
                READ=fold_pair(frd, fold_query),
                UPD=fold_pair(fupd, fold_query),
                WITH=fold_pair(fwith, fold_query),
                RETURN=lambda x: fpi(snd(x['projection_items'])),
                STOP=lambda: id)
        return fold_right(fold_query)(snd(x))

    return Either.fold(freg, const(id))


@delay
def farrow(f, x):
    Arrow = Pattern.Arrow
    return x.match(
        LEFT =c(Arrow.LEFT, f),
        RIGHT=c(Arrow.RIGHT, f),
        BIDI =c(Arrow.BIDI, f))

def map_statement(fchain=id, fproj_items=id):
    Tp = Types[Expr]
    def fex(x):
        return x.match(
            ATOM=c(Expr.ATOM, fat),
            BINOP=lambda op, x, y: Expr.BINOP(op, fex(x), fex(y)),
            PREOP=lambda op, x: Expr.PREOP(op, fex(x)),
            POSTOP=lambda op, x: Expr.POSTOP(op, fex(x)),
            LABEL_IS=c(Expr.LABEL_IS, ffst(fex)),
            PROP_REF=c(Expr.PROP_REF, ffst(fex)),
            LIST_REF=c(Expr.LIST_REF, ffst(fex)))
    opt_fex = Option.map(fex)
    def fat(x):
        A = Atom
        return x.match(
            COUNT=lambda: A.COUNT,
            LITERAL=c(A.LITERAL, flit),
            EXPRESSION=c(A.EXPRESSION, fex),
            FUNCTION_CALL=c(A.FUNCTION_CALL, fsnd(fsnd(bind(map, fex)))),
            QUANTIFIER=c(A.QUANTIFIER, fsnd(prod(fsnd(fex), opt_fex))),
            PATTERN_PREDICATE=c(A.PATTERN_PREDICATE, fchain),
            PATTERN_COMP=c(A.PATTERN_COMP, prod(prod(fsnd(fchain), opt_fex), fex)),
            LIST_COMP=c(A.LIST_COMP, prod(prod(fsnd(fex), opt_fex), opt_fex)),
            CASE_EXPR=c(A.CASE_EXPR, prod(opt_fex, prod(bind(map, fboth(fex)), opt_fex))),
            EXISTENTIAL=c(A.EXISTENTIAL, Either.map(fexst, fm)),
            EXISTS=c(A.EXISTS, fex),
            VARIABLE=A.VARIABLE,
            PARAMETER=A.PARAMETER)
    def flit(x):
        Literal = Atom.Literal
        return x.match(
            NULL=lambda: Literal.NULL(),
            BOOL=Literal.BOOL,
            INT=Literal.INT,
            FLOAT=Literal.FLOAT,
            QUOTED=Literal.QUOTED,
            LIST=c(Literal.LIST, bind(map, fex)),
            MAP=c(Literal.MAP, bind(map, fsnd(fex))))
    fm = prod(bind(map, fsnd(fchain)), opt_fex)
    def frd(x):
        RC = Tp.ReadingClause
        return x.match(
            MATCH_=c(RC.MATCH_, fsnd(fm)),
            UNWIND=c(RC.UNWIND, ffst(fex)),
            IN_QUERY_CALL=RC.IN_QUERY_CALL)
    def fexst(x):
        def map_q(x):
            return x.match(
                READ=c(Existential.READ, prod(frd, map_q)),
                WITH=c(Existential.WITH, prod(fwith, map_q)),
                SUCCEED=lambda: Existential.SUCCEED)
        return fsnd(bind(map, map_q))(x)
    fwith = fsnd(opt_fex)
    def freg(x):
        fpi = fsnd(c(fproj_items, bind(map, ffst(fex))))
        def fupd(_): raise Exception("Unexpected update clause")
        def map_query(x):
            return x.match(
                READ=c(Query.READ, prod(frd, map_query)),
                UPD=c(Query.UPD, prod(fupd, map_query)),
                WITH=c(Query.WITH, prod(fwith, map_query)),
                RETURN=c(Query.RETURN, fkey('projection_items', fpi)),
                STOP=lambda: Query.STOP())
        return fsnd(bind(map, map_query))(x)
    return Either.map(freg, id)

split_unions = Either.fold(c(bind(map, lambda q: Either.LEFT((False, [q]))), snd), const([]))

def rm_key(kk): return lambda d: [(k,v) for k, v in d if k != kk]
def map_props(f): return fkey('properties', f)


scoped_edges = [ "CASE", "GROUP_FIELD", "GROUP_SUBGROUP", "MESSAGE_FIELD", "MESSAGE_SUBGROUP" ]
def is_scoped(f):
    def is_scoped(f):
        return f.match(
            ATOM=lambda a: a in scoped_edges,
            AND=lambda f, g: is_scoped(f) or is_scoped(g),
            OR=lambda f, g: is_scoped(f) or is_scoped(g),
            NOT=const(False))
    return Option.map_or(False, is_scoped)(f)

def scoping_analysis(statement):
    noop = const(id)
    @splice
    def fprop_exp(p, fx): return c(ffst(lambda x: x or p == "scope"), fx)
    def fe(e): return fsnd(lambda b: b or is_scoped(e['formula']))
    def frel(fex): return lambda r: c(fold_props(c(fprop_exp, fsnd(fex)))(r), fe(r))
    folder = fold_statement(label_is=noop, prop_ref=flip(fprop_exp),
                            binding=fprop_exp, node_prop=fprop_exp, frel=frel)
    return folder(statement)((False, False))


def set_scope_and_graph_id(scope, graph_id, fproj_items=uniq):
    def binding(k, v): return k, Expr.ATOM(Atom.LITERAL(Atom.Literal.QUOTED(v)))

    rm_graph_id = rm_key("graph_id")
    add_graph_id = cons(binding("graph_id", graph_id))
    def apply_scope(sc): return c(cons(binding("scope", sc)), rm_key("scope"))

    def enscope(ty):
        scope1 = scope if is_scoped(ty) else Option.NONE()
        return Option.map_or(id, apply_scope)(scope1)

    def fchain():
        def frel(r): return map_props(enscope(r['formula']))(r)
        fn1 = map_props(c(add_graph_id, rm_graph_id))
        fnx = map_props(rm_graph_id)
        return prod(fn1, bind(map, prod(farrow(ffst(frel)), fnx)))

    return map_statement(fchain=fchain(), fproj_items=fproj_items)
