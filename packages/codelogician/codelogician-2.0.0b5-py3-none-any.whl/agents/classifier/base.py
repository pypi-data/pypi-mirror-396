from pydantic import BaseModel, Field

from agents.code_logician.formalizer.graph import (
    cl_non_py_agent as code_logician_general,
    cl_py_agent as code_logician_python,
)
from agents.fix_wizard.graph import agent as fix_wizard
from agents.formalizer.graph import agent as formalizer
from agents.iml_checker.graph import agent as iml_checker
from agents.ipl_analysis.graph import agent as ipl_analysis
from agents.ipl_checker.graph import agent as ipl_checker
from agents.ipl_job_data.graph import agent as ipl_job_data
from agents.prose_reasoner.graph import agent as prose_reasoner
from agents.reasoner_invoker.graph import agent as reasoner_invoker
from agents.spec_logician.formal_spec.graph import agent as spec_logician_formal
from agents.universe_discoverer.graph import agent as universe_discoverer
from utils.agent.base import Agent, AgentDisclosure, AgentGraph, InputBase
from utils.llm import MODEL_NAME

agents: dict[Agent, AgentGraph] = {
    "agent/universe_discoverer": universe_discoverer,
    "agent/reasoner_invoker": reasoner_invoker,
    "agent/imandra_checker": iml_checker,
    "agent/ipl_checker": ipl_checker,
    "agent/code_logician_general": code_logician_general,
    "agent/code_logician_python": code_logician_python,
    "agent/spec_logician_formal": spec_logician_formal,
    "agent/ipl_analysis": ipl_analysis,
    "agent/ipl_job_data": ipl_job_data,
    "agent/formalizer": formalizer,
    "agent/prose_reasoner": prose_reasoner,
    "agent/fix_wizard": fix_wizard,
}


class InputState(InputBase):
    problem: str = Field(..., description="The problem to be classified")


class GraphState(InputState, AgentDisclosure):
    task_handler: Agent
    scores: dict[Agent, float]

    def render(self) -> str:
        s = f"Recommended agent: {agents[self.task_handler].full_name}\n\n"
        s += "Score:\n\n"
        for handler, score in self.scores.items():
            s += f"- {agents[handler].full_name}: {score}\n\n"
        return s


class GraphConfig(BaseModel):
    llm_model_name: MODEL_NAME | None = None
