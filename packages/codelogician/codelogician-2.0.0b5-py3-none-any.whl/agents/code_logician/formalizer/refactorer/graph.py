from typing import Literal

from anthropic import BaseModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.types import Command
from pydantic import Field, create_model

from agents.code_logician.formalizer.refactorer.base import GraphState, InputState
from agents.code_logician.formalizer.refactorer.steps import (
    functional_refactorings,
)
from agents.code_logician.formalizer.refactorer.utils import (
    FunctionalRefactoringData,
    assess_sys_prompt,
    merge_transform,
)
from utils.agent.base import EndResult, ImandraMetadata, NodeMetadata
from utils.llm import get_llm


async def functional_refactoring(state: InputState) -> Command[Literal["__end__"]]:
    """
    <Node> Functional refactoring
    """

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

    print("--- Node: FUNCTIONAL REFACTORING ---")
    src_code = state.src_code

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
    llm = get_llm(use_case="code")  # maybe json is enough?
    assess_tools: list[type[BaseModel]] = [fr.to_assess_tool() for fr in refactorings]

    batch_refactoring_tool = create_batch_refactoring_tool(assess_tools)
    llmwt = llm.bind_tools(
        tools=[*assess_tools, batch_refactoring_tool],
        tool_choice="auto",  # automatically selects a tool (including no tool)
    )
    assess_msgs = [
        SystemMessage(content=assess_sys_prompt),
        HumanMessage(
            # add src_lang in ```?
            content=f"Here is the code to be refactored:\n\n```\n{src_code}\n```\n\n",
        ),
    ]
    assess_res = await llmwt.ainvoke(assess_msgs)

    required_names: list[str] = parse_required_refactorings(assess_res)
    required_refactorings: list[FunctionalRefactoringData] = [
        fr for fr in refactorings if fr.name in required_names
    ]

    print(f"\t- Required refactorings: {[r.name for r in required_refactorings]}")

    # Apply refactorings
    llm = get_llm(use_case="code")
    refactoring_res: list[tuple[str, str]] = []
    if required_refactorings:
        # Apply in one go
        merged_name = "_".join([r.name for r in required_refactorings])
        merged_name = str(len(required_refactorings)) + "_" + merged_name
        refactored_code = await merge_transform(src_code, llm, required_refactorings)
        refactoring_res = [(merged_name, refactored_code)]
        print("\t- Refactoring applied")

        # # Apply in sequence
        # curr_code = src_code
        # refactoring_res: list[tuple[str, str]] = []
        # for refactoring in required_refactorings:
        #     print(f"\t- {refactoring.name} refactoring being applied...")
        #     curr_code = refactoring.transform(curr_code, llm)
        #     refactoring_res.append((refactoring.name, curr_code))

    update = {
        "refactored_code": refactoring_res,
    }
    info_str = (
        (f"\n\nRefactored code:\n\n```python\n{refactoring_res[-1][1]}\n```")
        if refactoring_res
        else ""
    )
    update["end_result"] = EndResult(
        result="success",
        info="Refactoring completed." + info_str,
    )

    return Command(
        update=update,
        goto="__end__",
    )


builder = StateGraph(GraphState, input_schema=InputState)

builder.add_node(
    "functional_refactoring",
    functional_refactoring,
    metadata=NodeMetadata(imandra=ImandraMetadata(task_name="Refactoring Python code")),
)

builder.add_edge(START, "functional_refactoring")

graph = builder.compile()
