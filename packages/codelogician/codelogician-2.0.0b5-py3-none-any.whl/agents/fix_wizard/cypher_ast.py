# fmt: off
# ruff: noqa: UP031, E741, E501, UP046
from typing import Generic, Self, TypedDict, TypeVar

from adt import Case, adt

from .util import compose as c, identity, maybe_else

A = TypeVar('A')
E = TypeVar('E')
T = TypeVar('T')
L = TypeVar('L')
R = TypeVar('R')

def adt_repr(x):
    return '%s%s' % (x._key.name, maybe_else('', lambda x: '(%s)' % repr(x), x._value))

@adt
class Id(Generic[T]):
    ID: Case[T]
    def get(self): return self.match(id=identity)

@adt
class Option(Generic[T]):
    NONE: Case
    SOME: Case[T]

    @staticmethod
    def map_or(d, f): return lambda x: x.match(none=lambda: d, some=f)
    @staticmethod
    def map(f): return Option.map_or(Option.NONE(), c(Option.SOME, f))
    @staticmethod
    def of_list(l): return Option.SOME(l[0]) if l else Option.NONE()
    def to_list(self): return self.map_or([], lambda x: [x])
    def __repr__(self): return adt_repr(self)

@adt
class Either(Generic[L,R]):
    LEFT: Case[L]
    RIGHT: Case[R]
    @staticmethod
    def fold(l, r): return lambda x: x.match(left=l, right=r)
    @staticmethod
    def map(l, r): return lambda x: x.match(left=c(Either.LEFT, l), right=c(Either.RIGHT,r))
    def __repr__(self): return adt_repr(self)

@adt
class Formula(Generic[T]):
    ATOM: Case[T]
    NOT: Case[Self]
    AND: Case[Self,Self]
    OR: Case[Self,Self]
    def __repr__(self: Option[T]): return adt_repr(self)


Identifier = str
Variable = Identifier
QualifiedName = tuple[Option[Identifier], Identifier]

@adt
class ExprF(Generic[A]):
    ATOM: Case[A]
    PREOP: Case[str,Self]
    POSTOP: Case[str,Self]
    BINOP: Case[str,Self,Self]
    LABEL_IS: Case[tuple[Self,Formula[str]]]
    PROP_REF: Case[tuple[Self,str]]
    LIST_REF: Case[tuple[Self,Either[tuple[Option[Self],Option[Self]], Self]]]
    def __repr__(self: Option[T]): return adt_repr(self)

class Pattern(Generic[E]):
    @adt
    class ArrowF(Generic[T]):
        LEFT: Case[T]
        RIGHT: Case[T]
        BIDI: Case[T]
        def __repr__(self): return '%s(%r)' % (self._key.name,self._value)

    class Element(TypedDict):
        variable: Option[Variable]
        formula: Option[Formula[str]]
        properties: list[tuple[Identifier, E]]

    Range = tuple[Option[int], Option[Option[int]]]
    Relationship = tuple[Element, Option[Range]]
    Arrow = ArrowF[Relationship]
    Link = tuple[Arrow, Element]
    Chain = tuple[Element, list[Link]]
    Pattern = list[tuple[Option[Variable],Chain]]

    empty = (Option.NONE(), Option.NONE(), [])

@adt
class AtomF(Generic[T,E]):
    Pattern = Pattern[E]

    @adt
    class Quant:
        ALL: Case
        ANY: Case
        NONE: Case
        SINGLE: Case
        def __repr__(self: Option[T]): return adt_repr(self)

    @adt
    class Literal:
        Map = list[tuple[Identifier, E]]

        NULL: Case
        BOOL: Case[bool]
        FLOAT: Case[float]
        INT: Case[int]
        QUOTED: Case[str]
        LIST: Case[list]
        MAP: Case[Map]
        def __repr__(self): return adt_repr(self)

    COUNT: Case
    LITERAL: Case[Literal]
    PARAMETER: Case[str]
    VARIABLE: Case[str]
    EXPRESSION: Case[E]
    FUNCTION_CALL: Case[tuple[QualifiedName, tuple[bool, list[E]]]]
    QUANTIFIER: Case[tuple[Quant,tuple[tuple[str,E],Option[E]]]]
    CASE_EXPR: Case[tuple[Option[E], tuple[list[tuple[E,E]], Option[E]]]]
    LIST_COMP: Case[tuple[tuple[tuple[str,E], Option[E]], Option[E]]]
    PATTERN_COMP: Case[tuple[tuple[tuple[str, E], Option[E]], Option[E]]]
    PATTERN_PREDICATE: Case[Pattern.Chain]
    EXISTENTIAL: Case[Either[T, tuple[Pattern.Pattern, Option[E]]]]
    EXISTS: Case[E]

    def __repr__(self): return adt_repr(self)

@adt
class UpdatingClause(Generic[T,E]):
    A = AtomF[T, E]

    @adt
    class SetItem:
        SET_PROPERTY: Case[tuple[tuple[A, str], E]]
        SET_VARIABLE: Case[tuple[Variable, E]]
        INCREMENT: Case[tuple[Variable, E]]
        LABEL: Case[tuple[Variable, list[str]]]
        def __repr__(self): return adt_repr(self)

    RemoveItem = Either[list[tuple[Variable,str]], tuple[A,str]]

    SET : Case[list[SetItem]]
    REMOVE : Case[list[RemoveItem]]
    CREATE : Case[Pattern.Pattern]
    MERGE : Case[tuple[tuple[Option[Variable], Pattern.Chain], list[tuple[bool, list[SetItem]]]]]
    DELETE : Case[tuple[bool, list[E]]]
    def __repr__(self): return adt_repr(self)

class Types(Generic[E]):
    class ProjectionBody(TypedDict):
        distinct: bool
        projection_items: tuple[bool, list[tuple[E, Option[Variable]]]]
        order: Option[list[tuple[E, Option[bool]]]]
        skip: Option[E]
        limit: Option[E]

    @adt
    class ReadingClause:
        YieldItems = tuple[list[tuple[Option[Variable], Variable]], Option[E]]

        MATCH_: Case[tuple[bool, tuple[Pattern.Pattern, Option[E]]]]
        IN_QUERY_CALL: Case[tuple[tuple[QualifiedName, list[E]], Option[YieldItems]]]
        UNWIND: Case[tuple[T,Variable]]
        def __repr__(self): return adt_repr(self)

@adt
class Existential(Generic[E]):
    Tp = Types[E]
    SUCCEED: Case
    READ: Case[tuple[Tp.ReadingClause, Self]]
    WITH: Case[tuple[tuple[Tp.ProjectionBody, Option[E]], Self]]
    def __repr__(self): return adt_repr(self)

@adt
class Query(Generic[T,E]):
    Tp = Types[E]
    STOP: Case
    RETURN: Case[Tp.ProjectionBody]
    UPD:  Case[tuple[UpdatingClause[T,E], Self]]
    READ: Case[tuple[Tp.ReadingClause, Self]]
    WITH: Case[tuple[tuple[Tp.ProjectionBody, Option[E]], Self]]
    def __repr__(self): return adt_repr(self)

Expr = ExprF[AtomF[Existential['Expr'],'Expr']]
Atom = AtomF[Existential[Expr],Expr]
Pattern = Pattern[Expr]
