from enum import Enum
from typing import Annotated, Literal, Self

from devtools import pformat
from pydantic import BaseModel, Field, model_validator

from utils.agent.base import (
    EndResult,
    InputBase,
    create_partial_graph_state,
)
from utils.imandra.imandrax.proto_models.simple_api import (
    DecomposeRes,
    InstanceRes,
    VerifyRes,
)


class RawVerifyReq(BaseModel):
    """
    A formal specification of a property / logical statement, clause, predicate,
    or condition to verify about functions in the source code.

    Each verification pairs a natural language description with a corresponding logical
    statement that will be later used in tasks related to property-based testing and
    formal verification.
    The description is human-readable, while the logical statement is more precise,
    mathematically formal.
    """

    src_func_names: list[str] = Field(
        ...,
        description="names of the functions (including class methods) involved "
        "in the verification",
    )
    iml_func_names: list[str] = Field(
        ..., description="names of the corresponding functions in IML"
    )
    description: str = Field(
        ...,
        description="Human-readable description of the property to verify. Should "
        "clearly explain what aspect of the function's behavior is being checked. "
        "Example: 'The function always returns a value greater than or equal to 10' or "
        "'The output array is always sorted in ascending order'",
    )
    logical_statement: str = Field(
        ...,
        description="Logical statement expressing the property in a precise way. "
        "Can use plain English with logical terms like 'for all', 'there exists', "
        "'and', 'or', etc. Example: 'for all inputs x, f(x) is greater than or equal "
        "to 10' or 'for all indices i from 0 to n-2, array[i] is less than or equal "
        "to array[i+1]'",
    )

    def __repr__(self):
        return pformat(self)


class RawDecomposeReq(BaseModel):
    """
    A function to decompose in source code and its corresponding function in IML.
    """

    description: str = Field(
        description="Human-readable description of the function to decompose"
    )
    src_func_name: str = Field(
        description="name of function to decompose in source code"
    )
    iml_func_name: str = Field(description="name of function to decompose in IML")

    def __repr__(self):
        return pformat(self)


class PartialVerifyReq(BaseModel):
    predicate: str = Field(
        description="IML code representing some logical statement using lambda"
        "functions. Eg. `fun x -> x >= 10`, `fun x -> f x <> 98`. Backticks should"
        "be omitted."
    )
    kind: Literal["verify", "instance"] = Field(
        description="""Kind of reasoning request. 
        - `verify` checks that the given predicate is always true (universal)
        - `instance` finds an example where the predicate is true (existential)
        """
    )

    def to_iml(self) -> str:
        return f"${self.kind} ({self.predicate})"

    def to_negation(self) -> Self:
        predicate = self.predicate
        arrow_idx = predicate.index("->")
        dom = predicate[:arrow_idx]
        cod = predicate[arrow_idx + 2 :]
        neg_cod = f"not ({cod.strip()})"
        neg_predicate = f"{dom}-> {neg_cod}"
        if self.kind == "verify":
            kind = "instance"
        else:
            kind = "verify"
        return PartialVerifyReq(predicate=neg_predicate, kind=kind)


class PartialDecomposeReq(BaseModel):
    src_func_name: str | None = None
    iml_func_name: str

    @classmethod
    def from_raw(cls, raw: RawDecomposeReq):
        return cls(src_func_name=raw.src_func_name, iml_func_name=raw.iml_func_name)

    def to_iml(self) -> str:
        """
        `decompose` keyword is not yet supported in ImandraX
        For now, it could be something like:
        `let target_fn .. = .. [@@decompose ~assuming:[%id asm] ~basis:[[%id foo]] ..]`
        """
        return f"(* decompose {self.iml_func_name} *)"


class RawReasonReq[Req](BaseModel):
    content: Req
    source: Literal["comments", "main_function"] = Field(
        ..., description="The way the request is extracted"
    )


class ReasonReq[Req, Res](BaseModel):
    iml_query: Req = Field(..., description="IML query")
    imx_res: Res | None = Field(..., description="Result from ImandraX client")
    extra: dict | None = Field(..., description="Extra information")

    @model_validator(mode="after")
    def validate_res(self) -> Self:
        match (self.iml_query, self.imx_res):
            case (PartialVerifyReq(), VerifyRes()):
                return self
            case (PartialVerifyReq(), InstanceRes()):
                return self
            case (PartialDecomposeReq(), DecomposeRes()):
                return self
            case (_, None):
                return self
            case _:
                raise ValueError(
                    f"Invalid combination of iml_query and imx_res: "
                    f"{self.iml_query} {self.imx_res}"
                )

    def __repr__(self):
        return pformat(self)


class ReasonerActionType(str, Enum):
    SYNC_SRC = "sync_src"
    SYNC_IML = "sync_iml"
    EXTRACT_VERIFY_REQS = "extract_verify_reqs"
    GEN_IML_VERIFY_QUERIES = "gen_iml_verify_queries"
    EXTRACT_DECOMPOSE_REQS = "extract_decompose_reqs"
    RUN_VERIFY = "run_verify"
    RUN_DECOMPOSE = "run_decompose"
    EXTRACT_ALL = "extract_all"
    # artifacts?


class ReasonerAction(BaseModel, use_enum_values=True):
    type: ReasonerActionType
    params: dict | None = Field(None, description="Parameters for the action")

    @model_validator(mode="after")
    def validate_params(self) -> Self:
        """Validate that params are only required for SYNC_SRC and SYNC_IML actions"""
        match self.type:
            case ReasonerActionType.SYNC_SRC:
                if not self.params or "new_iml_code" not in self.params:
                    raise ValueError(f"{self.type} requires params with new_iml_code")
            case ReasonerActionType.SYNC_IML:
                if not self.params or "new_src_code" not in self.params:
                    raise ValueError(f"{self.type} requires params with new_src_code")
            case ReasonerActionType.EXTRACT_DECOMPOSE_REQS:
                pass
            case _:
                if self.params is not None:
                    raise ValueError(f"{self.type} should not have params")
        return self


class InputState(InputBase):
    src_code: str = Field(..., description="Code in source language")
    iml_code: str = Field(..., description="Model in IML")
    decompose_raw: list[RawReasonReq[RawDecomposeReq]] = Field(
        [], description="List of raw decomposition requests"
    )
    decompose_req: list[ReasonReq[PartialDecomposeReq, DecomposeRes]] = Field(
        [], description="List of ImandraX decomposition results and extra information"
    )
    verify_raw: list[RawReasonReq[RawVerifyReq]] = Field(
        [], description="List of raw verify requests for reasoning"
    )
    verify_req: list[ReasonReq[PartialVerifyReq, VerifyRes]] = Field(
        [], description="List of ImandraX verify results and extra information"
    )
    action: ReasonerAction = Field(..., description="Action to perform")
    counter: int | None = Field(None, description="An intermediate counter")

    @property
    def iml_queries(self, verify_only: bool = True) -> list[str]:
        reason_reqs = self.decompose_req + self.verify_req
        return [
            reason_req.iml_query.to_iml()
            for reason_req in reason_reqs
            if verify_only and isinstance(reason_req.iml_query, PartialVerifyReq)
        ]


def merge_end_result(er1: EndResult, er2: EndResult) -> EndResult:
    info = ""
    if er1.info:
        info += f"{er1.info}"
    if er2.info:
        info += f"\n\n{er2.info}"

    if er1.result == "success" and er2.result == "success":
        return EndResult(result="success", info=info)
    else:
        return EndResult(result="failure", info=info)


class GraphState(InputState):
    end_result: Annotated[EndResult, merge_end_result] = Field(
        description="End result of the whole task."
    )

    def render(self) -> str:
        s = ""
        s += "### Raw Reasoning Requests\n\n"
        raw_reason_reqs = self.decompose_raw + self.verify_raw
        for raw_reason_req in raw_reason_reqs:
            s += f"- {raw_reason_req.content}\n"
        s += "\n"
        s += "### Reasoning Requests\n\n"
        for iml_query in self.iml_queries:
            s += f"- {iml_query}\n"
        return s


PartialOutput = create_partial_graph_state(InputState, GraphState)


class GraphConfig(BaseModel):
    pass
