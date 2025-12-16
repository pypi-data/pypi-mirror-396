from typing import Literal

import structlog
from langgraph.types import Command
from pydantic import BaseModel, Field

from agents.formalizer.base import InputState
from agents.formalizer.prompt import translate_prompt
from utils.llm import get_llm

logger = structlog.get_logger("agents.formalizer.nodes")


class FormalizedCode(BaseModel):
    code: str = Field(..., description="Formalized code to pass to the Reasoner.")


async def translate(state: InputState, config) -> Command[Literal["__end__"]]:
    logger.info("translate_node_started")
    formalized_code: FormalizedCode = (
        await get_llm(None, use_case="code")
        .with_structured_output(FormalizedCode)
        .ainvoke(
            translate_prompt.format_messages(
                reasoner=state.reasoner, raw_input=state.raw_input
            )
        )
    )
    return Command(update={"formalized_code": formalized_code.code}, goto="__end__")
