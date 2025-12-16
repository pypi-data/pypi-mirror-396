from typing import Literal

from devtools import pformat
from langgraph.graph import START, StateGraph
from langgraph.types import Command

from agents.code_logician.formalizer.decomposer.base import GraphState, InputState
from agents.code_logician.reasoner.nodes.extract_reasoning_req import (
    RawDecomposeReq,
    extract_raw_decompose_reqs,
)
from utils.agent.base import EndResult
from utils.imandra.imandrax.async_client import decompose, eval_src, get_imandrax_client
from utils.llm import get_llm


async def decomp_main(state: InputState, config) -> Command[Literal["__end__"]]:
    src_code = state.src_code
    iml_code = state.iml_code
    llm = get_llm(use_case="code")
    imandra_api_key: str = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )

    # Extract
    raw_reqs: list[RawDecomposeReq] = await extract_raw_decompose_reqs(
        llm, src_code, iml_code, "main_function"
    )
    iml_func_name = raw_reqs[0].iml_func_name  # TODO: error handling?
    update = {"iml_func_name": iml_func_name}

    # Run decomp
    async with get_imandrax_client(imandra_api_key) as imx_client:
        _ = await eval_src(imx_client, iml_code)
        decomp_res = await decompose(imx_client, name=iml_func_name, ctx_simp=True)
    update |= {
        "decomp_res": decomp_res,
    }

    if not decomp_res.errors:
        update["end_result"] = EndResult(result="success")
    else:
        update["end_result"] = EndResult(
            result="failure", info=pformat(decomp_res.errors)
        )

    return Command(
        goto="__end__",
        update=update,
    )


builder = StateGraph(GraphState, input_schema=InputState)

builder.add_node("decomp_main", decomp_main)

builder.add_edge(START, "decomp_main")


graph = builder.compile()
