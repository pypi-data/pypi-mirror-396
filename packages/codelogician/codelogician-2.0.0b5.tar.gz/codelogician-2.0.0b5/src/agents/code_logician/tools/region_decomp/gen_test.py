import asyncio
import json
import re
from functools import reduce
from typing import Any, cast

import structlog
from imandrax_api import AsyncClient  # ty:  ignore[possibly-missing-import]
from jinja2 import Template
from langchain.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import traceable
from multilspy import multilspy_types
from multilspy.lsp_protocol_handler import lsp_types as LSPTypes  # noqa: N812
from pydantic import BaseModel, Field, TypeAdapter, field_validator
from pydantic_ai import format_as_xml

from utils.imandra.imandrax.async_client import typecheck
from utils.imandra.imandrax.proto_models.simple_api import DecomposeRes, TypecheckRes
from utils.llm import anthropic_mark_cache_control, support_anthropic_prompt_caching
from utils.lsp.server import SyncCLLanguageServer

from ..gen_vgs import CONTEXT_ON_SRC_IML_CORRESPONDENCE

logger = structlog.get_logger(__name__)

gen_py_test_sys_prompt = f"""<context_on_source_iml_correspondence>
{CONTEXT_ON_SRC_IML_CORRESPONDENCE}
</context_on_source_iml_correspondence>

Now we have some test cases for a function in IML. Each test case consists of \
a dictionary for the function's arguments and the expected output of the \
function.

<task>
The task is to utilize these test cases in IML to generate test cases for the \
corresponding function in source language.

The information you will receive includes:
- The test cases in IML. Each test case is a dictionary for the function's arguments \
  and the expected output of the function.
- The name and type signature of the function in IML and source language.
- The complete source code of the function in IML and source language.

Notes:
- If names of the arguments in IML and source language \
  do not match. You need to map the arguments correctly.
- One tricky part is matching the types between IML and source language. Sometimes we \
  have ADTs in IML, and we need to map them to the corresponding types in source \
  language, for example, in Python, we might use dataclasses to represent ADTs.
- When generating multiple test cases in one batch, you need to make sure that the \
  order is preserved.
</task>
"""


# TODO: few-shot examples


gen_test_input_prompt_1: Template = Template("""\
<input>
<iml_code>
{{ iml_code }}
</iml_code>

<src_code_in>
```{{ src_lang }}
{{ src_code }}
```
</src_code_in>

<iml_function_for_test_generation>
name: {{ iml_func_name }}
type: {{ iml_type }}
</iml_function_for_test_generation>

<src_function_for_test_generation>
name: {{ src_func_name }}\
{% if src_type %}type: {{ \nsrc_type\n }}{% endif %}
</src_function_for_test_generation>""")


gen_test_input_prompt_2 = """<test_cases>
{test_cases}
</test_cases>
</input>"""


class TestGenerationError(Exception):
    """Error during the generation of test cases."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class SrcTestCase(BaseModel):
    """A test case in source language.
    Example1:
        {
            "args": {"x": "1", "y": "2"},
            "expected_output": "3"
        }
    Example2:
        {
            "args": {"input": "hello"},
            "expected_output": "HELLO"
        }
    Example3:
        {
            "args": {"data": {"name": "John", "age": 30}},
            "expected_output": "True"
        }
    """

    args: dict[str, str] = Field(description="the arguments of the test case")
    expected_output: str = Field(description="the expected output of the test case")

    @field_validator("args", mode="before")
    @classmethod
    def validate_args(cls, v: Any) -> Any:
        """If values of the args dicts are not str, convert them to json strings."""
        if isinstance(v, dict) and any(
            map(lambda x: not isinstance(x, str), v.values())
        ):
            return {
                k: json.dumps(v) if not isinstance(v, str) else v for k, v in v.items()
            }
        return v


class SrcTestCases(BaseModel):
    """A list of test cases in source language.

    Example:
        [
            {
                "args": {"x": "1", "y": "2"},
                "expected_output": "3"
            },
            {
                "args": {"input": "hello"},
                "expected_output": "HELLO"
            },
            {
                "args": {"data": {"name": "John", "age": 30}},
                "expected_output": "True"
            }
        ]
    """

    test_cases: list[SrcTestCase] = Field(description="the test cases")


@traceable
def get_py_func_signature(
    src_code: str,
    func_name: str,
) -> str:
    """Get the type signature of a Python function."""
    lsp = SyncCLLanguageServer()

    # Get the hover information of the function
    with lsp.start_server():
        symbols: list[LSPTypes.DocumentSymbol] = lsp.request_document_symbols(
            contents=src_code
        )
        hovers: dict[str, multilspy_types.Hover] = {}
        for sym in symbols:
            if sym["kind"] != 12:
                continue  # not function
            if sym["name"] != func_name:
                continue  # not the function we want
            hover_result = lsp.request_hover(
                contents=src_code,
                line=sym["selectionRange"]["start"]["line"],
                column=sym["selectionRange"]["start"]["character"],
            )
            if hover_result is not None:
                hovers[sym["name"]] = hover_result
    hover = hovers.get(func_name)
    if not hover:
        raise TestGenerationError(
            f"Cannot find the function `{func_name}` in the code."
        )
    hover_contents = hover["contents"]
    # Extract value from MarkupContent
    if isinstance(hover_contents, dict) and "value" in hover_contents:
        hover_text = hover_contents["value"]
    else:
        hover_text = str(hover_contents)

    # Extract the function signature from hover information
    sig_pattern = r"```[\w-]*\n(.*?)\n```"
    match = re.search(sig_pattern, hover_text, re.DOTALL)
    if not match:
        raise TestGenerationError(
            f"Cannot parse function signature of `{func_name}` from the hover "
            f"information. {hover_text}"
        )
    type_sig = match.group(1)
    return type_sig


@traceable
async def get_iml_func_signature(
    imandrax_client: AsyncClient,
    iml_code: str,
    func_name: str,
) -> str:
    """Get the type signature of an IML function."""
    typecheck_res: TypecheckRes = await typecheck(imandrax_client, iml_code)
    iml_type = [it for it in typecheck_res.types if it.name == func_name]
    if not iml_type:
        raise TestGenerationError(
            f"Cannot find the type information of `{func_name}` in IML code."
        )
    type_sig: str = iml_type[0].ty
    return type_sig


async def async_gen_tests(
    src_lang: str,
    src_code: str,
    iml_code: str,
    src_func_name: str,
    iml_func_name: str,
    llm: BaseChatModel,
    imandrax_client: AsyncClient,
    decompose_res: DecomposeRes,
    include_docstr: bool = True,
    fallback: bool = True,
) -> dict[str, list[dict]]:
    """Generate test cases for a specific region decomp result.

    Args:
        include_docstr: Whether to include constraints and invariants as docstrings \
            in the test cases.
    """
    iml_test_cases: list[dict] = decompose_res.iml_test_cases

    res = {
        "iml": iml_test_cases,
    }

    docstrs: list[str] = decompose_res.test_docstrs

    try:
        if len(iml_test_cases) > 200:
            raise TestGenerationError(
                f"Too many regions generated in IML ({len(iml_test_cases)} > 200). "
                "For large numbers of regions, please use ImandraX directly via the "
                "`imandrax-api` package or the `ImandraX` VSCode extension."
            )

        # Get type of the IML function
        iml_type = await get_iml_func_signature(
            imandrax_client, iml_code, iml_func_name
        )

        # Get type of the source function using LSP
        if src_lang == "python":
            try:
                src_func_type = get_py_func_signature(src_code, src_func_name)
            except Exception as e:
                logger.error(
                    "source_function_type_error",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                src_func_type = None
        else:
            src_func_type = None

        # Transform IML values into values in source language
        ## Messages
        fixed_msgs = [
            SystemMessage(content=gen_py_test_sys_prompt),
            HumanMessage(
                content=gen_test_input_prompt_1.render(
                    iml_code=iml_code,
                    src_code=src_code,
                    src_lang=src_lang,
                    iml_func_name=iml_func_name,
                    iml_type=iml_type,
                    src_func_name=src_func_name,
                    src_type=src_func_type,
                )
            ),
        ]
        if support_anthropic_prompt_caching(llm):
            fixed_msgs[0] = anthropic_mark_cache_control(fixed_msgs[0])
            fixed_msgs[1] = anthropic_mark_cache_control(fixed_msgs[1])

        ## Generate test cases by batch
        async def gen_by_batch(batch: list[dict]) -> list[SrcTestCase]:
            msgs = fixed_msgs.copy()
            msgs.append(
                HumanMessage(
                    content=gen_test_input_prompt_2.format(
                        test_cases=format_as_xml(
                            batch, item_tag="test_case", root_tag="test_cases"
                        ),
                    )
                )
            )
            res = await llm.with_structured_output(
                SrcTestCases,
                method="function_calling",
            ).ainvoke(msgs)
            res = cast(SrcTestCases, res)
            return res.test_cases

        batches = [
            iml_test_cases[i : i + 10] for i in range(0, len(iml_test_cases), 10)
        ]
        # trigger prompt cache
        gen_src_test_cases = await gen_by_batch(batches[0])

        if len(batches) > 1:
            _gen_src_test_cases = await asyncio.gather(
                *[gen_by_batch(batch) for batch in batches[1:]]
            )
            _gen_src_test_cases = reduce(list.__add__, _gen_src_test_cases, [])
            gen_src_test_cases.extend(_gen_src_test_cases)

        res["src"] = TypeAdapter(list[SrcTestCase]).dump_python(gen_src_test_cases)
        if include_docstr:
            for i, docstr in enumerate(docstrs):
                res["src"][i]["docstr"] = docstr
        return res

    except TestGenerationError as e:
        logger.error(
            "test_generation_error",
            error=str(e),
            error_type=type(e).__name__,
            fallback_mode="exporting_original_iml_only",
        )
        if fallback:
            if include_docstr:
                for i, docstr in enumerate(docstrs):
                    res["iml"][i]["docstr"] = docstr
            return res
        else:
            raise TestGenerationError(
                f"Error generating test cases: {e}\n"
                "Exporting only the original IML test cases."
            ) from e
