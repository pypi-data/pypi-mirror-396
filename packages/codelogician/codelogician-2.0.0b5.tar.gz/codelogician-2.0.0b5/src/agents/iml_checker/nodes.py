from typing import Literal

from google.protobuf.json_format import MessageToDict
from langgraph.types import Command

from agents.code_logician.imandrax_model_utils import error_to_llm_context
from agents.iml_checker.base import InputState, PartialOutput
from utils.agent.base import EndResult
from utils.fdb.fdb import get_fdb
from utils.imandra.imandrax.async_client import get_imandrax_client
from utils.imandra.imandrax.proto_models.simple_api import EvalRes


async def imandra_check(
    state: InputState, config
) -> Command[Literal["retrieve_hints", "__end__"]]:
    """
    <Node> Imandra check
    """
    print("--- Node: Imandra CHECK ---")
    iml_code: str = state.iml_code
    imandra_api_key: str = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )

    # Imandra session
    async with get_imandrax_client(imandra_api_key) as imx_client:
        # Imandra check
        _imx_eval_res = await imx_client.eval_src(iml_code)
    imx_eval_res: dict = MessageToDict(_imx_eval_res)
    # imx_eval_res = {"success": True, "errors": [{"msg": {"msg": "error"}}]}  # Fake client  # noqa: E501
    imx_eval_res = EvalRes(**imx_eval_res)

    if not imx_eval_res.errors:
        end_result = EndResult(
            result="success",
        )
        goto = "__end__"
        print("\t- Imandra check success")
    else:
        end_result = EndResult(
            result="failure",
            info="IML check failed",
        )
        goto = "retrieve_hints"
        print("\t- Imandra check failed")

    update = {
        "iml_check_res": imx_eval_res,
        "end_result": end_result,
    }
    return Command(goto=goto, update=update)


async def retrieve_hints(state: PartialOutput, config) -> Command[Literal["__end__"]]:
    """
    <Node> Retrieve relevant hints from FDB
    """
    print("--- Node: RETRIEVING RELEVANT HINTS ---")
    iml_check_res: EvalRes = state.iml_check_res

    iml_errs: list[str] = [error_to_llm_context(e) for e in iml_check_res.errors]

    fdb = get_fdb()
    sim_err_suggestions: list[dict] = [
        (await fdb.search_error(iml_err))[0].to_dict() for iml_err in iml_errs
    ]
    sim_err_suggestions_ = [
        {
            "err_msg": e["msg_str"],
            "suggestion": e["solution_description"],
        }
        for e in sim_err_suggestions
    ]
    return Command(
        goto="__end__",
        update={
            "similar_err_hints": sim_err_suggestions_,
        },
    )
