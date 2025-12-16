import json
import uuid

from pydantic import BaseModel, Field

from utils.agent.base import (
    AgentDisclosure,
    InputBase,
    create_partial_graph_state,
)


class InputState(InputBase):
    ipl_code: str = Field(..., description="The IPL code to be checked")


class GraphState(InputState, AgentDisclosure):
    ipl_check_res: list[dict] | None

    def render(self, as_sub_agent: bool = False) -> str:
        return f"IPL check result: {json.dumps(self.ipl_check_res)}"


PartialOutput = create_partial_graph_state(InputState, GraphState)


class GraphConfig(BaseModel):
    thread_id: str = Field(default_factory=lambda _: str(uuid.uuid4()))
