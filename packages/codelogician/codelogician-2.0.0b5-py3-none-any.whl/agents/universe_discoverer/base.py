from pydantic import BaseModel, Field

from utils.agent.base import AgentDisclosure, InputBase
from utils.llm import MODEL_NAME


class InputState(InputBase):
    query: str = Field(..., description="The query to search the universe")


class GraphState(InputState, AgentDisclosure):
    response: str

    def render(self) -> str:
        return self.response


class GraphConfig(BaseModel):
    llm_model_name: MODEL_NAME | None = None
