import asyncio
from typing import cast

import structlog
from langchain_core.messages import BaseMessage
from langsmith import trace, traceable

from agents.code_logician.base import (
    VG,
    DecomposeReqData,
    FormalizationState,
    FormalizationStateUpdate,
    FormalizationStatus,
    RegionDecomp,
    VerifyReqData,
)
from agents.code_logician.base.model_utils import (
    decompose_req_data_post,
    get_iml_model_with_dependencies,
    parse_iml,
    verify_req_data_post,
)
from agents.code_logician.tools.formalize_to_iml import (
    strip_block_quote_and_add_newline,
)
from utils.imandra.imandrax.async_client import eval_src, get_imandrax_client
from utils.imandra.imandrax.proto_models import EvalRes
from utils.llm import get_llm, support_anthropic_prompt_caching

from ..tools.formalize_to_iml import format_formalization_msgs

logger = structlog.get_logger(__name__)


@traceable
async def admit_model(fstate: FormalizationState, config) -> FormalizationStateUpdate:
    """Check IML code and find opaqueness"""
    full_iml = get_iml_model_with_dependencies(fstate)

    imandra_api_key = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )

    # Check IML
    with trace(name="eval_src", inputs={"full_iml": full_iml}) as rt:
        opaque: bool | None = None
        async with get_imandrax_client(imandra_api_key) as imx_client:
            imx_eval_res: EvalRes = await eval_src(imx_client, full_iml)

            # Find opaqueness and determine formalization status
            if imx_eval_res.has_errors:
                # TODO: should we have another status for PO errors?
                fstatus = FormalizationStatus.INADMISSIBLE
            else:
                if fstate.opaque_funcs:
                    opaque = True
                else:
                    opaque = False
                fstatus = (
                    FormalizationStatus.ADMITTED_WITH_OPAQUENESS
                    if opaque
                    else FormalizationStatus.TRANSPARENT
                )
        rt.end(outputs={"fstatus": fstatus, "opaque": opaque})

    update = FormalizationStateUpdate(
        status=fstatus,
        eval_res=imx_eval_res,
    )
    return update


async def set_model(
    fstate: FormalizationState,
    config,
    iml_code: str,
) -> FormalizationStateUpdate:
    imandra_api_key = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )

    parsed_res = parse_iml(iml_code)
    if parsed_res is None:
        logger.warning("IML code has syntax errors and cannot be parsed")
        (
            iml_model,
            top_defs,
            linting_errors,
            decomp_req_data,
            verify_req_data,
        ) = iml_code, [], [], [], []
    else:
        (
            iml_model,
            top_defs,
            linting_errors,
            decomp_req_data,
            verify_req_data,
        ) = parsed_res

    # Parse update
    update1 = FormalizationStateUpdate(
        status=FormalizationStatus.UNKNOWN,
        iml_code=iml_code,
        iml_model=iml_model,
        top_definitions=top_defs,
        linting_errors=linting_errors,
    )
    fstate1 = FormalizationState.model_validate(fstate.model_copy(update=update1))

    # eval_src
    update2 = await admit_model(fstate1, config)

    # handle decomp / verify requests: override existing
    region_decomps = [
        RegionDecomp(data=decomp_req_data_item)
        for decomp_req_data_item in decomp_req_data
    ]
    vgs = [VG(data=verify_req_data_item) for verify_req_data_item in verify_req_data]

    if len(region_decomps) + len(vgs) == 0:
        return update1 | update2

    async with get_imandrax_client(imandra_api_key) as imx_client:
        # TODO: we eval model twice, once in admit_model and once here
        _eval_res = await eval_src(imx_client, iml_model)

        decomp_tasks = [
            decompose_req_data_post(
                cast(DecomposeReqData, rd.data),
                imx_client,
            )
            for rd in region_decomps
        ]
        verify_tasks = [
            verify_req_data_post(
                cast(VerifyReqData, vg.data),
                imx_client,
            )
            for vg in vgs
        ]

        # Run everything concurrently
        decomp_results, verify_results = await asyncio.gather(
            asyncio.gather(*decomp_tasks), asyncio.gather(*verify_tasks)
        )

        # Assign results
        for i, res in enumerate(decomp_results):
            region_decomps[i].res = res
        for i, res in enumerate(verify_results):
            vgs[i].res = res
    update3 = FormalizationStateUpdate(
        region_decomps=region_decomps,
        vgs=vgs,
    )

    return update1 | update2 | update3


@traceable
async def convert_to_iml(
    fstate: FormalizationState, config
) -> FormalizationStateUpdate:
    """
    <Node> Convert to IML

    1. Compose formalization messages
    - IML 101 with meta examples (S)
    - (Python only) Relevant examples (few shot messages, HAHAHA...)
    - Context messages (H)
    - Source code (H)
    - (Previous formalization) IML code (A)
    - (Previous formalization) error and hints (H)

    2. Convert and check

    3. Find opaqueness and determine formalization status
    """
    src_lang = fstate.src_lang
    src_code = fstate.src_code
    refactored_code = fstate.refactored_code
    src_info = fstate.conversion_source_info
    failures_info = fstate.conversion_failures_info
    dependency = fstate.dependency

    if refactored_code:
        code = refactored_code[-1][1]
    else:
        code = src_code

    if src_info is None:
        raise ValueError("Source info is required")

    if config.get("configurable", {}).get("use_small_llm", False):
        llm = get_llm(use_case="json")
    else:
        llm = get_llm(use_case="code")

    cache_prompt = config.get("configurable", {}).get("cache_prompt", False)
    cache_prompt = cache_prompt and support_anthropic_prompt_caching(llm)

    msgs = format_formalization_msgs(
        src_lang,
        code,
        src_info,
        dependency,
        failures_info,
        cache_prompt,
    )

    # Convert to IML
    res: BaseMessage = await llm.ainvoke(msgs)
    iml_model: str = cast(str, res.content)

    # Strip block-quote and add newline
    iml_model = strip_block_quote_and_add_newline(iml_model)

    update = await set_model(fstate, config, iml_model)

    assert iml_model == update["iml_model"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
    assert "region_decomps" not in update
    assert "vgs" not in update

    update |= FormalizationStateUpdate(region_decomps=[], vgs=[])

    return update
