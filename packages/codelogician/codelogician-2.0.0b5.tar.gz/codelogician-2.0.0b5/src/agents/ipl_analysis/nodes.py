import os
from typing import Literal

import imandra.ipl as ipl
from langchain_core.messages import AIMessage
from langgraph.types import Command
from urllib3.util import parse_url

from agents.ipl_analysis.base import (
    AnalysisMode,
    InputState,
)
from utils.agent.base import EndResult


def _get_ipl_client(config):
    imandra_api_key = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )
    url = parse_url(os.getenv("IMANDRA_U_URL"))
    return ipl.Client(api_key=imandra_api_key, scheme=url.scheme, host=url.host)


def invoke_ipl_analysis(input_state: InputState, config) -> Command[Literal["__end__"]]:
    print("--- Node: Invoke IPL Decomposition ---")
    ipl_code = input_state.ipl_code
    client = _get_ipl_client(config)
    match input_state.mode:
        case AnalysisMode.Decompose:
            job_uuid = client.decompose(model=ipl_code)
            msg = f"Awaiting Decomp for Job UUID: {job_uuid}"
        case AnalysisMode.UnsatAnalysis:
            job_uuid = client.unsat_analysis(model=ipl_code)
            msg = f"Awaiting Unsat Analysis for Job UUID: {job_uuid}"

    print(msg)

    return Command(
        goto="__end__",
        update={
            "job_uuid": job_uuid,
            "messages": AIMessage(content=msg),
            "end_result": EndResult(result="success", info=msg),
        },
    )
