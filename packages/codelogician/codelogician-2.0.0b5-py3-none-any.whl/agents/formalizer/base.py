from pydantic import BaseModel, Field

from utils.agent.base import AgentDisclosure, InputBase, create_partial_graph_state
from utils.llm import MODEL_NAME


class InputState(InputBase):
    reasoner: str = Field(
        ...,
        description=("The Reasoner to invoke."),
    )
    raw_input: str = Field(
        ...,
        description=("The raw input to formalize."),
    )


class GraphState(InputState, AgentDisclosure):
    formalized_code: str = Field(
        ..., description="Formalized code to pass to the Reasoner."
    )

    def render(self) -> str:
        return


PartialOutput = create_partial_graph_state(InputState, GraphState)


class GraphConfig(BaseModel):
    llm_model_name: MODEL_NAME | None = None
