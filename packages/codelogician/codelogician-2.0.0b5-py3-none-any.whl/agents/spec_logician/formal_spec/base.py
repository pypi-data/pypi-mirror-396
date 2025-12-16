from pydantic import BaseModel, Field

from agents.spec_logician.formal_spec.dsl.pretty_printing import pp_feature
from utils.agent.base import (
    AgentDisclosure,
    InputBase,
)

from . import templates
from .dsl.syntax import Feature


class InputState(InputBase):
    nat_lang_feature: str = Field(
        ...,
        description="The Cucumber Feature in natural language provided by the user",
    )


class PartialState(InputState):
    generated_feature: Feature
    generated_feature_rendered: str
    generated_decomp_ipl: str | None = Field(None)
    generated_unsat_ipl: str | None = Field(None)
    generated_ipl: str | None = Field(None)
    analysis_results: list[str] | None = Field(None)
    attempts: int


class GraphState(PartialState, AgentDisclosure):
    def render(self, as_sub_agent: bool = False) -> str:
        output = pp_feature(self.generated_feature)
        result = templates.final_result_ok.format(
            output=output, ipl_code=self.generated_ipl
        )
        return result


class GraphConfig(BaseModel):
    thread_id: str
