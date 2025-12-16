from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class IplList(BaseModel):
    type_ctor: Literal["list"]
    base_type: IplType


IplType = Literal["int"] | Literal["string"] | Literal["bool"] | IplList


class LiteralVal(BaseModel):
    val: int | str | bool = Field(description="Literal value")


class ListLiteral(BaseModel):
    elements: list[Expr] = Field(description="Contents of the list literal")


class Identifier(BaseModel):
    id: str = Field(description="Identifier name")


class FunctionApp(BaseModel):
    name: str = Field(description="Identifier of the function being applied")
    args: list[FnArg] = Field(description="Arguments of the function application")


class LambdaExpr(BaseModel):
    param: str = Field(description="Parameter of the lambda expression")
    body: Expr = Field(description="Body of the lambda expression")


class BinOp(BaseModel):
    left: Expr = Field(description="Left operand")
    op: str = Field(description="Operator symbol")
    right: Expr = Field(description="Right operand")


class Subscription(BaseModel):
    operand: str = Field(
        description="The identifier being indexed by the subscript operator"
    )
    subscript: Expr = Field(
        description="The subscript being used to index into the operand"
    )


class UnaryNot(BaseModel):
    operand: Expr = Field(description="Expression being negated")


class IfThenElse(BaseModel):
    guard: Expr = Field(description="Boolean guard of the if-then-else")
    then_branch: Expr = Field(description="Expression to evaluate if the guard is true")
    else_branch: Expr = Field(
        description="Expression to evaluate if the guard is false"
    )


Expr = (
    LiteralVal
    | ListLiteral
    | Identifier
    | FunctionApp
    | BinOp
    | IfThenElse
    | Subscription
    | UnaryNot
)
FnArg = Expr | LambdaExpr


class LetStmt(BaseModel):
    identifier: str = Field(description="Variable being bound by the let statement")
    ipl_type: IplType = Field(description="Type of the variable being bound")
    expr: Expr = Field(
        description="Expression which value is being assigned to the bound variable"
    )


class AssignmentStmt(BaseModel):
    identifier: str = Field(description="Variable to be assigned to")
    expr: Expr = Field(
        description="Expression which value is being assigned to the variable"
    )


class ReturnStmt(BaseModel):
    expr: Expr = Field(description="Expression which value is being returned")


Stmt = LetStmt | AssignmentStmt | ReturnStmt
