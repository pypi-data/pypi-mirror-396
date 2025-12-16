from typing import Any, Literal

from langgraph.graph import START, StateGraph
from langgraph.types import Command
from pydantic import BaseModel, Field

import agents.spec_logician.tools as tools
from agents.spec_logician.formalization_state import FormalizationState, mk_init_state
from utils.agent.base import EndResult

###############
# GRAPH STATE #
###############


class InitStateCommand(BaseModel):
    type: Literal["init_state"] = "init_state"
    src_spec: str


class GenerateFormalSpecCommand(BaseModel):
    type: Literal["generate_formal_spec"] = "generate_formal_spec"


class ValidateFormalSpec(BaseModel):
    type: Literal["validate_formal_spec"] = "validate_formal_spec"


class SetSourceSpecCommand(BaseModel, extra="forbid"):
    type: Literal["set_source_spec"] = "set_source_spec"
    src_spec: str


class SetFormalSpecCommand(BaseModel, extra="forbid"):
    type: Literal["set_formal_spec"] = "set_formal_spec"
    formal_spec: str


class AutomaticWorkflowCommand(BaseModel, extra="forbid"):
    type: Literal["automatic_workflow"] = "automatic_workflow"


class SyncSourceCommand(BaseModel, extra="forbid"):
    type: Literal["sync_source"] = "sync_source"


class SyncFormalCommand(BaseModel, extra="forbid"):
    type: Literal["sync_formal"] = "sync_formal"


class SubmitFnImplementation(BaseModel, extra="forbid"):
    type: Literal["submit_fn_implementation"] = "submit_fn_implementation"
    name: str
    statements: list[str]


class SetUserInstructions(BaseModel, extra="forbid"):
    type: Literal["add_user_instructions"] = "add_user_instructions"
    instructions: list[str]


class GetNLSpec(BaseModel, extra="forbid"):
    type: Literal["get_nl_spec"] = "get_nl_spec"


class GetPprintedFormalSpec(BaseModel, extra="forbid"):
    type: Literal["get_pprinted_formal_spec"] = "get_pprinted_formal_spec"


class GetIplSpec(BaseModel, extra="forbid"):
    type: Literal["get_ipl_spec"] = "get_ipl_spec"


class GetValidationResult(BaseModel, extra="forbid"):
    type: Literal["get_validation_result"] = "get_validation_result"


class GetOpaqueFunctions(BaseModel, extra="forbid"):
    type: Literal["get_opaque_functions"] = "get_opaque_functions"


class GetUserInstructions(BaseModel, extra="forbid"):
    type: Literal["get_user_instructions"] = "get_user_instructions"


UserCommand = (
    InitStateCommand
    | GenerateFormalSpecCommand
    | ValidateFormalSpec
    | SetSourceSpecCommand
    | SetFormalSpecCommand
    | AutomaticWorkflowCommand
    | SyncSourceCommand
    | SyncFormalCommand
    | SubmitFnImplementation
    | SetUserInstructions
    | GetNLSpec
    | GetPprintedFormalSpec
    | GetIplSpec
    | GetValidationResult
    | GetOpaqueFunctions
    | GetUserInstructions
)


class GraphState(BaseModel):
    command: UserCommand | None = Field(None, description="User command to run")
    formalization_state: FormalizationState | None = Field(
        None, description="Current state of the formalization process"
    )
    attempts: int = Field(
        0, description="Counter of attempts for automatic agentic workflows"
    )
    end_result: EndResult = Field(
        description="End result of the whole task.",
        default=EndResult(result="success", info=""),
    )


#########
# NODES #
#########


def on_auto_workflow(cmd: UserCommand | None) -> bool:
    return isinstance(cmd, AutomaticWorkflowCommand)


def success_update(info: str) -> dict:
    return {"end_result": EndResult(result="success", info=info)}


def fail_update(info: str) -> dict:
    return {"end_result": EndResult(result="failure", info=info)}


def exec_command(
    state: GraphState,
    config,
) -> Command[Literal["generate_formal_spec", "validate_formal_spec", "__end__"]]:
    cmd = state.command
    fstate = state.formalization_state

    if not cmd:
        return Command(goto="__end__", update=fail_update("No command to execute"))

    if isinstance(cmd, InitStateCommand):
        print("Node: INIT STATE")
        if fstate:
            update = fail_update("State is already initialized")
        else:
            update = {
                "formalization_state": mk_init_state(cmd.src_spec),
                "end_result": EndResult(result="success", info=""),
            }
        return Command(goto="__end__", update=update)
    elif isinstance(cmd, GenerateFormalSpecCommand | AutomaticWorkflowCommand):
        return Command(goto="generate_formal_spec")
    elif isinstance(cmd, ValidateFormalSpec):
        return Command(goto="validate_formal_spec")
    elif isinstance(cmd, SetSourceSpecCommand):
        update = set_source_spec(state, cmd.src_spec)
        return Command(goto="__end__", update=update)
    elif isinstance(cmd, SetFormalSpecCommand):
        update = set_formal_spec(state, cmd.formal_spec)
        return Command(goto="__end__", update=update)
    elif isinstance(cmd, SyncSourceCommand):
        update = sync_source(state, config)
        return Command(goto="__end__", update=update)
    elif isinstance(cmd, SyncFormalCommand):
        update = sync_formal(state, config)
        return Command(goto="__end__", update=update)
    elif isinstance(cmd, SubmitFnImplementation):
        update = submit_fn_implementation(state, cmd.name, cmd.statements)
        return Command(goto="__end__", update=update)
    elif isinstance(cmd, SetUserInstructions):
        update = set_user_instructions(state, cmd.instructions)
        return Command(goto="__end__", update=update)
    elif isinstance(cmd, GetNLSpec):
        update = get_nl_spec(state)
        return Command(goto="__end__", update=update)
    elif isinstance(cmd, GetPprintedFormalSpec):
        update = get_pprinted_formal_spec(state)
        return Command(goto="__end__", update=update)
    elif isinstance(cmd, GetIplSpec):
        update = get_ipl_spec(state)
        return Command(goto="__end__", update=update)
    elif isinstance(cmd, GetValidationResult):
        update = get_validation_result(state)
        return Command(goto="__end__", update=update)
    elif isinstance(cmd, GetOpaqueFunctions):
        update = get_opaque_functions(state)
        return Command(goto="__end__", update=update)
    elif isinstance(cmd, GetUserInstructions):
        update = get_user_instructions(state)
        return Command(goto="__end__", update=update)
    else:
        return Command(goto="__end__", update=fail_update("Unknown command"))


def generate_formal_spec(
    state: GraphState, config
) -> Command[Literal["validate_formal_spec", "__end__"]]:
    print("--- Node: GENERATE FORMAL SPEC ---")

    fstate = state.formalization_state
    if not fstate:
        return Command(goto="__end__", update=fail_update("State not initialized"))

    new_fstate = tools.generate_formal_spec(fstate, config)
    update: dict[str, Any] = {
        "formalization_state": new_fstate,
        "attempts": state.attempts + 1,
    }
    if on_auto_workflow(state.command):
        goto = "validate_formal_spec"
    else:
        update["end_result"] = EndResult(result="success", info="")
        goto = "__end__"

    return Command(goto=goto, update=update)


def validate_formal_spec(
    state: GraphState, config
) -> Command[Literal["generate_formal_spec", "__end__"]]:
    print("--- Node: VALIDATE FORMAL SPEC ---")

    fstate = state.formalization_state
    if not fstate:
        return Command(goto="__end__", update=fail_update("State not initialized"))

    new_fstate = tools.validate_formal_spec(fstate, config)

    if isinstance(new_fstate, tools.ToolError):
        return Command(goto="__end__", update=fail_update(new_fstate.message))

    if (
        new_fstate.formalization is None
        or new_fstate.formalization.validation_result is None
    ):
        return Command(
            goto="__end__", update=fail_update("Validation failed unexpectedly")
        )

    update: dict[str, Any] = {"formalization_state": new_fstate}
    if on_auto_workflow(state.command):
        feedback = new_fstate.formalization.validation_result

        if len(feedback) > 0 and state.attempts < 3:
            goto = "generate_formal_spec"
        else:
            if len(feedback) > 0:
                update["end_result"] = EndResult(
                    result="failure",
                    info="A formal spec has been generated, "
                    "but with some validation errors",
                )
                goto = "__end__"
            else:
                update["end_result"] = EndResult(result="success", info="")
                goto = "__end__"
    else:
        update["end_result"] = EndResult(result="success", info="")
        goto = "__end__"

    return Command(goto=goto, update=update)


def set_source_spec(state: GraphState, src_spec: str) -> dict[str, Any]:
    print("--- Node: SET SOURCE SPEC ---")

    fstate = state.formalization_state
    if not fstate:
        return fail_update("State not initialized")

    new_fstate = tools.set_natural_language_spec(fstate, src_spec)
    update = {
        "formalization_state": new_fstate,
        "end_result": EndResult(result="success", info=""),
    }
    return update


def set_formal_spec(state: GraphState, formal_spec: str) -> dict[str, Any]:
    print("--- Node: SET FORMAL SPEC ---")

    fstate = state.formalization_state
    if not fstate:
        return fail_update("State not initialized")

    new_fstate = tools.set_formal_spec(fstate, formal_spec)

    if isinstance(new_fstate, tools.ToolError):
        return fail_update(new_fstate.message)

    update = {
        "formalization_state": new_fstate,
        "end_result": EndResult(result="success", info=""),
    }
    return update


def sync_source(state: GraphState, config) -> dict[str, Any]:
    print("--- Node: SYNC SOURCE ---")

    fstate = state.formalization_state
    if not fstate:
        return fail_update("State not initialized")

    new_fstate = tools.sync_nl_spec(fstate, config)

    if isinstance(new_fstate, tools.ToolError):
        return fail_update(new_fstate.message)

    update = {
        "formalization_state": new_fstate,
        "end_result": EndResult(result="success", info=""),
    }
    return update


def sync_formal(state: GraphState, config) -> dict[str, Any]:
    print("--- Node: SYNC FORMAL ---")

    fstate = state.formalization_state
    if not fstate:
        return fail_update("State not initialized")

    new_fstate = tools.sync_formal(fstate, config)

    update = {
        "formalization_state": new_fstate,
        "end_result": EndResult(result="success", info=""),
    }
    return update


def set_user_instructions(state, instructions: list[str]) -> dict[str, Any]:
    print("--- Node: SET USER INSTRUCTIONS ---")

    fstate = state.formalization_state
    if not fstate:
        return fail_update("State not initialized")

    new_fstate = tools.set_user_instructions(fstate, instructions)

    return {
        "formalization_state": new_fstate,
        "end_result": EndResult(result="success", info=""),
    }


def submit_fn_implementation(state, name: str, statements: list[str]) -> dict[str, Any]:
    print("--- Node: SUBMIT FN IMPLEMENTATION ---")

    fstate = state.formalization_state
    if not fstate:
        return fail_update("State not initialized")

    new_fstate = tools.submit_fn_implementation(fstate, name, statements)

    if isinstance(new_fstate, tools.ToolError):
        return fail_update(new_fstate.message)

    return {
        "formalization_state": new_fstate,
        "end_result": EndResult(result="success", info=""),
    }


def get_nl_spec(state: GraphState) -> dict[str, Any]:
    print("--- Node: GET NL SPEC ---")

    fstate = state.formalization_state
    if not fstate:
        return fail_update("State not initialized")

    return success_update(fstate.src_spec)


def get_pprinted_formal_spec(state: GraphState) -> dict[str, Any]:
    print("--- Node: GET PPRINTED FORMAL SPEC ---")

    fstate = state.formalization_state
    if not fstate:
        return fail_update("State not initialized")

    result = tools.get_pprinted_formal_spec(fstate)
    if isinstance(result, tools.ToolError):
        return fail_update(result.message)

    return success_update(result)


def get_ipl_spec(state: GraphState) -> dict[str, Any]:
    print("--- Node: GET IPL SPEC ---")

    fstate = state.formalization_state
    if not fstate:
        return fail_update("State not initialized")

    result = tools.get_ipl_spec(fstate)
    if isinstance(result, tools.ToolError):
        return fail_update(result.message)

    return success_update(result)


def get_validation_result(state: GraphState) -> dict[str, Any]:
    print("--- Node: GET VALIDATION RESULT ---")

    fstate = state.formalization_state
    if not fstate:
        return fail_update("State not initialized")

    result = tools.get_validation_result(fstate)
    if isinstance(result, tools.ToolError):
        return fail_update(result.message)

    return success_update(result)


def get_opaque_functions(state: GraphState) -> dict[str, Any]:
    print("--- Node: GET OPAQUE FUNCTIONS ---")

    fstate = state.formalization_state
    if not fstate:
        return fail_update("State not initialized")

    result = tools.get_opaque_functions(fstate)
    if isinstance(result, tools.ToolError):
        return fail_update(result.message)

    return success_update(result)


def get_user_instructions(state: GraphState) -> dict[str, Any]:
    print("--- Node: GET USER INSTRUCTIONS ---")

    fstate = state.formalization_state
    if not fstate:
        return fail_update("State not initialized")

    result = tools.get_user_instructions(fstate)
    if isinstance(result, tools.ToolError):
        return fail_update(result.message)

    return success_update(result)


#########
# GRAPH #
#########

builder = StateGraph(GraphState)
builder.add_node("exec_command", exec_command)
builder.add_node("generate_formal_spec", generate_formal_spec)
builder.add_node("validate_formal_spec", validate_formal_spec)
builder.add_edge(START, "exec_command")


graph = builder.compile()
