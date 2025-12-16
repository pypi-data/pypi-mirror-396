from __future__ import annotations

import textwrap

from imandrax_api import AsyncClient  # ty: ignore[possibly-missing-import]
from jinja2 import Template
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langsmith import traceable

from utils.fdb.fdb import FDB, FDBFormatter
from utils.imandra.imandrax.async_client import (
    decompose,
    verify_src,
    verify_src_catching_internal_error,
)
from utils.imandra.imandrax.proto_models import (
    DecomposeRes,
    VerifyRes,
)
from utils.llm import anthropic_mark_cache_control

from ...imandrax_model_utils import eval_res_errors_to_llm_context
from ..context import (
    ConversionFailureInfo,
    ConversionSourceInfo,
)
from ..dependency import FormalizationDependency, ModuleInfo
from ..formalization_state import FormalizationState
from ..region_decomp import DecomposeReqData
from ..vg import VerifyReqData
from .iml import parse_iml

__all__ = [
    "cfi_summary",
    "cfi_to_messages",
    "csi_summary",
    "csi_to_llm_context",
    "csi_to_messages",
    "decompose_req_data_post",
    "get_iml_model_with_dependencies",
    "parse_iml",
    "verify_req_data_post",
]

# =====
# Context
# =====


def csi_summary(csi: ConversionSourceInfo) -> dict[str, int]:
    return {
        "meta_eg": len(csi.meta_eg),
        "relevant_eg": len(csi.relevant_eg),
        "iml_api_refs": len(csi.iml_api_refs),
        "missing_func": len(csi.missing_func) if csi.missing_func else 0,
    }


def csi_to_llm_context(csi: ConversionSourceInfo) -> str:
    """Format to a string for LLM context"""
    s = ""
    s += FDBFormatter.format_conversion_pair(csi.meta_eg)
    s += "Relevant IML API References:\n\n"
    s += FDBFormatter.format_iml_api_reference(csi.iml_api_refs)

    if csi.missing_func:
        missing_func_s = FDBFormatter.format_missing_func(csi.missing_func)
        s += "\n\nMissing functions in the source code and their IML counterparts:\n"
        s += missing_func_s
    return s


def csi_to_messages(
    csi: ConversionSourceInfo, cache_prompt: bool = False
) -> list[BaseMessage]:
    """Format to a list of messages

    - Language-specific meta examples (QAs between human and AI)
    - Relevant examples (QAs between human and AI)
    - Context messages (Human message)

    Args:
        cache_prompt: Whether to using prompt caching for the meta examples
    """

    # Language-specific meta examples
    lang_meta_eg_msgs = []
    if csi.meta_eg:
        for eg in csi.meta_eg:
            eg: FDB.ConversionPair
            lang_meta_eg_msgs.extend(
                [
                    HumanMessage(content=eg.src_code),
                    AIMessage(content=eg.iml_code),
                ]
            )

    # Relevant examples
    relevant_egs_msgs = []
    if csi.relevant_eg:
        for eg in csi.relevant_eg:
            eg: FDB.ConversionPair
            relevant_egs_msgs.extend(
                [
                    HumanMessage(content=eg.src_code),
                    AIMessage(content=eg.iml_code),
                ]
            )

    ctx_s = ""

    # Context messages (IML API Reference and Missing functions)
    # IML API Reference
    if csi.iml_api_refs:
        ctx_s += "Some relevant IML API references:\n\n"
        ctx_s += FDBFormatter.format_iml_api_reference(csi.iml_api_refs)

    # Missing functions
    if csi.missing_func:
        ctx_s += (
            "\n\nMissing functions in the source code and their IML counterparts:\n"
        )
        ctx_s += FDBFormatter.format_missing_func(csi.missing_func)

    # User-injected context
    if csi.user_inject:
        ctx_s += "\n\nUser-injected context:\n"
        ctx_s += csi.user_inject

    if ctx_s:
        ctx_msg = HumanMessage(
            content=(
                "Here are some relevant context for the code that you are going to "
                "formalize:\n\n" + ctx_s
            )
        )
    else:
        ctx_msg = None

    if cache_prompt:
        lang_meta_eg_msgs[-1] = anthropic_mark_cache_control(lang_meta_eg_msgs[-1])

    return [
        *lang_meta_eg_msgs,
        *relevant_egs_msgs,
        *([ctx_msg] if ctx_msg else []),
    ]


def cfi_summary(cfi: ConversionFailureInfo) -> dict[str, int]:
    return {
        "sim_errs": len(cfi.sim_errs),
        "human_hint": 1 if cfi.human_hint else 0,
        "iml_api_refs": len(cfi.iml_api_refs),
        "missing_func": len(cfi.missing_func),
    }


def cfi_to_messages(cfi: ConversionFailureInfo) -> list[BaseMessage]:
    answer_msg = AIMessage(content=cfi.iml_code)
    s = ""
    s += "Your previous attempt has errors. \n\n"
    s += "Error in your previous IML code:\n"
    errors_llm_context = eval_res_errors_to_llm_context(cfi.eval_res)
    assert errors_llm_context is not None
    s += errors_llm_context
    if cfi.sim_errs:
        s += "\n\n"
        s += "Similar errors for your reference (might not be relevant):\n"
        s += FDBFormatter.format_error(cfi.sim_errs)
    if cfi.linting_errors:
        s += "\n\n"
        s += "Linting errors from static analysis (might not be relevant):\n"
        for i, linting_error in enumerate(cfi.linting_errors, 1):
            if i >= 5:
                # A maximum of 5 linting errors are shown
                break
            s += f"- linting error {i}:\n"
            s += linting_error.format_error_message()
    if cfi.iml_api_refs:
        s += "\n\n"
        s += "More relevant IML API references:\n"
        s += FDBFormatter.format_iml_api_reference(cfi.iml_api_refs)
    if cfi.human_hint:
        s += "\n\n"
        s += "Suggestions from human:\n"
        s += f"{cfi.human_hint}"
    if cfi.tool_calls:
        s += "\n\n"
        for i, tool_call_text in enumerate(cfi.tool_calls, 1):
            s += f"## Tool call {i}\n"
            s += tool_call_text
    error_msg = HumanMessage(content=s)
    return [answer_msg, error_msg]


# =====
# Dependency
# =====


def get_monolith_iml(dependencies: list[FormalizationDependency]) -> str:
    return mk_monolith_iml([fd.iml_module for fd in dependencies])


def format_dependencies_context(
    dependencies: list[FormalizationDependency],
    src_lang: str,
) -> str:
    iml_monolith = get_monolith_iml(dependencies)

    template = Template("""\
The module being formalized has the following dependencies:

## Dependencies (already formalized in IML)
{% for dep in dependencies %}
###  {{ loop.index }}. {{ dep.src_module.name }}
- Path: `{{ dep.src_module.relative_path }}`
- Source code:
```{{ src_lang }}
{{ dep.src_module.content }}
```
{% endfor %}

## Formalized dependencies, i.e, Available IML modules
```iml
{{ iml_monolith }}
```

## Instructions
- The dependencies of the source code are already formalized and provided as a \
monolith IML file.
- You can directly use the modules in the monolith without any import statements.
- Your code will be checked (compiled) together with the monolith.
- Dependencies are defined as modules so that you can use them directly for \
convenience. For your newly generated code, you are not required to wrap it in a \
module.
""")
    return template.render(
        dependencies=dependencies,
        src_lang=src_lang,
        iml_monolith=iml_monolith,
    )


def mk_monolith_iml(modules: list[ModuleInfo]) -> str:
    """
    Given a list of IML modules sorted by topological order (leaves to root), produce
    a monolith IML file content that:
        - define all the modules inline
        - no import statements
        - ready to be continued

    Args:
        modules: The modules to be included in the monolith, sorted by topological
        order.

    Returns:
        The monolith iml file content, ready to be continued.
    """
    mod_names = [module.name for module in modules]
    mod_contents = [
        textwrap.indent(module.content.rstrip("\n"), "    ") for module in modules
    ]
    template = Template(
        textwrap.dedent(
            """
            {% for name, content in mod_names_modules %}
            module {{ name }} = struct
            {{ content }}
            end
            {% endfor %}
            """
        ),
    )
    mono = template.render(mod_names_modules=zip(mod_names, mod_contents, strict=True))
    return format_empty_lines(mono)


def format_empty_lines(content: str) -> str:
    """Format the empty lines in the content.
    - No empty lines at the beginning of the file
    - Newline at the end of the file
    """
    content = content.strip()
    content = content.lstrip("\n")
    if not content.endswith("\n"):
        content += "\n"
    return content


# =====
# FormalizationState
# =====


@traceable
def get_iml_model_with_dependencies(fstate: FormalizationState) -> str:
    """Get the full IML code, including the monolith IML redefining the dependencies
    modules and the original IML code.
    """
    if fstate.iml_model is None:
        raise ValueError("IML code is required")
    if fstate.dependency:
        iml_dep = get_monolith_iml(fstate.dependency)
        full_iml = iml_dep + "\n" + fstate.iml_model.strip() + "\n"
    else:
        full_iml = fstate.iml_model
    return full_iml


# =====
# region_decomp
# =====


async def decompose_req_data_post(
    decompose_req_data: DecomposeReqData,
    imx_client: AsyncClient,
    catch_internal_error: bool = True,
) -> DecomposeRes:
    params = decompose_req_data.model_dump(by_alias=True)
    name = params.pop("name")
    decompose_res = await decompose(imx_client, name, **params)
    return decompose_res


# =====
# VG
# =====


async def verify_req_data_post(
    verify_req_data: VerifyReqData,
    imx_client: AsyncClient,
    catch_internal_error: bool = True,
) -> VerifyRes:
    """
    Post the verify request to ImandraX and return the result

    catch_internal_error:
        Whether internal error from ImandraX is caught and serialized to the error
        field of VerifyRes
    """

    # TODO: should we consider kind here?
    if catch_internal_error:
        imx_res = await verify_src_catching_internal_error(
            imx_client, verify_req_data.predicate
        )
    else:
        imx_res = await verify_src(imx_client, verify_req_data.predicate)
    return imx_res
