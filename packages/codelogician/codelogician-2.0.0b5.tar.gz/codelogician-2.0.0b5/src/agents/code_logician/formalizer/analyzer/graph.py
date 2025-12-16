from typing import Literal

from langgraph.graph import START, StateGraph
from langgraph.types import Command

from agents.code_logician.formalizer.analyzer.base import GraphState, InputState
from agents.code_logician.formalizer.analyzer.utils import find_missing_func
from utils.agent.base import EndResult, ImandraMetadata, NodeMetadata
from utils.fdb.fdb import get_fdb


async def appropriateness_check(state: InputState) -> Command[Literal["__end__"]]:
    """
    <Node> Check if the Python code is within the scope of Imandra's capability.
    """
    print("--- Node: APPROPRIATENESS CHECK ---")
    src_code = state.src_code
    src_lang = "python"

    fdb = get_fdb()
    missing_func: list[dict] = await find_missing_func(fdb, src_code, src_lang)
    inappropriateness = [mf["src_code"] for mf in missing_func]

    # Logging
    if missing_func:
        info = f"Inappropriateness found: {inappropriateness}"
    else:
        info = "Passed appropriateness check."
    print(info)

    # Routing
    update = {"inappropriateness": inappropriateness}
    update["end_result"] = EndResult(
        result="success",
        info=info,
    )

    return Command(
        update=update,
        goto="__end__",
    )


builder = StateGraph(GraphState, input_schema=InputState)

builder.add_node(
    "appropriateness_check",
    appropriateness_check,
    metadata=NodeMetadata(imandra=ImandraMetadata(task_name="Analyzing Python code")),
)

builder.add_edge(START, "appropriateness_check")


graph = builder.compile()
