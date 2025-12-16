from typing import Any, Literal

import structlog
from langgraph.types import Command as LGCommand

from ..base import FormalizationState, FormalizationStateUpdate
from ..task import Formalization, FormalizationTask, Interaction, PrecheckFailure
from .graph_state import GraphState

logger = structlog.get_logger(__name__)

SupervisorInGraphCommand = LGCommand[Literal["code_logician_supervisor"]]


def check_field_exists(
    fstate: FormalizationState | None,
    *field_path: str,
    message: str | None = None,
    use_bool_val: bool = False,
) -> list[PrecheckFailure]:
    """
    Check if a field (potentially nested) exists in formalization state

    Args:
        fstate: The formalization state to check
        *field_path: Path to the field (e.g., "iml_code" or "eval_res", "errors")
        message: Custom message for the failure (optional)
        use_bool_val: If True, determine missing using `bool()`. If False, use `is None`

    Returns:
        List of precheck failures if field doesn't exist
    """
    if fstate is None:
        return [
            PrecheckFailure(
                field="fstate",
                reason="missing",
                message="No formalization state found, use `init_state` to initialize",
            )
        ]

    # If no field path provided, just check fstate exists (already passed)
    if not field_path:
        return []

    def missing_check(val: Any) -> bool:
        if use_bool_val:
            return not bool(val)
        else:
            return val is None

    current = fstate
    full_field_path = ".".join(field_path)

    try:
        # Get the value of the field
        for field in field_path:
            if hasattr(current, field):
                current = getattr(current, field)
                if current is None:
                    break
            else:
                current = None
                break

        if missing_check(current):
            default_message = f"No {full_field_path} found"

            return [
                PrecheckFailure(
                    field=full_field_path,
                    reason="missing",
                    message=message or default_message,
                )
            ]

        return []

    except Exception:
        return [
            PrecheckFailure(
                field=full_field_path,
                reason="missing",
                message=message or f"No {full_field_path} found",
            )
        ]


def unpack_step_data(state: GraphState) -> tuple[int, list[Interaction], Interaction]:
    """Extract step data with validation"""
    step_i = state.step_i
    if step_i is None:
        raise ValueError("Missing step index")
    steps = state.steps
    step = steps[step_i]
    return step_i, steps, step


def append_fstate_to_ftask(
    ftask: FormalizationTask,
    fstate: FormalizationState,
    fupdate: FormalizationStateUpdate,
    action_name: str,
) -> tuple[FormalizationState, FormalizationTask]:
    """Create updated fstate and append to ftask"""
    new_fstate = FormalizationState.model_validate(fstate.model_dump() | fupdate)
    new_formalization = Formalization(action=action_name, fstate=new_fstate)

    updated_ftask = ftask.model_copy(
        update={"formalizations": [*ftask.formalizations, new_formalization]}
    )

    return new_fstate, updated_ftask


def mk_precheck_failure_response(
    precheck_failures: list[PrecheckFailure], steps: list[Interaction], step_i: int
) -> SupervisorInGraphCommand:
    """Build precheck failure response"""
    updated_steps = steps.copy()
    ftask = updated_steps[step_i].task
    if ftask is None:
        raise ValueError("Missing task when building precheck failure response")

    # Create new task with failures
    updated_ftask = ftask.model_copy(
        update={"status": "precheck_failed", "precheck_failures": precheck_failures}
    )

    # Update step with new task
    updated_steps[step_i] = updated_steps[step_i].model_copy(
        update={"task": updated_ftask}
    )

    command = SupervisorInGraphCommand(
        update={"steps": updated_steps}, goto="code_logician_supervisor"
    )

    return command


def mk_success_response(
    steps: list[Interaction], step_i: int, updated_ftask: FormalizationTask
) -> SupervisorInGraphCommand:
    """Build success response"""
    updated_steps = steps.copy()
    updated_steps[step_i] = updated_steps[step_i].model_copy(
        update={"task": updated_ftask}
    )

    command = SupervisorInGraphCommand(
        update={"steps": updated_steps}, goto="code_logician_supervisor"
    )

    return command
