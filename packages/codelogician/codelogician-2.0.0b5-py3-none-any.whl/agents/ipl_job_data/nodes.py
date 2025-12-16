import io
import json
import os
import tarfile
from typing import Literal

import imandra.ipl as ipl
from langgraph.types import Command
from urllib3.util import parse_url

# from langchain_core.messages import AIMessage
from agents.ipl_job_data.base import (
    # GraphState,
    InputState,
    # PartialOutput,
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


def extract_decomp_tree(raw_data):
    with (
        io.BytesIO(raw_data["content"]) as tar_stream,
        tarfile.open(fileobj=tar_stream) as tar,
    ):
        decomp_file = tar.extractfile(tar.getmember("out/decomposition_tree.json"))
        data_raw = decomp_file.read()
        return json.loads(data_raw)


def extract_unsat_cores(raw_data):
    return raw_data["content"].decode("ascii")


def get_data(graph_state: InputState, config) -> Command[Literal["__end__"]]:
    print("--- Node: Awaiting IPL Data ---")
    client = _get_ipl_client(config)

    if graph_state.wait:
        status = client.wait(graph_state.job_uuid)
    else:
        status = client.status(graph_state.job_uuid)
    if status != "done":
        return Command(
            goto="__end__",
            update={
                "end_result": EndResult(
                    result="failure",
                    # TODO: accurate data here
                ),
                "data": None,
            },
        )

    raw_data = client.data(graph_state.job_uuid)
    match raw_data["content_type"]:
        # TODO: this isn't a particularly robust way of differentiating the two
        # requests, but the only way I see for now.
        # Really the API should also report what kind
        # of data is being returned.

        case "text/plain":
            # TODO: Also, it would be nice if this produced structured data
            # instead of a string...
            data = extract_unsat_cores(raw_data)
        case "application/gzip":
            data = extract_decomp_tree(raw_data)

    return Command(
        goto="__end__",
        update={
            "end_result": EndResult(
                result="success",
            ),
            "data": data,
        },
    )
