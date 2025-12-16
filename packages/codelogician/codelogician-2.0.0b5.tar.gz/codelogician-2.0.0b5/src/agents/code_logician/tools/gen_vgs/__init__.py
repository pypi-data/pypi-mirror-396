from pathlib import Path
from typing import cast

import jinja2
from devtools import pformat
from langchain.chat_models import BaseChatModel
from langsmith import traceable
from pydantic import BaseModel, Field

from ...base import (
    RawVerifyReq,
    VerifyReqData,
)

curr_dir = Path(__file__).parent
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(curr_dir))
code_to_raw_template = jinja_env.get_template("code_to_raw.jinja")
raw_to_verify_req_template = jinja_env.get_template("raw_to_verify_req.jinja")


class RawVerifyReqs(BaseModel):
    """
    List of verification statements. It looks like this:

    ```
    [
        {
            "src_func_name": "f",
            "iml_func_name": "f",
            "description": "Verify this function returns a number no less than 10",
            "logical_statement": "for all x in f(x) >= 10",
        },
        {
            "src_func_name": "g",
            "iml_func_name": "g",
            "description": "Check that this function returns a positive number",
            "logical_statement": "for all x in g(x) > 0",
        },
    ]
    ```
    """

    raw_verify_reqs: list[RawVerifyReq] = Field(
        ..., description="List of verification statements"
    )

    def __repr__(self):
        return pformat(self)


@traceable
async def code_to_raw_verify_req(
    src_lang: str,
    src_code: str,
    iml_code: str,
    description: str | None,
    llm: BaseChatModel,
) -> list[RawVerifyReq]:
    """Extract verification statements from description or comments in the
    source code."""

    raw_verify_reqs = await llm.with_structured_output(RawVerifyReqs).ainvoke(
        [
            code_to_raw_template.render(
                src_lang=src_lang,
                src_code=src_code,
                iml_code=iml_code,
                context_on_src_iml_correspondence=CONTEXT_ON_SRC_IML_CORRESPONDENCE,
                description=description,
            )
        ]
    )
    raw_verify_reqs = cast(RawVerifyReqs, raw_verify_reqs)
    return raw_verify_reqs.raw_verify_reqs


@traceable
async def raw_to_verify_req(
    llm: BaseChatModel,
    rvq: RawVerifyReq,
    iml_code: str,
    last_iml_query: str | None = None,
    last_error_msg: str | None = None,
) -> VerifyReqData:
    """Encode the verification statement into lambda functions in IML code."""
    func_names_str = ", ".join(rvq.iml_func_names)
    description = rvq.description
    logical_statement = rvq.logical_statement

    msg = raw_to_verify_req_template.render(
        iml_code=iml_code,
        func_names=func_names_str,
        description=description,
        logical_statement=logical_statement,
        last_iml_query=last_iml_query,
        last_error_msg=last_error_msg,
    )
    verify_src = await llm.with_structured_output(VerifyReqData).ainvoke([msg])
    verify_src = cast(VerifyReqData, verify_src)
    return verify_src


CONTEXT_ON_SRC_IML_CORRESPONDENCE = """IML (Imandra Modeling Language) is a formalized \
subset of OCaml designed for automated reasoning and formal verification. When working \
with IML, we create a formal model that corresponds to the original source code. This \
model preserves the core logic and behavior while adding mathematical rigor.

The correspondence between source code and IML is typically one-to-one at the function \
level - each important function in the source has a corresponding function in IML. \
This parallel structure allows us to reason about and verify properties of the \
original code through analysis of its formal IML model."""


RAW_TO_VERIFY_REQ_EXAMPLES: list[tuple[RawVerifyReq, VerifyReqData]] = [
    (
        RawVerifyReq(
            src_func_names=["calc_sum"],
            iml_func_names=["calc_sum"],
            description="Verify this function returns a number no less than 10",
            logical_statement="for all x, calc_sum(x) >= 10",
        ),
        VerifyReqData(predicate="fun x -> calc_sum x >= 10", kind="verify"),
    ),
    (
        RawVerifyReq(
            src_func_names=["check_legal", "property_1"],
            iml_func_names=["check_legal", "property_1"],
            description="Check that property_1 holds for all legal inputs",
            logical_statement="for all x, check_legal(x) ==> property_1(x)",
        ),
        VerifyReqData(
            predicate="fun x -> check_legal x ==> property_1 x", kind="verify"
        ),
    ),
    (
        RawVerifyReq(
            src_func_names=["safe_transform"],
            iml_func_names=["safe_transform"],
            description="""Check that a transformation preserves a property for \
any non-negative parameter value""",
            logical_statement="""for all state where state.value_a = 10 \
and state.value_b = 10 and state.parameter >= 0, safe_transform(state).value_a >= 0""",
        ),
        VerifyReqData(
            predicate="""fun state ->
  state.value_a = 10 &&
  state.value_b = 10 &&
  state.parameter >= 0
  ==>
  let state' = safe_transform state in
  state'.value_a >= 0""",
            kind="verify",
        ),
    ),
    (
        RawVerifyReq(
            src_func_names=["process_data", "validate_input", "compute_output"],
            iml_func_names=["process_data", "validate_input", "compute_output"],
            description="""Check that for valid inputs meeting a threshold condition, \
a multi-step process preserves a critical invariant""",
            logical_statement="""for all data where validate_input(data) \
and data.size < data.capacity, let output = compute_output(data) in \
process_data(data, output).integrity > 0""",
        ),
        VerifyReqData(
            predicate="""fun data ->
  validate_input data &&
  data.size < data.capacity
  ==>
  let output = compute_output data in
  let processed = process_data data output in
  processed.integrity > 0""",
            kind="verify",
        ),
    ),
    (
        RawVerifyReq(
            src_func_names=["valid_input", "process", "has_error"],
            iml_func_names=["valid_input", "process", "has_error"],
            description="Check that processing valid inputs never results in errors",
            logical_statement="""for all x, valid_input(x) ==> \
not(has_error(process(x)))""",
        ),
        VerifyReqData(
            predicate="fun x -> valid_input x ==> not (has_error (process x))",
            kind="verify",
        ),
    ),
    (
        RawVerifyReq(
            src_func_names=["is_target_state", "apply_transition", "apply_actions"],
            iml_func_names=["is_target_state", "apply_transition", "apply_actions"],
            description="""Prove that there exists a solution, which is a sequence of \
actions, that leads from the initial state to the target state""",
            logical_statement="""There exists a sequence of actions such that \
is_target_state(apply_actions(init_state, actions)) is true""",
        ),
        VerifyReqData(
            predicate="""fun actions ->
  let state = apply_actions init_state actions in
  is_target_state state""",
            kind="instance",
        ),
    ),
]

RAW_TO_VERIFY_REQ_EXAMPLES_STR = "\n\n".join(
    [
        f"""<example>
<input>
function names: {input.iml_func_names}
description: {input.description}
logical statement: {input.logical_statement}
</input>
<output>
{output.model_dump_json()}
</output>
</example>"""
        for (input, output) in RAW_TO_VERIFY_REQ_EXAMPLES
    ]
)
