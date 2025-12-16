from typing import Literal, cast

import structlog
from langchain.chat_models import BaseChatModel
from langchain_core.prompts import HumanMessagePromptTemplate
from langsmith import traceable
from pydantic import BaseModel, Field

from ...base import RawDecomposeReq
from ..gen_vgs import CONTEXT_ON_SRC_IML_CORRESPONDENCE

logger = structlog.get_logger(__name__)


@traceable
async def gen_raw_decomp_reqs(
    llm: BaseChatModel,
    src_code: str,
    iml_code: str,
    method: Literal["main_function", "comments", "nat_lang_req"] = "comments",
    nat_lang_req: str | None = None,
) -> list[RawDecomposeReq]:
    """Extract decomposition statements from the source code."""

    # TODO: Make LLM do multiple-choice from top definitions
    class RawDecomposeReqs(BaseModel):
        raw_decompose_reqs: list[RawDecomposeReq] = Field(
            description="List of functions to decompose in source code and their "
            "corresponding functions in IML"
        )

    match method:
        case "nat_lang_req":
            dss = await llm.with_structured_output(RawDecomposeReqs).ainvoke(
                [
                    extract_decomp_req_from_nat_lang_req_prompt.format(
                        src_code=src_code,
                        iml_code=iml_code,
                        nat_lang_req=nat_lang_req,
                    )
                ]
            )
            dss = cast(RawDecomposeReqs, dss)
            return dss.raw_decompose_reqs

        case "comments":
            dss = await llm.with_structured_output(RawDecomposeReqs).ainvoke(
                [
                    extract_decomp_req_from_comments_prompt.format(
                        src_code=src_code,
                        iml_code=iml_code,
                        examples=extract_decomp_req_from_comments_examples,
                    )
                ]
            )
            dss = cast(RawDecomposeReqs, dss)
            return dss.raw_decompose_reqs

        case "main_function":

            class MainFunctionNames(BaseModel):
                """
                The name of the main function in source code and its corresponding
                function in IML.

                Typically the final function name but not necessarily.
                """

                src_func_name: str = Field(
                    description="name of the main function in source code"
                )
                iml_func_name: str = Field(
                    description="name of the main function in IML"
                )

            func_names = await llm.with_structured_output(MainFunctionNames).ainvoke(
                [
                    extract_decomp_req_from_main_func_prompt.format(
                        src_code=src_code,
                        iml_code=iml_code,
                    )
                ]
            )
            func_names = cast(MainFunctionNames, func_names)
            return [
                RawDecomposeReq(
                    description="Main function",
                    src_func_name=func_names.src_func_name,
                    iml_func_name=func_names.iml_func_name,
                )
            ]
        case _:
            raise AssertionError(f"Never: Invalid method {method}")


# TODO: use jinja template to consolidate the prompts (if else logic)


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
{CONTEXT_ON_SRC_IML_CORRESPONDENCE}
</context_on_the_correspondence_between_source_code_and_iml_code>
"""


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


extract_decomp_req_from_nat_lang_req_prompt = HumanMessagePromptTemplate.from_template(
    template=(
        extract_decomp_req_intro
        + """
<task>
Your task is to identify and extract the structured decomposition requests from \
the natural language description of decomposition requests.

Both the function name in source code and its corresponding function in IML should be \
extracted.
</task>

Example:
<example1>
Input:
<src_code>
```
def f(x):
    return x + 1

def g(x):
    return x + f(x)
```
</src_code>

<IML_code>
```
let f x = x + 1
let g x = x + f x
```
</IML_code>

<nat_lang_req>
I want to decompose the function `g`
</nat_lang_req>

Output:
```
{{
    "raw_decompose_req": "decompose g",
    "src_func_name": "g",
    "iml_func_name": "g",
}}
```
</example1>


<notes>
- The function name in IML might be slightly different from the function name in source
code.
- Answer as per the provided JSON format.
</notes>


{nat_lang_req}
"""
    )
)

extract_decomp_req_from_comments_prompt = HumanMessagePromptTemplate.from_template(
    template=(
        extract_decomp_req_intro
        + """
<task>
Your task is to identify and extract the decomposition requests from the comments in \
the source code. Such comments must satisfy the following conditions:
- Has keyword "decompose" or "generate test cases"
- Are located on top of the function to decompose

Once a comment satisfies the above conditions, both the function name in source code \
and its corresponding function in IML should be extracted.
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
