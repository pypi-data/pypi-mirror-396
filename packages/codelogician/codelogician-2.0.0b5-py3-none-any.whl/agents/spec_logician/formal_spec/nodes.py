import os
from pathlib import Path
from typing import Literal

import imandra.ipl as ipl
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import Command
from urllib3.util import parse_url

from agents.spec_logician.formal_spec.base import (
    InputState,
    PartialState,
)
from agents.spec_logician.formal_spec.dsl.checking import check_feature
from agents.spec_logician.formal_spec.dsl.codegen import (
    generate_base_ipl,
    generate_decomp_ipl,
    generate_unsat_ipl,
)
from agents.spec_logician.formal_spec.dsl.feedback import pp_feedback
from agents.spec_logician.formal_spec.dsl.pretty_printing import pp_feature
from agents.spec_logician.formal_spec.dsl.syntax import Feature
from utils.agent.base import EndResult
from utils.llm import get_llm

current_dir = Path(__file__).resolve().parent
ipl_expr_101 = current_dir / "ipl-expr-101.md"
sys_prompt = current_dir / "sys-prompt.md"

trans_prompt_template = """
Translate this Cucumber Feature into a Formal Feature:

```
{cucumber}
```
"""


def _get_ipl_client(imandra_api_key: str | None = None):
    imandra_u_url = os.getenv("IMANDRA_U_URL")
    imandra_api_key = imandra_api_key or os.getenv("IMANDRA_API_KEY")
    if not imandra_u_url:
        raise ValueError("IMANDRA_U_URL is None")
    if not imandra_api_key:
        raise ValueError("IMANDRA_API_KEY is None")
    url = parse_url(imandra_u_url)
    return ipl.Client(api_key=imandra_api_key, scheme=url.scheme, host=url.host)


async def invoke_llm(config, messages) -> Feature:
    model_name = config.get("configurable", {}).get("llm_model_name", None)
    llm = get_llm(model_name) if model_name else get_llm(use_case="code")
    response = await llm.with_structured_output(schema=Feature).ainvoke(messages)
    return response


def compose_init_msgs(state: InputState, config):
    ipl_expr_101_content = ipl_expr_101.read_text()
    sys_prompt_content = sys_prompt.read_text()

    nl_feature = state.nat_lang_feature
    trans_request = trans_prompt_template.format(cucumber=nl_feature)
    return [
        SystemMessage(ipl_expr_101_content),
        SystemMessage(sys_prompt_content),
        HumanMessage(trans_request),
    ]


def compose_feedback(analysis_results: list[str]):
    feedback_list = "\n".join([f"* {fb}" for fb in analysis_results])
    feedback_text = f"""
        There were some issues with the Formal Spec you generated.
        Please address them:

        {feedback_list}
        """
    return HumanMessage(feedback_text)


async def generate_feature(state: InputState, config) -> Command[Literal["run_checks"]]:
    print("--- Node: GENERATE INITIAL FEATURE JSON ---")
    init_msgs = compose_init_msgs(state, config)
    response = await invoke_llm(config, init_msgs)
    update = {
        "generated_feature": response,
        "generated_feature_rendered": pp_feature(response),
        "attempts": 0,
    }
    return Command(goto="run_checks", update=update)


async def regenerate_feature(
    state: PartialState, config
) -> Command[Literal["run_checks"]]:
    print("--- Node: REGENERATE FEATURE JSON FROM FEEDBACK ---")
    init_msgs = compose_init_msgs(state, config)
    prior_attempt_msg = AIMessage(state.generated_feature.model_dump_json())
    msgs = [*init_msgs, prior_attempt_msg]
    if state.analysis_results is not None:
        feedback_msg = compose_feedback(state.analysis_results)
        msgs = [*msgs, feedback_msg]
    response = await invoke_llm(config, msgs)
    attempts = state.attempts + 1
    update = {
        "generated_feature": response,
        "generated_feature_rendered": pp_feature(response),
        "analysis_results": None,
        "attempts": attempts,
    }
    return Command(goto="run_checks", update=update)


def run_checks(
    state: PartialState, config
) -> Command[Literal["regenerate_feature", "__end__"]]:
    print("--- Node: RUN CHECKS ---")
    imandra_api_key: str = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )
    ipl_client = _get_ipl_client(imandra_api_key)
    feature = state.generated_feature
    check_results = check_feature(ipl_client, feature)
    feedback = [pp_feedback(fb) for fb in check_results]
    generated_decomp_ipl = generate_decomp_ipl(feature) if len(feedback) == 0 else None
    generated_unsat_ipl = generate_unsat_ipl(feature) if len(feedback) == 0 else None
    generated_ipl = generate_base_ipl(feature) if len(feedback) == 0 else None
    update = {
        "generated_feature": feature,
        "generated_decomp_ipl": generated_decomp_ipl,
        "generated_unsat_ipl": generated_unsat_ipl,
        "generated_ipl": generated_ipl,
        "analysis_results": feedback,
    }
    if len(feedback) > 0 and state.attempts < 3:
        goto = "regenerate_feature"
    else:
        if len(feedback) > 0:
            human_feedback = [pp_feedback(fb, for_llm=False) for fb in check_results]
            info = "\n".join(human_feedback)
            update["end_result"] = EndResult(result="failure", info=info)
            goto = "__end__"
        else:
            update["end_result"] = EndResult(result="success", info="")
            goto = "__end__"
    return Command(goto=goto, update=update)
