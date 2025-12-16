import abc
import typing
import uuid
from collections.abc import Callable, Sequence
from inspect import isfunction
from typing import Annotated, Any, Literal

from devtools import pformat
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field, create_model
from pydantic.fields import FieldInfo

Agent = Literal[
    "agent/classifier",
    "agent/universe_discoverer",
    "agent/imandra_checker",
    "agent/ipl_analysis",
    "agent/ipl_job_data",
    "agent/ipl_checker",
    "agent/code_logician_general",
    "agent/code_logician_python",
    "agent/spec_logician_formal",
    "agent/reasoner_invoker",
    "agent/formalizer",
    "agent/prose_reasoner",
    "agent/fix_wizard",
]


def safe_string(agent: Agent | str) -> str:
    return agent.removeprefix("agent/")


class ImandraMetadata(BaseModel):
    task_name: str | None = None
    stream_responses: bool | None = None


class NodeMetadata(BaseModel):
    imandra: ImandraMetadata | None = None

    def items(self) -> list[tuple[str, Any]]:
        res = {}
        nested = self.model_dump()
        for key, value in nested.items():
            if isinstance(value, dict):
                for inner_key, inner_value in value.items():
                    if inner_value is not None:
                        res[f"{key}_{inner_key}"] = str(inner_value)
            elif value is not None:
                res[key] = str(value)

        return res.items()


class InterruptMessage(BaseModel):
    agent: Agent | str = Field(description="Name of the agent")
    output: str = Field(
        description="Current output of the agent, providing context for feedback"
    )
    prompt: str = Field(description="Prompt used to ask for feedback")
    id: str = Field(default_factory=lambda _: str(uuid.uuid4()))

    def to_messages(self) -> list[AIMessage]:
        return [
            AIMessage(
                content=self.output,
                name=safe_string(self.agent),
                id=f"{self.id}-output",
            ),
            AIMessage(
                content=self.prompt,
                name=safe_string(self.agent),
                id=f"{self.id}-prompt",
            ),
        ]

    def to_dicts(self) -> list[dict]:
        msgs = self.to_messages()
        return [m.model_dump() for m in msgs]

    def __repr__(self) -> str:
        s = (
            f"### InterruptMessage\n\n"
            f"#### Agent: {self.agent}\n\n"
            "#### Output\n"
            f"{self.output}\n\n"
            "#### Prompt\n"
            f"{self.prompt}\n"
        )
        s = s.replace("```iml", "```ocaml")
        return s


class EndResult(BaseModel):
    """
    Fulfilled right before `__end__` node.
    """

    result: Literal["success", "failure", "abort"] = Field(
        description="Final result of agent calling"
    )
    info: str | None = Field(
        default=None, description="Additional information about the result"
    )


# Require extra="forbid" to generate OpenAI-strict compatible JSON Schemas
# (with additionalProperites="false")
class InputBase(BaseModel, extra="forbid"):
    pass


class AgentDisclosure(BaseModel, abc.ABC):
    """
    Communicate with other agents.
    """

    hil_messages: Annotated[Sequence[BaseMessage] | None, add_messages] = Field(
        [],
        description="Interruption and resuming messages. Q&A during human-in-the-loop.",
    )
    end_result: EndResult = Field(description="End result of the whole task.")

    @abc.abstractmethod
    def render(self) -> str:
        """Render state using Markdown"""
        pass

    def __repr__(self) -> str:
        return pformat(self, indent=2)


def create_partial_graph_state(
    input_state_cls: type[BaseModel], graph_state_cls: type[BaseModel]
):
    """
    Create a new state class where:
    - Fields from InputState remain unchanged
    - Additional fields from GraphState become optional
    - Metadata of fields is not preserved. **Reducer is not preserved.**

    Should only be used to annotate input fields of GraphState for intermediate nodes.
    """
    input_fields: dict[str, FieldInfo] = input_state_cls.model_fields
    graph_fields: dict[str, FieldInfo] = graph_state_cls.model_fields

    new_fields = {}

    for field_name, field in graph_fields.items():
        if field_name in input_fields:
            # Keep original field from InputState
            new_fields[field_name] = (field.annotation, field.default)
        else:
            # Check if field is already Optional
            field_type = field.annotation
            if typing.get_origin(field_type) is typing.Union and type(
                None
            ) in typing.get_args(field_type):
                # Field is already Optional, keep it as is
                new_fields[field_name] = (field_type, field.default)
            else:
                # Make field Optional
                new_fields[field_name] = (field_type | None, None)

    return create_model("PartialOutput", __base__=input_state_cls, **new_fields)


AgentType = Literal["one_shot_tool", "interruptible_agent"]


class AgentGraph(BaseModel):
    agent_type: AgentType
    full_name: str
    task_name: str
    use_case: str
    tool_description: str
    input_schema: type[InputBase] | Callable[[], type[InputBase]]
    state_schema: type[AgentDisclosure]
    config: type[BaseModel]

    def input_type(self) -> type[InputBase]:
        return (
            self.input_schema() if isfunction(self.input_schema) else self.input_schema
        )
