from collections.abc import Callable
from functools import wraps
from typing import Literal, ParamSpec, TypeVar

import structlog
from google.protobuf.json_format import MessageToDict
from imandrax_api.twirp.exceptions import TwirpServerException
from langchain_core.messages import AIMessage
from langgraph.types import Command

from agents.code_logician.imandrax_model_utils import eval_res_errors_to_llm_context
from agents.code_logician.reasoner.base import (
    PartialDecomposeReq,
    PartialOutput,
    PartialVerifyReq,
    RawReasonReq,
    ReasonerActionType,
    ReasonReq,
)
from agents.code_logician.reasoner.nodes.extract_reasoning_req import (
    RawDecomposeReq,
    RawVerifyReq,
    extract_raw_decompose_reqs,
    extract_raw_verify_reqs,
    gen_partial_verify_req,
)
from agents.code_logician.reasoner.nodes.gen_py_tests import async_gen_py_tests
from agents.code_logician.reasoner.nodes.sync_model import (
    UpdatedIMLCode,
    diff_code,
    retry_update_iml_code_prompt,
    update_iml_code_prompt,
    update_src_code,
)
from agents.code_logician.reasoner.nodes.utils import context_on_src_iml_correspondence
from utils.agent.base import EndResult
from utils.imandra.imandrax.async_client import (
    AsyncClient,
    decompose,
    eval_src,
    get_imandrax_client,
    instance_src,
)
from utils.imandra.imandrax.proto_models.error import Error, ErrorMessage
from utils.imandra.imandrax.proto_models.simple_api import (
    EvalRes,
    InstanceRes,
    VerifyRes,
)
from utils.llm import get_llm

P = ParamSpec("P")
R = TypeVar("R")

logger = structlog.get_logger(__name__)


def validate_input_state[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    # FIXME: This is a temporary fix for langgraph validation bugs
    @wraps(func)
    def wrapper(state: PartialOutput, *args: P.args, **kwargs: P.kwargs) -> R:
        logger.info("validating_state", function_name=func.__name__)
        validated_state = PartialOutput.model_validate(state.model_dump())
        return func(validated_state, *args, **kwargs)

    return wrapper


@validate_input_state
def reasoner_entry(
    state: PartialOutput,
) -> Command[
    Literal[
        "extract_verify_reqs",
        "extract_decompose_reqs",
        "gen_iml_verify_queries",
        "run_decompose",
        "run_verify",
        "sync_src",
        "sync_iml",
    ]
]:
    """Route the reasoning request based on the action"""
    logger.info("reasoner_entry_node_started")
    match state.action.type:
        case ReasonerActionType.EXTRACT_ALL:
            # Run extraction in parallel
            return Command(goto=["extract_verify_reqs", "extract_decompose_reqs"])
        case (
            (
                ReasonerActionType.GEN_IML_VERIFY_QUERIES
                | ReasonerActionType.RUN_VERIFY
            ) as at
        ):
            return Command(
                goto=at,
                update={"counter": 0},
            )
        case _ as at:
            return Command(goto=at)


# @validate_input_state
async def extract_verify_reqs(
    state: PartialOutput, config
) -> Command[Literal["gen_iml_verify_queries"]]:
    logger.info("extract_verify_requests_node_started")
    # NOTE: this replaces the decorator `@validate_input_state`
    # because it doesn't work with async functions
    state = PartialOutput.model_validate(state.model_dump())

    src_code = state.src_code
    iml_code = state.iml_code
    llm = get_llm(use_case="code")

    # Extract raw requests
    raw_reqs: list[RawVerifyReq] = await extract_raw_verify_reqs(
        llm, src_code, iml_code
    )
    logger.info("verify_requests_extracted", count=len(raw_reqs))

    raw_reqs = [
        RawReasonReq(content=raw_req, source="comments") for raw_req in raw_reqs
    ]

    return Command(
        goto="gen_iml_verify_queries",
        update={"verify_raw": raw_reqs, "counter": 0},
    )


# @validate_input_state
async def gen_iml_verify_queries(
    state: PartialOutput, config
) -> Command[Literal["__end__"]]:
    logger.info("gen_iml_verify_queries_node_started")
    # NOTE: this replaces the decorator `@validate_input_state`
    # because it doesn't work with async functions
    state = PartialOutput.model_validate(state.model_dump())

    iml_code = state.iml_code
    llm = get_llm(use_case="code")

    # Get raw verify reqs
    rvqs: list[RawVerifyReq] = [rrq.content for rrq in state.verify_raw]

    # Gen partial verify reqs
    partial_reqs: list[PartialVerifyReq] = [
        await gen_partial_verify_req(llm, rvq, iml_code) for rvq in rvqs
    ]
    reason_reqs = [
        ReasonReq(iml_query=partial_req, imx_res=None, extra=None)
        for partial_req in partial_reqs
    ]

    return Command(
        goto="__end__",
        update={
            "verify_req": reason_reqs,
            "end_result": EndResult(result="success"),
        },
    )


async def _verify_src_catching_internal_error(
    imandrax_client: AsyncClient,
    src: str,
) -> VerifyRes:
    """Catch internal error from ImandraX and serialize it to VerifyRes."""
    try:
        imx_res = await imandrax_client.verify_src(src=src)
        imx_res = VerifyRes(
            **MessageToDict(
                imx_res,
                preserving_proto_field_name=True,
                always_print_fields_with_no_presence=True,
            )
        )
    except TwirpServerException as e:
        if e.message == "Internal Server Error":
            imx_res = VerifyRes(
                errors=[
                    Error(
                        msg=ErrorMessage(
                            msg=e.to_dict()["meta"]["body"],
                        ),
                        kind="verify_internal",
                    )
                ],
            )
        else:
            raise e
    return imx_res


# @validate_input_state
async def run_verify(
    state: PartialOutput, config
) -> Command[Literal["fix_iml_verify_queries", "__end__"]]:
    logger.info("run_verify_node_started")
    # NOTE: this replaces the decorator `@validate_input_state`
    # because it doesn't work with async functions
    state = PartialOutput.model_validate(state.model_dump())

    iml_code = state.iml_code
    reason_reqs: list[ReasonReq] = state.verify_req
    imandra_api_key: str = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )

    # Initialize ImandraX client and evaluate IML code
    async with get_imandrax_client(imandra_api_key) as imx_client:
        logger.info("evaluating_iml_code", iml_code=iml_code)
        _ = await eval_src(imx_client, iml_code)

        # Track if any verification errors occurred
        has_verification_errors = False

        # Process each reasoning request
        extra = None
        for i, reason_req in enumerate(reason_reqs):
            match reason_req:
                case ReasonReq(
                    iml_query=PartialVerifyReq() as verify_req, imx_res=None
                ):
                    # Run verification and update result
                    logger.info("running_verification", verify_req=verify_req)
                    verification_result = await _verify_src_catching_internal_error(
                        imx_client, verify_req.predicate
                    )
                    # Check for refuted result
                    if verification_result.refuted is not None:
                        # Find counter-example if it's a counter-satisfiable error
                        logger.info("counter_example_found_triggering_instance")
                        instance_res: InstanceRes = await instance_src(
                            imx_client, verify_req.to_negation().predicate
                        )
                        instance_res: dict = instance_res.model_dump()
                        extra = {"instance_res": instance_res}
                    elif verification_result.errors:
                        # Trigger re-gen verify reqs
                        logger.info("verify_error_triggering_regen")
                        has_verification_errors = True

                    reason_reqs[i] = reason_req.model_copy(
                        update={"imx_res": verification_result, "extra": extra}
                    )
                case _:
                    continue

    update = {
        "verify_req": reason_reqs,
        "counter": state.counter + 1,
    }

    # Routing
    if (state.counter < 2) and has_verification_errors:
        logger.info("verify_error_retrying", counter=state.counter)
        goto = "fix_iml_verify_queries"
    else:
        if has_verification_errors:
            logger.info("verify_error_budget_exhausted")
        else:
            logger.info("verification_completed_successfully")
        goto = "__end__"
        update["end_result"] = EndResult(result="success")

    return Command(goto=goto, update=update)


# @validate_input_state
async def fix_iml_verify_queries(
    state: PartialOutput, config
) -> Command[Literal["run_verify"]]:
    logger.info("regen_verify_reqs_node_started")
    # NOTE: this replaces the decorator `@validate_input_state`
    # because it doesn't work with async functions
    state = PartialOutput.model_validate(state.model_dump())

    iml_code = state.iml_code
    raw_reason_reqs: list[RawReasonReq] = state.verify_raw
    reason_reqs: list[ReasonReq] = state.verify_req
    llm = get_llm(use_case="code")

    for i, (raw_rr, rr) in enumerate(zip(raw_reason_reqs, reason_reqs, strict=True)):
        match rr:
            case ReasonReq(
                iml_query=PartialVerifyReq() as verify_req, imx_res=imx_res
            ) if imx_res and imx_res.errors:
                # Re-gen verify reqs
                new_pvr = await gen_partial_verify_req(
                    llm=llm,
                    rvq=raw_rr.content,
                    iml_code=iml_code,
                    last_iml_query=verify_req.predicate,
                    last_error_msg=imx_res.errors[0].msg,
                )
                reason_reqs[i] = rr.model_copy(
                    update={"iml_query": new_pvr, "imx_res": None, "extra": None}
                )
            case _:
                continue

    return Command(
        goto="run_verify",
        update={"verify_req": reason_reqs},
    )


# @validate_input_state
async def extract_decompose_reqs(
    state: PartialOutput, config
) -> Command[Literal["run_decompose"]]:
    logger.info("extract_decompose_requests_node_started")
    # NOTE: this replaces the decorator `@validate_input_state`
    # because it doesn't work with async functions
    state = PartialOutput.model_validate(state.model_dump())

    src_code = state.src_code
    iml_code = state.iml_code
    action_params: dict | None = state.action.params
    extract_method = action_params.get("method") if action_params else "main_function"
    llm = get_llm(use_case="code")

    # Extract raw requests
    raw_reqs: list[RawDecomposeReq] = await extract_raw_decompose_reqs(
        llm, src_code, iml_code, extract_method
    )
    print(f"\tExtracted {len(raw_reqs)} decompose reqs")

    raw_reqs = [
        RawReasonReq(content=raw_req, source="comments") for raw_req in raw_reqs
    ]

    return Command(
        goto="run_decompose",
        update={"decompose_raw": raw_reqs},
    )


# @validate_input_state
async def run_decompose(state: PartialOutput, config) -> Command[Literal["__end__"]]:
    print("--- Node: Run Decompose ---")
    # NOTE: this replaces the decorator `@validate_input_state`
    # because it doesn't work with async functions
    state = PartialOutput.model_validate(state.model_dump())
    src_code = state.src_code
    iml_code = state.iml_code
    imandra_api_key: str = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )
    llm = get_llm(use_case="code")

    # Get partial decompose reqs
    rdrs: list[RawDecomposeReq] = [rrq.content for rrq in state.decompose_raw]
    reason_reqs = [
        ReasonReq(
            iml_query=PartialDecomposeReq.from_raw(rdr),
            imx_res=None,
            extra=None,
        )
        for rdr in rdrs
    ]

    # Run decomposition
    async with get_imandrax_client(imandra_api_key) as imx_client:
        _ = await eval_src(imx_client, iml_code)
        for i, rr in enumerate(reason_reqs):
            match rr:
                case ReasonReq(
                    iml_query=PartialDecomposeReq() as decomp_req, imx_res=None
                ):
                    decomp_res = await decompose(
                        imx_client, name=decomp_req.iml_func_name, ctx_simp=True
                    )

                    # Get extra info: gen test cases
                    test_cases = None
                    if not decomp_res.errors:
                        test_cases = await async_gen_py_tests(
                            py_code=src_code,
                            iml_code=iml_code,
                            py_func_name=decomp_req.src_func_name,
                            iml_func_name=decomp_req.iml_func_name,
                            imandrax_client=imx_client,
                            llm=llm,
                            decompose_res=decomp_res,
                            fallback=True,
                        )
                    extra = {"test_cases": test_cases} if test_cases else None

                    # Populate results
                    reason_reqs[i] = rr.model_copy(
                        update={
                            "imx_res": decomp_res,
                            "extra": extra,
                        }
                    )
                case _:
                    continue

    return Command(
        goto="__end__",
        update={
            "decompose_req": reason_reqs,
            "end_result": EndResult(result="success"),
        },
    )


# @validate_input_state
async def sync_src(state: PartialOutput, config) -> Command[Literal["__end__"]]:
    print("--- Node: Update src code based on iml diff ---")
    # NOTE: this replaces the decorator `@validate_input_state`
    # because it doesn't work with async functions
    state = PartialOutput.model_validate(state.model_dump())

    src_code = state.src_code
    iml_code = state.iml_code
    new_iml_code = state.action.params["new_iml_code"]
    llm = get_llm(use_case="code")

    iml_code_diff = diff_code(iml_code, new_iml_code)
    new_src_code = await update_src_code(llm, src_code, iml_code, iml_code_diff)

    return Command(
        goto="__end__",
        update={
            "src_code": new_src_code,
            "iml_code": new_iml_code,
            "end_result": EndResult(result="success"),
        },
    )


# @validate_input_state
async def sync_iml(state: PartialOutput, config) -> Command[Literal["__end__"]]:
    print("--- Node: Update iml code based on src diff ---")
    # NOTE: this replaces the decorator `@validate_input_state`
    # because it doesn't work with async functions
    state = PartialOutput.model_validate(state.model_dump())

    iml_code = state.iml_code
    src_code = state.src_code
    new_src_code = state.action.params["new_src_code"]
    llm = get_llm(use_case="code")
    imandra_api_key: str = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )

    src_code_diff = diff_code(src_code, new_src_code)

    msgs = [
        update_iml_code_prompt.format(
            context_on_src_iml_correspondence=context_on_src_iml_correspondence,
            iml_code=iml_code,
            orig_src_code=src_code,
            src_code_diff=src_code_diff,
        )
    ]

    try_count = 0
    async with get_imandrax_client(imandra_api_key) as imx_client:
        while True:
            new_iml_code = (
                await llm.with_structured_output(UpdatedIMLCode).ainvoke(msgs)
            ).iml_code
            imx_eval_res = await imx_client.eval_src(new_iml_code)
            imx_eval_res = EvalRes(**MessageToDict(imx_eval_res))
            if not imx_eval_res.errors or try_count > 3:
                break

            ai_msg = AIMessage(content=new_iml_code)
            human_msg = retry_update_iml_code_prompt.format(
                iml_error=eval_res_errors_to_llm_context(imx_eval_res)
            )
            msgs += [ai_msg, human_msg]
            try_count += 1

    if imx_eval_res.errors:
        print(
            f"\tFailed to update IML code after {try_count} retries. Consider "
            "re-formalizing the source code from scratch."
        )
    else:
        print(f"\tUpdated IML code after {try_count} retries")

    return Command(
        goto="__end__",
        update={
            "src_cde": new_src_code,
            "iml_code": new_iml_code,
            "end_result": EndResult(result="success"),
        },
    )
