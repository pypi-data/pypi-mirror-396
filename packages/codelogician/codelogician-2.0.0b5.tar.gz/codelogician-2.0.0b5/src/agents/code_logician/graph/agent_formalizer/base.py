"""
Core data types
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import (
    Any,
    Literal,
    ParamSpec,
    TypedDict,
    TypeGuard,
    assert_never,
    get_args,
)

from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel

from ...base import FormalizationStateUpdate
from ...command import AgentFormalizerCommand
from ...fstate_transition import (
    AsyncFormalizationStateTransition,
    FormalizationStateTransition,
)

type ToolName = Literal["gen_model", "search_iml_api"]

type FTransName = Literal[
    "check_formalization",
    "gen_formalization_data",
    "gen_program_refactor",
    "gather_formalization_failure_info",
]

type HITLName = Literal["check_formalization_hitl", "formalization_action_hitl"]


P = ParamSpec("P")


@dataclass(slots=True, frozen=True)
class ToolDefinition:
    """Something that can be executed and results in transition of fstate.

    Not necessarily a LLM tool.
    """

    name: str
    description: str | None
    args_schema: type[BaseModel] | None
    tool_func: FormalizationStateTransition | AsyncFormalizationStateTransition

    @staticmethod
    def create(
        tool_func: FormalizationStateTransition | AsyncFormalizationStateTransition,
        name: str | None = None,
        description: str | None = None,
        args_schema: type[BaseModel] | None = None,
    ) -> ToolDefinition:
        if name is None:
            name = tool_func.__name__

        if description:
            description_ = description
        elif args_schema:
            description_ = args_schema.__doc__
        elif tool_func.__doc__:
            description_ = tool_func.__doc__
        assert description_ is not None
        return ToolDefinition(
            name=name,
            description=description_,
            args_schema=args_schema,
            tool_func=tool_func,
        )

    def to_langchain_tool(self) -> BaseTool:
        return tool(
            self.tool_func,
            description=self.description,
            args_schema=self.args_schema,
        )


@dataclass(slots=True, frozen=True)
class ToolCall:
    """A tool invocation with name and arguments."""

    tool_name: ToolName
    arguments: dict[str, Any]


def validate_tool_name(tool_name: str) -> TypeGuard[ToolName]:
    """Type guard to check if string is valid ToolName."""
    return tool_name in get_args(ToolName.__value__)


def ai_message_to_tool_calls(msg: AIMessage) -> list[ToolCall]:
    """Extract ToolCall objects from AIMessage tool_calls."""
    res = []
    for tool_call in msg.tool_calls:
        tool_name = tool_call["name"]
        assert validate_tool_name(tool_name)
        res.append(
            ToolCall(
                tool_name=tool_name,
                arguments=tool_call["args"],
            )
        )
    return res


@dataclass(slots=True, frozen=True)
class ToolResult:
    """Result of tool execution with state update or error."""

    success: bool
    fupdate: FormalizationStateUpdate | None
    error: str | None = None


class StepType(Enum):
    """Type of MDP step execution."""

    GEN_MODEL = "gen_model"
    LLM_INVOKE = "llm_invoke"
    FSTATE_TRANSITION = "fstate_transition"
    HITL_INTERRUPTED = "hitl_interrupted"
    HITL = "hitl"


# =====
# Agent in
# =====

type MessageParam = Any  # Placeholder for future message algebra
type ModelSpec = Any  # Placeholder for future model algebra


@dataclass(slots=True, frozen=True)
class LLMAgentParam:
    """Parameters for LLM agent tool selection step."""

    tool_names: list[ToolName]
    message_param: MessageParam = None
    model_spec: ModelSpec = None


@dataclass(slots=True, frozen=True)
class FTransParam:
    """Parameters for direct formalization state transition."""

    name: FTransName


@dataclass(slots=True, frozen=True)
class GenModelParam:
    """Parameters for IML model generation step."""

    pass


@dataclass(slots=True, frozen=True)
class HITLParam:
    """Parameters for human-in-the-loop interaction step."""

    data: Any

    def get_name(self) -> HITLName:
        match self.data:
            case {"missing_func": _, "src_code": _}:
                return "check_formalization_hitl"
            case {"iml_code": _, "err_str": _}:
                return "formalization_action_hitl"
            case _ as unreachable:
                assert_never(unreachable)  # ty: ignore[type-assertion-failure]


type AgentParam = LLMAgentParam | FTransParam | GenModelParam

type StepParam = AgentParam | HITLParam


def repr_step_param(step_param: StepParam) -> str:
    """Human-readable representation of step parameter."""
    match step_param:
        case FTransParam(name=name):
            return f"FTransParam(name={name})"
        case GenModelParam():
            return "GenModelParam()"
        case LLMAgentParam(tool_names=tool_names):
            return f"LLMAgentParam(tool_names={tool_names})"
        case HITLParam(data=data):
            return f"HITLParam(data={data})"
        case _ as unreachable:
            assert_never(unreachable)  # ty: ignore[type-assertion-failure]


# =====
# Agent out
# =====


@dataclass(slots=True, frozen=True)
class LLMInvokeResult:
    """Result of LLM tool invocation with success status per tool."""

    tool_call_summary: list[tuple[ToolName, bool]]


@dataclass(slots=True, frozen=True)
class FStateTransitionResult:
    """Result marker for formalization state transition completion."""

    pass


@dataclass(slots=True, frozen=True)
class GenModelResult:
    """Result marker for model generation completion."""

    pass


@dataclass(slots=True, frozen=True)
class HITLResult:
    """Result of HITL interaction with human response data."""

    data: Any


type StepResult = LLMInvokeResult | FStateTransitionResult | GenModelResult | HITLResult


class StepRecord(BaseModel):
    """Complete record of a step in the MDP"""

    step_type: StepType
    step_param: StepParam
    result: StepResult
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Disable validation as FStateTransitionResult, GenModelResult, HITLResult
    # are both empty and pydantic serialization cannot discriminate between them
    # @model_validator(mode="after")
    # def check_step_type(self) -> Self:
    #     es = self.validate()
    #     if es := list(es):
    #         raise ExceptionGroup("Validation failed", es)
    #     return self

    def validate(self) -> Iterator[AssertionError]:
        match self.step_type:
            case StepType.LLM_INVOKE:
                if not isinstance(self.result, LLMInvokeResult):
                    yield AssertionError(
                        f"result must be LLMInvokeResult, "
                        f"got {type(self.result).__name__}"
                    )
            case StepType.FSTATE_TRANSITION:
                if not isinstance(self.result, FStateTransitionResult):
                    yield AssertionError(
                        f"result must be FStateTransitionResult, "
                        f"got {type(self.result).__name__}"
                    )
            case StepType.GEN_MODEL:
                if not isinstance(self.result, GenModelResult):
                    yield AssertionError(
                        f"result must be GenModelResult, "
                        f"got {type(self.result).__name__}"
                    )
            case StepType.HITL:
                if not isinstance(self.result, HITLResult):
                    yield AssertionError(
                        f"result must be HITLResult, got {type(self.result).__name__}"
                    )
            case StepType.HITL_INTERRUPTED:
                if not isinstance(self.result, HITLResult):
                    yield AssertionError(
                        f"result must be HITLResult, got {type(self.result).__name__}"
                    )
                elif self.result.data != {}:
                    yield AssertionError(
                        "result.data for StepType.HITL_INTERRUPTED must be {}, "
                        f"got {self.result.data}"
                    )
            case _ as unreachable:
                assert_never(unreachable)  # ty: ignore[type-assertion-failure]


class MDPConfig(TypedDict):
    max_step: int
    no_check_formalization_hitl: bool
    no_refactor: bool
    no_gen_model_hitl: bool
    max_gen_model_without_hitl: int
    max_gen_model: int


def mk_default_mdp_config() -> MDPConfig:
    """Create default MDP configuration with standard limits."""
    return MDPConfig(
        max_step=50,
        no_check_formalization_hitl=True,
        no_refactor=False,
        no_gen_model_hitl=True,
        max_gen_model_without_hitl=3,  # won't take effect as we no_gen_model_hitl=True
        max_gen_model=5,
    )


def mk_mdp_config(command: AgentFormalizerCommand) -> MDPConfig:
    """Create MDP configuration from agent_formalizer command parameters."""
    default_max_step = 50

    no_check_formalization_hitl = command.no_check_formalization_hitl
    no_refactor = command.no_refactor
    no_gen_model_hitl = command.no_gen_model_hitl
    max_gen_model_without_hitl = command.max_tries_wo_hitl
    max_gen_model = command.max_tries

    return MDPConfig(
        max_step=default_max_step,
        no_check_formalization_hitl=no_check_formalization_hitl,
        no_refactor=no_refactor,
        no_gen_model_hitl=no_gen_model_hitl,
        max_gen_model_without_hitl=max_gen_model_without_hitl,
        max_gen_model=max_gen_model,
    )
