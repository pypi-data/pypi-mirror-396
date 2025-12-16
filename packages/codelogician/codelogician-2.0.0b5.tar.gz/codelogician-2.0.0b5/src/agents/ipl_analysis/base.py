import uuid
from collections.abc import Sequence
from enum import Enum
from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field

from utils.agent.base import (
    AgentDisclosure,
    InputBase,
)


class AnalysisMode(str, Enum):
    Decompose = "decompose"
    UnsatAnalysis = "unsat_analysis"


class InputState(InputBase):
    # The assumption is that this IPL spec is already checked for correctness
    ipl_code: str = Field(..., description="The IPL spec to decompose")
    mode: AnalysisMode


class GraphState(InputState, AgentDisclosure):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    job_uuid: str

    def render(self) -> str:
        return f"{self.mode} running with job uuid: {self.job_uuid}"


class GraphConfig(BaseModel):
    thread_id: str = Field(default_factory=lambda _: str(uuid.uuid4()))
