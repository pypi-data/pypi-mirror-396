from pydantic import BaseModel, Field

from agents.formalizer.base import (
    InputState as FormalizerInput,
)
from agents.reasoner_invoker.base import (
    GraphState as InvokerOutput,
    InputState as InvokerInput,
)
from utils.agent.base import AgentDisclosure, create_partial_graph_state
from utils.llm import MODEL_NAME


class InputState(FormalizerInput):
    pass


class GraphState(InputState, InvokerInput, AgentDisclosure):
    output: InvokerOutput = Field(None, description="Output of formal reasoning")

    def render(self) -> str:
        return self.output.render()


PartialOutput = create_partial_graph_state(InputState, GraphState)


class GraphConfig(BaseModel):
    llm_model_name: MODEL_NAME | None = None
    max_retries: int = 1
