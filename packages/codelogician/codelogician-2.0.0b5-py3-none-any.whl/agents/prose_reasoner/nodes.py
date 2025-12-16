from typing import Literal

import structlog
from langgraph.types import Command
from pydantic import BaseModel, Field

from agents.formalizer.graph import graph as formalizer
from agents.prose_reasoner.base import InputState, PartialOutput
from agents.reasoner_invoker.base import GraphState as InvokerState
from agents.reasoner_invoker.graph import graph as reasoner_invoker

logger = structlog.get_logger("agents.formalizer.nodes")


class FormalizedCode(BaseModel):
    code: str = Field(..., description="Formalized code to pass to the Reasoner.")


async def formalize(state: InputState, config) -> Command[Literal["invoke"]]:
    logger.info("formalize_node_started")
    formalized_code = await formalizer.ainvoke(state, config=config)["formalized_code"]
    return Command(
        update={"src_input": formalized_code},
        goto="invoke",
    )


async def invoke(state: PartialOutput, config) -> Command[Literal["__end__"]]:
    logger.info("invoke_node_started")
    output = InvokerState(**(await reasoner_invoker.ainvoke(state, config)))
    end_result = output.end_result
    return Command(update={"output": output, "end_result": end_result}, goto="__end__")
