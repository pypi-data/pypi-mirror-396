"""
Verification extraction:
- Get verfication specifications from (1) comments in the code, (2) human messages
or (3) source code.
- Transform informal statements into more formal logical statements.
- These logical statements will be later transformed to IML verification code.
"""

from typing import Literal

from devtools import pformat
from langchain.chat_models.base import BaseChatModel
from langchain_core.prompts import HumanMessagePromptTemplate
from pydantic import BaseModel, Field

from agents.code_logician.reasoner.base import (
    PartialDecomposeReq,  # noqa: F401
    PartialVerifyReq,
    RawDecomposeReq,
    RawVerifyReq,
)
from agents.code_logician.reasoner.nodes.utils import context_on_src_iml_correspondence


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


class RawDecomposeReqs(BaseModel):
    raw_decompose_reqs: list[RawDecomposeReq] = Field(
        description="List of functions to decompose in source code and their "
        "corresponding functions in IML"
    )

    def __repr__(self):
        return pformat(self)


extract_verify_req_from_comments_prompt = HumanMessagePromptTemplate.from_template(
    """<IML_code>
```
{iml_code}
```
</IML_code>

Source code:
```
{src_code}
```


Provided above are a pair of source code and IML code. \
<context_on_the_correspondence_between_source_code_and_iml_code>
{context_on_src_iml_correspondence}
</context_on_the_correspondence_between_source_code_and_iml_code>

<task>
User might request to verify properties of the source code in the comments. Your task \
is to identify these requests in natural language and transform them into logical \
statements.

<task_caveats>
- Not all comments are related to the verification. Looking for comments that
have the following keywords: `verify`, `check`, `assert`, `ensure`, `guarantee`.
- Not all logical statements are user requests. Some are just descriptions of the code.
- A single logical statement might involve multiple functions.
- "decompose" is not a related keyword.
- Solution finding is also a kind of verification. It is equivalent to verifying \
  that there exists a state satisfying some property.
- Answer as per the provided JSON format.
</task_caveats>

<example>
Input:
```
# verify that the function always returns a number no less than 10
def f(x):
    ...
```
Output:
```
{{
    "src_func_names": ["f"],
    "iml_func_names": ["f"],
    "description": "Verify that the function always returns a number no less than 10",
    "logical_statement": "for all x in f(x) >= 10",
}}
```
</example>

<example>
Input:
```
def check_legal(x) -> bool:
    ...

# check that if inputs are legal, then the property_1 always holds
def property_1(x) -> bool:
    ...
```
Output:
```
{{
    "src_func_names": ["check_legal", "property_1"],
    "iml_func_names": ["check_legal", "property_1"],
    "description": "Check that if inputs are legal, then the property_1 always holds",
    "logical_statement": "for all x in check_legal(x) ==> property_1(x)",
}}
```
</example>

<example>
Input:
```
def is_target_state(state) -> bool:
    ...
def apply_transition(state, action) -> State:
    ...
def apply_actions(state, actions) -> State:
    ...

# Find a solution that starts from the initial state and ends with the target state
```
Output:
```
{{
    "src_func_names": ["is_target_state", "apply_transition", "apply_actions"],
    "iml_func_names": ["is_target_state", "apply_transition", "apply_actions"],
    "description": "Verify that there exists a solution, which is a sequence of \
actions, that leads from the initial state to the target state",
    "logical_statement": "There exists a sequence of actions such that \
is_target_state(apply_actions(init_state, actions)) is true",
}}
```
</example>

</task>
"""
)

extract_verify_req_from_msg_prompt = HumanMessagePromptTemplate.from_template(
    """IML code:
```
{iml_code}
```

Source code:
```
{src_code}
```


Provided above are a pair of source code and IML code. \
{context_on_src_iml_correspondence}

Your task is to extract the logical statements about functions in the source code \
based on the human message.

Human message:
```
{message}
```

Answer as per the provided JSON format.
"""
)

suggest_verify_req_prompt = HumanMessagePromptTemplate.from_template(
    """
<IML_code>
```
{iml_code}
```
</IML_code>

<source_code>
```
{src_code}
```
</source_code>


Provided above are a pair of source code and IML code. \
{context_on_src_iml_correspondence}

Your task is to suggest the logical statements about functions that could be verified \
in the source code.

Answer as per the provided JSON format.
"""
)

_verify_examples = [
    (
        RawVerifyReq(
            src_func_names=["calc_sum"],
            iml_func_names=["calc_sum"],
            description="Verify this function returns a number no less than 10",
            logical_statement="for all x, calc_sum(x) >= 10",
        ),
        PartialVerifyReq(predicate="fun x -> calc_sum x >= 10", kind="verify"),
    ),
    (
        RawVerifyReq(
            src_func_names=["check_legal", "property_1"],
            iml_func_names=["check_legal", "property_1"],
            description="Check that property_1 holds for all legal inputs",
            logical_statement="for all x, check_legal(x) ==> property_1(x)",
        ),
        PartialVerifyReq(
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
        PartialVerifyReq(
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
        PartialVerifyReq(
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
        PartialVerifyReq(
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
        PartialVerifyReq(
            predicate="""fun actions ->
  let state = apply_actions init_state actions in
  is_target_state state""",
            kind="instance",
        ),
    ),
]

gen_iml_verify_req_prompt = HumanMessagePromptTemplate.from_template(
    """Your task is to convert the logical statement about some function to IML code, \
which is a formalized Higher-Order subset of OCaml featuring automated reasoning. \
You'll express these logical statements using lambda functions and functional \
programming patterns.

## Key Concepts to Apply:
- Express universal quantification and existential quantification using lambda \
abstractions.
- Translate logical implications into appropriate operators (==>)
- Use let-bindings for intermediate computation results
- Handle complex record structures and type constraints

## Examples:

{examples}

<IML_code>
```
{iml_code}
```
</IML_code>

Now, convert the following logical statement into IML code:
<input>
function names: {func_names}
description: {description}
logical statement: {logical_statement}
</input>
""",
    partial_variables={
        "examples": "\n\n".join(
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
                for (input, output) in _verify_examples
            ]
        )
    },
)

re_gen_iml_verify_req_prompt = HumanMessagePromptTemplate.from_template(
    gen_iml_verify_req_prompt.prompt.template
    + "\n\n"
    + """Here are the incorrect IML code and the error message from previous attempt:
```
{last_iml_query}
```
{last_error_msg}

Take these into account when generating the correct IML code.
""",
    partial_variables={
        "examples": "\n\n".join(
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
                for (input, output) in _verify_examples
            ]
        )
    },
)


async def extract_raw_verify_reqs(
    llm: BaseChatModel, src_code: str, iml_code: str
) -> list[RawVerifyReq]:
    """Extract verification statements from:

    (1) comments in the source code
    # TODO:
    (2) human messages
    (3) source code only

    Paired IML code is provided as we need the function names in IML.
    """

    vss = await llm.with_structured_output(RawVerifyReqs).ainvoke(
        [
            extract_verify_req_from_comments_prompt.format(
                src_code=src_code,
                iml_code=iml_code,
                context_on_src_iml_correspondence=context_on_src_iml_correspondence,
            )
        ]
    )
    return vss.raw_verify_reqs


async def gen_partial_verify_req(
    llm: BaseChatModel,
    rvq: RawVerifyReq,
    iml_code: str,
    last_iml_query: str | None = None,
    last_error_msg: str | None = None,
) -> PartialVerifyReq:
    """Encode the verification statement into lambda functions in IML code."""
    llmws = llm.with_structured_output(PartialVerifyReq)
    if last_iml_query is None and last_error_msg is None:
        msg = gen_iml_verify_req_prompt.format(
            iml_code=iml_code,
            func_names=rvq.iml_func_names,
            description=rvq.description,
            logical_statement=rvq.logical_statement,
        )
    else:
        msg = re_gen_iml_verify_req_prompt.format(
            iml_code=iml_code,
            func_names=rvq.iml_func_names,
            description=rvq.description,
            logical_statement=rvq.logical_statement,
            last_iml_query=last_iml_query,
            last_error_msg=last_error_msg,
        )
    verify_src = await llmws.ainvoke([msg])
    return verify_src


# ---

extract_decomp_req_intro = f"""<source_code>
```
{{src_code}}
```
</source_code>

<IML_code>
```
{{iml_code}}
```
</IML_code>

Provided above are a pair of source code and IML code. \
<context_on_the_correspondence_between_source_code_and_iml_code>
{context_on_src_iml_correspondence}
</context_on_the_correspondence_between_source_code_and_iml_code>
"""


class MainFunctionNames(BaseModel):
    """
    The name of the main function in source code and its corresponding function in IML.

    Typically the final function name but not necessarily.
    """

    src_func_name: str = Field(description="name of the main function in source code")
    iml_func_name: str = Field(description="name of the main function in IML")

    def __repr__(self):
        return pformat(self)


extract_decomp_req_from_main_func_prompt = HumanMessagePromptTemplate.from_template(
    template=(
        extract_decomp_req_intro
        + """
<task>
Your task is to identify and extract the main function name in source code and its \
corresponding function in IML. The main function is typically:
- The final function that encapsulates the core logic
- The function that other functions help to implement
- The function that will be called by external code
- Often found at the bottom of the file after helper functions, but not necessarily

Both the function name in source code and its corresponding function in IML should be \
extracted.
</task>"""
    )
)

extract_decomp_req_from_comments_prompt = HumanMessagePromptTemplate.from_template(
    template=(
        extract_decomp_req_intro
        + """
<task>
Your task is to identify and extract the decomposition requests from the source code. \
Such comments start with keyword "decompose" and are located on top of \
the function to decompose. 

Both the function name in source code and its corresponding function in IML should be \
extracted.
</task>

Example:

{examples}

<notes>
- There might be multiple or no decomposition requests in the source code.
- Return an empty list if there are no decomposition requests.
- There might be other comments requesting for verifying properties. Ignore them.
- The function name in IML might be different from the function name in source code.
- Answer as per the provided JSON format.
</notes>
"""
    )
)

extract_decomp_req_from_comments_examples = """<example1>
Input:
```
# decompose this function
def f(x):
    ...
```
Output:
```
{
    "raw_decompose_req": "decompose this function",
    "src_func_name": "f",
    "iml_func_name": "f",
}
```
</example1>

<example2>
Input:
```
# decompose calc_sum
def calc_sum(x):
    ...
```
Output:
```
{
    "raw_decompose_req": "decompose calc_sum",
    "src_func_name": "calc_sum",
    "iml_func_name": "calc_sum",
}
```
</example2>
"""


async def extract_raw_decompose_reqs(
    llm: BaseChatModel,
    src_code: str,
    iml_code: str,
    method: Literal["main_function", "comments"] = "main_function",
) -> list[RawDecomposeReq]:
    """Extract decomposition statements from the source code."""
    match method:
        case "comments":
            dss: RawDecomposeReqs = await llm.with_structured_output(
                RawDecomposeReqs
            ).ainvoke(
                [
                    extract_decomp_req_from_comments_prompt.format(
                        src_code=src_code,
                        iml_code=iml_code,
                        examples=extract_decomp_req_from_comments_examples,
                    )
                ]
            )
            return dss.raw_decompose_reqs
        case "main_function":
            func_names: MainFunctionNames = await llm.with_structured_output(
                MainFunctionNames
            ).ainvoke(
                [
                    extract_decomp_req_from_main_func_prompt.format(
                        src_code=src_code,
                        iml_code=iml_code,
                    )
                ]
            )
            return [
                RawDecomposeReq(
                    description="Main function",
                    src_func_name=func_names.src_func_name,
                    iml_func_name=func_names.iml_func_name,
                )
            ]
        case _:
            raise ValueError(f"Invalid method: {method}")
