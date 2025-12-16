import uuid
from collections.abc import Sequence
from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field

from utils.agent.base import (
    AgentDisclosure,
    InputBase,
)


class InputState(InputBase):
    job_uuid: str
    wait: bool


class GraphState(InputState, AgentDisclosure):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    data: dict | str | None

    def render(self) -> str:
        if not self.data:
            return f"job still running with uuid: {self.job_uuid}"
        return f"Data correctly grabbed for uuid: {self.job_uuid}"


class GraphConfig(BaseModel):
    thread_id: str = Field(default_factory=lambda _: str(uuid.uuid4()))
