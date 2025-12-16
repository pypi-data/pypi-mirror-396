import copy

import structlog
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langsmith import traceable
from pydantic import BaseModel, Field, create_model

from utils.llm import get_llm

from .linter import LinterError, Ruff
from .steps import functional_refactorings
from .utils import (
    FunctionalRefactoringData,
    assess_sys_prompt,
    merge_transform,
    refactoring_transform,
)

logger = structlog.get_logger(__name__)


def process_inputs(inputs: dict):
    processed = copy.deepcopy(inputs)
    processed["refactoring_candidates"] = [
        fr.name for fr in processed["refactoring_candidates"]
    ]
    return processed


def process_outputs(outputs: list[FunctionalRefactoringData]):
    processed = copy.deepcopy(outputs)
    processed = [fr.name for fr in processed]
    return processed


@traceable(process_inputs=process_inputs, process_outputs=process_outputs)
async def detect_required_refactorings(
    src_lang: str,
    src_code: str,
    refactoring_candidates: list[FunctionalRefactoringData],
    min_lines: int = 50,
) -> list[FunctionalRefactoringData]:
    """Detect the required refactorings for the given formalization state."""

    if len(src_code.splitlines()) < min_lines:
        return []

    def create_batch_refactoring_tool(
        tools: list[type[BaseModel]],
    ) -> type[BaseModel]:
        """Create a batch tool that can invoke a list of tools.

        See: https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview#parallel-tool-use
        """
        tool_names_str = ",".join([f"`{t.__name__}`" for t in tools])
        BatchRefactoring = create_model(  # noqa: N806
            "BatchRefactoring",
            __doc__="""Invoke and apply a list of refactorings to the code.""",
            refactorings=(
                list[str],
                Field(
                    description=f"A list of the refactoring names to be invoked. "
                    f"Available refactoring names: {tool_names_str}"
                ),
            ),
        )
        return BatchRefactoring

    def parse_required_refactorings(msg: AIMessage) -> list[str]:
        """Parse the tool calls to get the list of refactorings to apply."""
        if not msg.tool_calls:
            return []
        selected_tool: list[str] = []
        for tool_call in msg.tool_calls:
            if tool_call["name"] == "BatchRefactoring":
                selected_tool.extend(tool_call["args"]["refactorings"])
            else:
                selected_tool.append(tool_call["name"])
        return list(set(selected_tool))

    llm = get_llm(use_case="code")  # maybe json is enough?
    assess_tools: list[type[BaseModel]] = [
        fr.to_assess_tool() for fr in refactoring_candidates
    ]

    batch_refactoring_tool = create_batch_refactoring_tool(assess_tools)
    llmwt = llm.bind_tools(
        tools=[*assess_tools, batch_refactoring_tool],
        tool_choice="auto",  # automatically selects a tool (including no tool)
    )
    assess_msgs = [
        SystemMessage(content=assess_sys_prompt),
        HumanMessage(
            content=(
                f"Here is the code to be refactored:\n\n"
                f"```{src_lang}\n{src_code}\n```\n\n"
            )
        ),
    ]
    assess_res = await llmwt.ainvoke(assess_msgs)

    required_names: list[str] = parse_required_refactorings(assess_res)
    required_refactorings: list[FunctionalRefactoringData] = [
        fr for fr in refactoring_candidates if fr.name in required_names
    ]

    return required_refactorings


@traceable
async def functional_refactoring(
    src_lang: str,
    src_code: str,
    refactoring_min_lines: int = 50,
    use_batch_refactoring: bool = True,
) -> list[tuple[str, str]]:
    """
    <Node> Functional refactoring
    """

    # Filter refactorings
    skipped_refactorings = [
        "FunctionTotalizationRefactoring",
        "TypeSystemEnhancementRefactoring",
        "ExhaustivePatternMatchingRefactoring",
    ]
    refactorings: list[FunctionalRefactoringData] = [
        refactoring
        for refactoring in functional_refactorings
        if refactoring.name not in skipped_refactorings
    ]

    # Detect required refactorings
    required_refactorings: list[
        FunctionalRefactoringData
    ] = await detect_required_refactorings(
        src_lang=src_lang,
        src_code=src_code,
        refactoring_candidates=refactorings,
        min_lines=refactoring_min_lines,
    )

    logger.info(
        "required_refactorings",
        required_refactorings=[r.name for r in required_refactorings],
    )

    # Apply refactorings
    llm = get_llm(use_case="code")
    refactoring_res: list[tuple[str, str]] = []
    if required_refactorings:
        if use_batch_refactoring:
            # Apply in one go
            merged_name = "_".join([r.name for r in required_refactorings])
            merged_name = str(len(required_refactorings)) + "_" + merged_name
            refactored_code = await merge_transform(
                src_code=src_code,
                src_lang=src_lang,
                llm=llm,
                refactorings=required_refactorings,
            )
            refactoring_res = [(merged_name, refactored_code)]
            logger.info("refactoring_applied")

        else:
            # Apply in sequence
            curr_code = src_code
            refactoring_res: list[tuple[str, str]] = []
            for refactoring in required_refactorings:
                curr_code = await refactoring_transform(
                    src_code=curr_code,
                    src_lang=src_lang,
                    llm=llm,
                    refactoring=refactoring,
                )
                logger.info(
                    "refactoring_being_applied", refactoring_name=refactoring.name
                )
                refactoring_res.append((refactoring.name, curr_code))

    # Format and Lint (if there's any refactoring applied)
    if src_lang == "python" and refactoring_res:
        _, last_code = refactoring_res[-1]
        try:
            formatted_code, linted_code = format_and_lint(last_code)
            refactoring_res.extend(
                [
                    ("formatted", formatted_code),
                    ("linted", linted_code),
                ]
            )
        except Exception as e:
            if isinstance(e, LinterError):
                logger.info(
                    "linter_error",
                    error=str(e),
                    error_type=type(e).__name__,
                )
            else:
                logger.error(
                    "unexpected_error",
                    error=str(e),
                    error_type=type(e).__name__,
                )

    return refactoring_res


@traceable
def format_and_lint(code: str) -> tuple[str, str]:
    linter = Ruff()
    formatted_code = linter.format(code)
    linted_code = linter.lint(formatted_code)
    return formatted_code, linted_code
