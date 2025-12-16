"""Tool definitions and transition mappings for agent_formalizer.

Provides:
- TOOL_MAP: Available LLM-invocable tools (search_iml_api, gen_model)
- F_TRANSITION_MAP: State transition functions by name
- run_tool: Execute tool calls and handle errors
"""

from __future__ import annotations

from inspect import iscoroutinefunction
from typing import Final, cast

from pydantic import BaseModel, Field

from agents.code_logician.base.formalization_state import FormalizationStateUpdate
from agents.code_logician.fstate_transition import (
    functional_refactoring_trans,
    inappropriateness_check_trans,
)
from agents.code_logician.fstate_transition.fdb import (
    gather_formalization_failure_info,
    gather_formalization_source_info_trans,
)
from utils.fdb.fdb import FDB, FDBFormatter, get_fdb

from ...base import FormalizationState
from ...fstate_transition import (
    AsyncFormalizationStateTransition,
    FormalizationStateTransition,
    set_model,
)
from .base import FTransName, ToolCall, ToolDefinition, ToolName, ToolResult

F_TRANSITION_MAP: Final[  # ty: ignore[invalid-assignment]
    dict[
        FTransName,
        FormalizationStateTransition | AsyncFormalizationStateTransition,
    ]
] = {
    "check_formalization": inappropriateness_check_trans,
    "gen_program_refactor": functional_refactoring_trans,
    "gen_formalization_data": gather_formalization_source_info_trans,
    "gather_formalization_failure_info": gather_formalization_failure_info,
}


async def search_iml_api(
    fstate: FormalizationState, config, query: str
) -> FormalizationStateUpdate:
    """Search formalization database for IML API references and add to context."""
    fdb = get_fdb()
    search_res: list[FDB.IMLAPIReference] = await fdb.search_iml_func(
        query=query,
        top_k=5,
    )
    flatten = FDBFormatter.format_iml_api_reference(search_res)

    conv_f_info = fstate.conversion_failures_info
    last_conv_f_info = conv_f_info[-1]
    last_conv_f_info.tool_calls += [flatten]

    updated_conv_f_info = [*conv_f_info[:-1], last_conv_f_info]

    return FormalizationStateUpdate(conversion_failures_info=updated_conv_f_info)


class SearchIMLAPI(BaseModel):
    """Search IML API references in the database.

    A string flatten from a list of IML API references is returned, sorted by relevance.
    """

    query: str = Field(description="query string")


search_iml_api_tool = ToolDefinition.create(
    tool_func=search_iml_api,
    args_schema=SearchIMLAPI,
    description=SearchIMLAPI.__doc__,
)


class GenModel(BaseModel):
    """Consider ready to generate IML code and generate it"""

    iml: str = Field(description="IML code")


async def gen_model(
    fstate: FormalizationState,
    config,
    iml: str,
) -> FormalizationStateUpdate:
    """Generate and evaluate IML model, updating formalization state."""
    return await set_model(
        fstate,
        config,
        iml_code=iml,
    )


gen_model_tool = ToolDefinition.create(
    tool_func=gen_model,
    args_schema=GenModel,
    description=GenModel.__doc__,
)


TOOL_MAP: Final[dict[ToolName, ToolDefinition]] = {
    "gen_model": gen_model_tool,
    "search_iml_api": search_iml_api_tool,
}


async def run_tool(
    tool_call: ToolCall,
    fstate: FormalizationState,
    config,
) -> ToolResult:
    """Execute tool call and return result with error handling."""
    tool_func = TOOL_MAP[tool_call.tool_name].tool_func
    try:
        if iscoroutinefunction(tool_func):
            tool_func = cast(AsyncFormalizationStateTransition, tool_func)
            result = await tool_func(fstate, config, **tool_call.arguments)
        else:
            tool_func = cast(FormalizationStateTransition, tool_func)
            result = tool_func(fstate, config, **tool_call.arguments)

    except Exception as e:
        return ToolResult(
            success=False,
            fupdate=None,
            error=str(e),
        )

    return ToolResult(
        success=True,
        fupdate=result,
        error=None,
    )
