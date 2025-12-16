import re

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from agents.code_logician.base import (
    ConversionFailureInfo,
    ConversionSourceInfo,
    FormalizationDependency,
)
from agents.code_logician.base.model_utils import (
    cfi_to_messages,
    csi_to_messages,
    format_dependencies_context,
)
from utils.llm import (
    anthropic_mark_cache_control,
)

from .prompts import (
    formalization_caveats,
    iml_101,
    output_format_instruction,
    role_prompt,
)


def format_formalization_msgs(
    src_lang: str,
    src_code: str,
    src_info: ConversionSourceInfo,
    dependency: list[FormalizationDependency],
    failures_info: list[ConversionFailureInfo] | None = None,
    with_output_format_instruction: bool = True,
    cache_prompt: bool = False,
) -> list[BaseMessage]:
    """
    Prepare messages for conversion.

    Args:
        src_lang: Source language
        src_code: Source code
        src_info: Source info
        failures_info: Previous failures
        cache_prompt: Whether to cache the prompt

    Returns:
        The messages for the conversion.
        [
            Sys: IML 101 + lang agnostic meta examples (cache point)
            HAs?: lang-specific meta examples (cache point)
            HAs?: retrieved examples
            H: context message
            H?: dependency context
            H: source code
            AHs: previous formalization
        ]
    """
    # System message: IML 101 + lang agnostic meta examples
    sys_msg = SystemMessage(content=role_prompt + iml_101)
    if cache_prompt:
        sys_msg = anthropic_mark_cache_control(sys_msg)

    # Source info
    source_info_msgs = csi_to_messages(src_info, cache_prompt)

    # Dependency
    if dependency:
        dependency_msgs = [
            HumanMessage(content=format_dependencies_context(dependency, src_lang))
        ]
    else:
        dependency_msgs = []

    # Source code
    src_msg = HumanMessage(
        content=(
            f"<final_caveats>\n{formalization_caveats}\n</final_caveats>\n\n"
            f"<source_code_in>\n```{src_lang}\n{src_code}\n```\n</source_code_in>\n\n"
        )
    )

    # Previous formalization
    prev_f_msgs = []
    if failures_info:
        for f in failures_info:
            prev_f_msgs.extend(cfi_to_messages(f))

    output_format_instruction_msgs = []
    if with_output_format_instruction:
        output_format_instruction_msgs = [
            HumanMessage(content=output_format_instruction)
        ]

    return [
        sys_msg,
        *source_info_msgs,
        *dependency_msgs,
        src_msg,
        *prev_f_msgs,
        *output_format_instruction_msgs,
    ]


def strip_block_quote_and_add_newline(s: str) -> str:
    """
    Extract code from a markdown code block, ignoring surrounding text.

    Handles two cases:
    Case 1: Triple quotes on their own line (at start/end)
        ```iml
        code here
        ```
    Case 2: Text before/after the code block
        Here's the code:
        ```iml
        code here
        ```
        That's it!
    """

    lines = s.splitlines(keepends=True)

    # Case 1: Check if first/last lines are just triple quotes (with optional language)
    # First line should match: optional whitespace + ``` + optional language + optional
    # whitespace
    # Last line should match: optional whitespace + ``` + optional whitespace
    first_line_is_fence = len(lines) > 0 and re.match(r"^\s*```(?:iml)?\s*$", lines[0])
    last_line_is_fence = len(lines) > 0 and re.match(r"^\s*```\s*$", lines[-1])

    if first_line_is_fence and last_line_is_fence and len(lines) >= 2:
        # Case 1: Strip first and last lines that contain only triple quotes
        code = "".join(lines[1:-1])
    else:
        # Case 2: Use regex to find code block anywhere in the text
        # Match ```iml or just ``` followed by content until closing ```
        pattern = r"```(?:iml)?\s*\n(.*?)```"
        match = re.search(pattern, s, re.DOTALL)

        if match:
            # Extract the code content from the matched group
            code = match.group(1)
        else:
            # No code block found at all, return original stripped
            code = s.strip()

    # Ensure trailing newline
    if not code.endswith("\n"):
        code += "\n"

    return code
