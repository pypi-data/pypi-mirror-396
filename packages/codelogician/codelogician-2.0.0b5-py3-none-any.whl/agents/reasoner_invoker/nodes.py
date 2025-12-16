import os
from typing import Literal

import duckdb
import structlog
from imandra.u.reasoners import Client
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field
from urllib3.util import parse_url

from agents.reasoner_invoker.base import (
    PartialOutput,
    ReasonerCall,
    ReasonerResult,
)
from agents.reasoner_invoker.prompt import (
    fix_prompt,
)
from agents.reasoner_invoker.rag import (
    connect_duckdb,
    ctxlize_errors,
    ctxlize_valid_inputs,
    load_vector_store,
)
from utils.agent.base import EndResult, InterruptMessage
from utils.llm import get_llm

logger = structlog.get_logger("cogito.agent.reasoner_invoker.nodes")


def call_reasoner(
    state: PartialOutput, config
) -> Command[Literal["confirm_attempt_change", "__end__"]]:
    logger.info("call_reasoner_node_started")
    reasoner: str = state.reasoner
    reasoner_calls: list[ReasonerCall] = state.reasoner_calls or []
    should_attempt_change: bool | None = state.should_attempt_change
    imandra_api_key = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )
    max_retries = config.get("configurable", {}).get("max_retries", 1)

    if not reasoner_calls:
        reasoner_call = ReasonerCall(input=state.src_input, result=None)
    else:
        reasoner_call: ReasonerCall = reasoner_calls[-1]

    url = parse_url(os.getenv("IMANDRA_U_URL"))
    if not url:
        raise ValueError("IMANDRA_U_URL is None")
    client = Client(
        scheme=url.scheme, host=url.host, reasoner=reasoner, api_key=imandra_api_key
    )

    # Eval
    res: dict = client.eval(reasoner_call.input)

    # Update
    res = ReasonerResult(**res)
    updated_reasoner_call = reasoner_call.model_copy(update={"result": res})
    updates = {
        "reasoner_calls": [*reasoner_calls[:-1], updated_reasoner_call],
    }

    # Route
    if res.errors:
        if should_attempt_change is None:
            goto = "confirm_attempt_change"
        elif not should_attempt_change:
            raise ValueError("We should not be here")
        else:
            n_attempts = len(reasoner_calls)
            if n_attempts < max_retries:
                goto = "attempt_change"
            else:
                end_result = EndResult(
                    result="failure",
                    info=(
                        f"Evaluation with Reasoner `{reasoner}` failed "
                        f"after {n_attempts} attempts."
                    ),
                )
                updates["end_result"] = end_result
                goto = "__end__"
    else:
        end_result = EndResult(
            result="success",
            info=f"Evaluation with Reasoner `{reasoner}` succeeded.",
        )
        updates["end_result"] = end_result
        goto = "__end__"

    return Command(update=updates, goto=goto)


class ConfirmAttemptChangeResult(BaseModel):
    """The result of the confirmation of whether to attempt to change the reasoner \
input."""

    should_attempt_change: bool = Field(
        ...,
        description="Whether to attempt to change the reasoner input.",
    )


async def confirm_attempt_change(
    state: PartialOutput,
) -> Command[Literal["retrieve_correction_context", "__end__"]]:
    logger.info("confirm_attempt_change_node_started")
    last_call: ReasonerCall = state.reasoner_calls[-1]
    error: str = "\n".join(last_call.result.errors)
    llm = get_llm(None, use_case="json")

    # Interrupt and get human feedback
    interrupt_msg = InterruptMessage(
        agent="reasoner_invoker",
        output=f"There were errors in the previous reasoner call:\n\n{error}\n",
        prompt="Should we try to fix the input and run the reasoner again?",
    )
    human_feedback: str = interrupt(interrupt_msg)

    # Parse human feedback
    result: ConfirmAttemptChangeResult = await llm.with_structured_output(
        ConfirmAttemptChangeResult
    ).ainvoke([HumanMessage(content=human_feedback)])

    # Update
    hil_messages = [*interrupt_msg.to_messages(), HumanMessage(content=human_feedback)]
    updates = {
        "should_attempt_change": result.should_attempt_change,
        "hil_messages": hil_messages,
    }

    # Route
    if result.should_attempt_change:
        goto = "retrieve_correction_context"
    else:
        end_result = EndResult(
            result="failure",
            info=(
                f"Evaluation with Reasoner `{state.reasoner}` failed. "
                "The user chose not to attempt to change the reasoner input."
            ),
        )
        updates["end_result"] = end_result
        goto = "__end__"

    return Command(update=updates, goto=goto)


class FixedInput(BaseModel):
    """The fixed input to pass to the reasoner."""

    fixed_input: str = Field(
        ...,
        description="The fixed input to pass to the reasoner.",
    )


def retrieve_correction_context(
    state: PartialOutput, config
) -> Command[Literal["attempt_change"]]:
    logger.info("retrieve_correction_context_node_started")

    reasoner: str = state.reasoner
    last_call: ReasonerCall = state.reasoner_calls[-1]

    # RAG: similar valid inputs and error and corrections
    con: duckdb.DuckDBPyConnection = connect_duckdb(reasoner)
    vector_stores = load_vector_store(con)
    sim_inputs: list[Document] = vector_stores["valid_input"].similarity_search(
        last_call.input, k=2
    )
    sim_corrections: list[Document] = vector_stores["error_vector"].similarity_search(
        "\n".join(last_call.result.errors), k=2
    )
    sim_inputs_strs = ctxlize_valid_inputs(sim_inputs, con)
    sim_corrections_strs = ctxlize_errors(sim_corrections, con)

    return Command(
        update={
            "retrieved_context": {
                "valid_inputs": "\n".join(sim_inputs_strs),
                "error_corrections": "\n".join(sim_corrections_strs),
            },
        },
        goto="attempt_change",
    )


async def attempt_change(
    state: PartialOutput, config
) -> Command[Literal["call_reasoner"]]:
    logger.info("attempt_change_node_started")
    reasoner: str = state.reasoner
    last_call: ReasonerCall = state.reasoner_calls[-1]
    model_name = config.get("configurable", {}).get("llm_model_name")
    llm = get_llm(model_name) if model_name else get_llm("code")
    retrieved_context = state.retrieved_context

    # Fix
    fix_msg = fix_prompt.format(
        reasoner=reasoner,
        input=last_call.input,
        error="\n".join(last_call.result.errors),
        similar_valid_inputs=retrieved_context["valid_inputs"],
        similar_error_corrections=retrieved_context["error_corrections"],
    )
    new_input = await llm.with_structured_output(FixedInput).ainvoke([fix_msg])

    return Command(
        update={
            "reasoner_calls": [
                *state.reasoner_calls,
                ReasonerCall(input=new_input.fixed_input, result=None),
            ],
        },
        goto="call_reasoner",
    )
