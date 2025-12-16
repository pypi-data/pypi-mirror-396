import asyncio
import json
import re
from functools import reduce
from typing import Any

from google.protobuf.json_format import MessageToDict
from langchain.chat_models.base import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, TypeAdapter, field_validator
from pydantic_ai import format_as_xml

from agents.code_logician.reasoner.nodes.utils import context_on_src_iml_correspondence
from utils.imandra.imandrax.async_client import (
    AsyncClient,
    decompose,
    eval_src,
)
from utils.imandra.imandrax.proto_models.simple_api import (
    DecomposeRes,
    TypecheckRes,
)
from utils.llm import (
    anthropic_mark_cache_control,
    get_llm,
    support_anthropic_prompt_caching,
)
from utils.lsp.server import SyncCLLanguageServer


class PyTestGenerationError(Exception):
    """Error during the generation of Python tests."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def get_py_func_signature(
    src_code: str,
    func_name: str,
) -> str:
    lsp = SyncCLLanguageServer()

    # Get the hover information of the function
    with lsp.start_server():
        symbols: list[dict[str, Any]] = lsp.request_document_symbols(contents=src_code)
        hovers: dict[str, dict[str, Any]] = {}
        for sym in symbols:
            if sym["kind"] != 12:
                continue  # not function
            if sym["name"] != func_name:
                continue  # not the function we want
            hovers[sym["name"]] = lsp.request_hover(
                contents=src_code,
                line=sym["selectionRange"]["start"]["line"],
                column=sym["selectionRange"]["start"]["character"],
            )
    hover = hovers.get(func_name)
    if not hover:
        raise PyTestGenerationError(
            f"Cannot find the function `{func_name}` in the code."
        )
    hover = hover["contents"]["value"]

    # Extract the function signature from hover information
    sig_pattern = r"```[\w-]*\n(.*?)\n```"
    match = re.search(sig_pattern, hover, re.DOTALL)
    if not match:
        raise PyTestGenerationError(
            f"Cannot parse function signature of `{func_name}` from the hover "
            f"information. {hover}"
        )
    type_sig = match.group(1)
    return type_sig


async def get_iml_func_signature(
    imandrax_client: AsyncClient,
    iml_code: str,
    func_name: str,
) -> str:
    typecheck_res = await imandrax_client.typecheck(iml_code)
    typecheck_res = TypecheckRes.model_validate(MessageToDict(typecheck_res))
    iml_type = [it for it in typecheck_res.types if it.name == func_name]
    if not iml_type:
        raise PyTestGenerationError(
            f"Cannot find the type information of `{func_name}` in IML code."
        )
    type_sig: str = iml_type[0].ty
    return type_sig


class PythonTestCase(BaseModel):
    """A test case in Python.
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


class PythonTestCases(BaseModel):
    """A list of test cases in Python.

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

    test_cases: list[PythonTestCase] = Field(description="the test cases")


gen_py_test_sys_prompt = f"""<context_on_source_iml_correspondence>
{context_on_src_iml_correspondence}
</context_on_source_iml_correspondence>

Now we have some test cases for a function in IML. Each test case consists of \
a dictionary for the function's arguments and the expected output of the \
function.

<task>
The task is to utilize these test cases in IML to generate test cases for the \
corresponding function in Python.

The information you will receive includes: 
- The test cases in IML. Each test case is a dictionary for the function's arguments \
  and the expected output of the function.
- The name and type signature of the function in IML and Python.
- The complete source code of the function in IML and Python.

Notes:
- If names of the arguments in IML and Python \
  do not match. You need to map the arguments correctly.
- One tricky part is matching the types between IML and Python. Sometimes we have \
  ADTs in IML, and we need to map them to the corresponding types (most of time, \
  they are dataclass) in Python.
</task>
"""


# TODO: few-shot examples


gen_py_test_input_prompt_1 = """<input>
<iml_code>
{iml_code}
</iml_code>

<py_code>
{py_code}
</py_code>

<iml_func>
name: {iml_func_name}
type: {iml_type}
</iml_func>

<py_func>
name: {py_func_name}
type: {py_type}
</py_func>"""


gen_py_test_input_prompt_2 = """<test_cases>
{test_cases}
</test_cases>
</input>"""


async def async_gen_py_tests(
    py_code: str,
    iml_code: str,
    py_func_name: str,
    iml_func_name: str,
    imandrax_client: AsyncClient,
    llm: BaseChatModel | None = None,
    decompose_res: DecomposeRes | None = None,
    fallback: bool = True,
) -> dict[str, list[dict]]:
    if llm is None:
        llm = get_llm(use_case="code")

    if decompose_res is None:
        await eval_src(imandrax_client, iml_code)
        decompose_res: DecomposeRes = await decompose(
            imandrax_client, iml_func_name, ctx_simp=True
        )

    iml_test_cases: list[dict] = decompose_res.iml_test_cases

    res = {
        "iml": iml_test_cases,
    }

    try:
        if len(iml_test_cases) > 200:
            raise PyTestGenerationError(
                f"Too many regions generated in IML ({len(iml_test_cases)} > 200). "
                "For large numbers of regions, please use ImandraX directly via the "
                "`imandrax-api` package or the `ImandraX` VSCode extension."
            )

        # Get type of the Python function using LSP
        py_type = get_py_func_signature(py_code, py_func_name)

        # Get type of the IML function
        iml_type = await get_iml_func_signature(
            imandrax_client, iml_code, iml_func_name
        )

        # Transform the IML values into Python values
        fixed_msgs = [
            SystemMessage(content=gen_py_test_sys_prompt),
            HumanMessage(
                content=gen_py_test_input_prompt_1.format(
                    iml_code=iml_code,
                    py_code=py_code,
                    iml_func_name=iml_func_name,
                    iml_type=iml_type,
                    py_func_name=py_func_name,
                    py_type=py_type,
                )
            ),
        ]
        if support_anthropic_prompt_caching(llm):
            fixed_msgs[0] = anthropic_mark_cache_control(fixed_msgs[0])
            fixed_msgs[1] = anthropic_mark_cache_control(fixed_msgs[1])

        async def gen_for_batch(batch: list[dict]) -> list[PythonTestCase]:
            msgs = fixed_msgs.copy()
            msgs.append(
                HumanMessage(
                    content=gen_py_test_input_prompt_2.format(
                        test_cases=format_as_xml(
                            batch, item_tag="test_case", root_tag="test_cases"
                        ),
                    )
                )
            )
            res: PythonTestCases = await llm.with_structured_output(
                PythonTestCases
            ).ainvoke(msgs)
            return res.test_cases

        batches = [
            iml_test_cases[i : i + 10] for i in range(0, len(iml_test_cases), 10)
        ]
        # trigger prompt cache
        gen_py_test_cases = await gen_for_batch(batches[0])

        if len(batches) > 1:
            _gen_py_test_cases = await asyncio.gather(
                *[gen_for_batch(batch) for batch in batches[1:]]
            )
            _gen_py_test_cases = reduce(list.__add__, _gen_py_test_cases, [])
            gen_py_test_cases.extend(_gen_py_test_cases)

        res["py"] = TypeAdapter(list[PythonTestCase]).dump_python(gen_py_test_cases)
        return res

    except PyTestGenerationError as e:
        err_msg = f"Error generating Python tests: {e}\n"
        err_msg += "Fallback to using the original IML values."
        print(err_msg)
        if fallback:
            return res
        else:
            raise PyTestGenerationError(err_msg) from e
