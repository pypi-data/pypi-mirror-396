import os
from typing import Literal

import imandra.ipl as ipl
from langgraph.types import Command
from urllib3.util import parse_url

from agents.ipl_checker.base import InputState
from utils.agent.base import EndResult


def ipl_check(state: InputState, config) -> Command[Literal["__end__"]]:
    print("--- Node: IPL CHECK ---")
    ipl_code = state.ipl_code

    imandra_api_key = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )
    url = parse_url(os.getenv("IMANDRA_U_URL"))
    client = ipl.Client(api_key=imandra_api_key, scheme=url.scheme, host=url.host)

    try:
        validation = client.validate(model=ipl_code)
        # Consider including warnings here, or make the inclusion configurable
        errors = [x for x in validation if x["severity"] == 1]
        if errors == []:
            result = "success"
            info = "IPL check succeeded"
        else:
            result = "failure"
            info = "IPL check failed"
    except ValueError as e:
        result = "failure"
        info = str(e)
        validation = None

    end_result = EndResult(result=result, info=info)
    goto = "__end__"
    update = {
        "ipl_check_res": validation,
        "end_result": end_result,
    }
    return Command(goto=goto, update=update)
