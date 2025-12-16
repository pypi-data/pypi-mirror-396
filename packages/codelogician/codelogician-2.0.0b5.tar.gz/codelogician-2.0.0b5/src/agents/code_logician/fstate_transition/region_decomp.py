import asyncio
from typing import Literal

import structlog
from langsmith import traceable

from agents.code_logician.base.model_utils.iml import add_requests
from utils.imandra.imandrax.async_client import eval_src, get_imandrax_client
from utils.llm import get_llm

from ..base import (
    DecomposeReqData,
    FormalizationState,
    FormalizationStateUpdate,
    RawDecomposeReq,
    RegionDecomp,
)
from ..base.model_utils import decompose_req_data_post
from ..tools.region_decomp import gen_raw_decomp_reqs
from ..tools.region_decomp.gen_test import async_gen_tests

logger = structlog.get_logger(__name__)


@traceable
async def gen_region_decomp(
    state: FormalizationState,
    config,
    method: Literal["main_function", "comments", "nat_lang_req"] = "comments",
    nat_lang_req: str | None = None,
) -> FormalizationStateUpdate:
    src_code = state.src_code
    iml_code = state.iml_code
    iml_model = state.iml_model
    if iml_code is None:
        raise ValueError("IML code is required")
    if iml_model is None:
        raise ValueError("IML model is required")
    llm = get_llm(use_case="code")

    # Generate raw decompose requests
    raw_decompose_reqs: list[RawDecomposeReq] = await gen_raw_decomp_reqs(
        llm, src_code, iml_code, method, nat_lang_req
    )
    logger.info("raw_decompose_requests_generated", count=len(raw_decompose_reqs))
    logger.debug("raw_decompose_requests", requests=raw_decompose_reqs)
    decomps = [RegionDecomp(raw=raw) for raw in raw_decompose_reqs]

    # Generate decompose data
    # TODO: determine parameters (basis, assumptions, etc.)
    for i, decomp in enumerate(decomps):
        raw_decomp = decomp.raw
        if raw_decomp is None:
            continue
        decomp_data = DecomposeReqData(
            name=raw_decomp.iml_func_name,
            ctx_simp=True,
        )
        decomps[i].data = decomp_data

    # Run decompose
    async with get_imandrax_client(
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    ) as imx_client:
        await eval_src(imx_client, iml_code)

        # Parallelize decompose calls
        decomp_tasks = [
            decompose_req_data_post(decomp.data, imx_client)
            for decomp in decomps
            if decomp.data is not None
        ]
        decomp_results = await asyncio.gather(*decomp_tasks)

        # Process results
        for i, decomp_res in enumerate(decomp_results):
            # TODO: artifact and task is dropped
            if decomp_res.artifact is not None:
                original_bytes_len = len(decomp_res.artifact.data)
                logger.info("dropping_decomp_artifact", bytes_len=original_bytes_len)
                len_repr = b"1e" + bytes(int(original_bytes_len ** (1 / 10)))
                decomp_res.artifact.data = len_repr + b"_bytes_dropped"
            decomp_res.task = None
            decomps[i].res = decomp_res

    updated_region_decomps = state.region_decomps + decomps
    vgs = state.vgs
    iml_code = add_requests(
        iml_model,
        [rd.data for rd in updated_region_decomps if rd.data is not None],
        [vg.data for vg in vgs if vg.data is not None],
    )

    return FormalizationStateUpdate(
        iml_code=iml_code, region_decomps=updated_region_decomps
    )


@traceable
async def gen_test_cases(
    state: FormalizationState,
    config,
    decomp_idx: int,
) -> FormalizationStateUpdate:
    src_lang = state.src_lang
    src_code = state.src_code
    iml_code = state.iml_code
    iml_model = state.iml_model
    decomps = state.region_decomps

    if iml_code is None:
        raise ValueError("IML code is required")
    if iml_model is None:
        raise ValueError("IML model is required")

    llm = get_llm(use_case="code")

    decomp = decomps[decomp_idx]
    decomp_raw = decomp.raw
    if decomp_raw is None:
        raise ValueError(f"Raw decomp request for {decomp_raw} is required")
    decomp_res = decomp.res
    if decomp_res is None:
        raise ValueError(f"Decompose result for {decomp_raw.src_func_name} is required")

    async with get_imandrax_client(
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    ) as imx_client:
        test_cases = await async_gen_tests(
            src_lang=src_lang,
            src_code=src_code,
            iml_code=iml_model,
            src_func_name=decomp_raw.src_func_name,
            iml_func_name=decomp_raw.iml_func_name,
            llm=llm,
            imandrax_client=imx_client,
            decompose_res=decomp_res,
            include_docstr=True,
            fallback=True,
        )
        decomps[decomp_idx].test_cases = test_cases

    return FormalizationStateUpdate(region_decomps=decomps)
