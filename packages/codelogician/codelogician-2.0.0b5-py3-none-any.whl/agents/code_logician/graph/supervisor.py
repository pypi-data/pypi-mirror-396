from typing import Literal

import structlog
from langgraph.types import Command as LGCommand, StreamWriter

from utils.agent.base import EndResult

from ..task import Formalization, FormalizationTask, Interaction, PrecheckFailure
from .graph_state import GraphState

logger = structlog.get_logger(__name__)

SupervisorOutGraphCommand = LGCommand[
    Literal[
        "__end__",
        "init_state_node",
        "edit_state_element_node",
        "get_state_element_node",
        "search_fdb_node",
        "embed_node",
        "check_formalization_node",
        "gen_program_refactor_node",
        "gen_formalization_data_node",
        "gen_formalization_failure_data_node",
        "admit_model_node",
        "gen_model_node",
        "set_model_node",
        "gen_vgs_node",
        "gen_region_decomps_node",
        "gen_test_cases_node",
        "sync_source_node",
        "sync_model_node",
        "agent_formalizer_node",
        "agent_formalizer_core_node",
        "agent_formalizer_hitl_node",
        "agent_formalizer_end_node",
        "suggest_formalization_action_node",
        "suggest_assumptions_node",
        "suggest_approximation_node",
    ]
]

# Commands that don't require formalization state
NO_FSTATE_COMMANDS = {"init_state", "search_fdb"}


def code_logician_supervisor(
    state: GraphState, config, writer: StreamWriter
) -> SupervisorOutGraphCommand:
    steps: list[Interaction] = state.steps

    logger.info(
        "supervisor_started",
        total_steps=len(steps),
        current_step=state.step_i,
    )

    # Exit if any step is in error or precheck_failed
    exit = any(
        (ftask := step.task) is not None
        and ftask.status in ["error", "precheck_failed"]
        for step in steps
    )
    if exit:
        logger.warning(
            "supervisor_exit_failure",
            reason="step_error_or_precheck_failed",
        )
        return SupervisorOutGraphCommand(
            update={"step_i": None, "end_result": EndResult(result="failure")},
            goto="__end__",
        )

    # Find the first pending step
    def is_pending_step(step: Interaction) -> bool:
        return (step.task is None and step.message is None) or (
            (ftask := step.task) is not None and ftask.status == "pending"
        )

    step_i = next(
        (i for i, step in enumerate(steps) if is_pending_step(step)),
        None,
    )

    # No pending step, finish
    if step_i is None:
        logger.info(
            "supervisor_completed",
            reason="no_pending_steps",
        )
        return SupervisorOutGraphCommand(
            update={"step_i": None},
            goto="__end__",
        )

    step: Interaction = steps[step_i]
    command = step.command

    # Command not requiring fstate
    if command.root.type in NO_FSTATE_COMMANDS:
        goto = command.root.type + "_node"
        logger.info(
            "supervisor_routing",
            step_id=step_i,
            command_type=command.root.type,
            goto=goto,
            requires_fstate=False,
        )
        return SupervisorOutGraphCommand(update={"step_i": step_i}, goto=goto)

    last_fstate = state.last_fstate  # It's guaranteed to be no later than current step
    # Check existence of formalization state
    if last_fstate is None:
        ftask = FormalizationTask(
            formalizations=[],
            status="precheck_failed",
            precheck_failures=[
                PrecheckFailure(
                    field="fstate",
                    reason="No formalization state",
                    message=(
                        "No formalization state found, use `init_state` to initialize"
                    ),
                )
            ],
        )
        step.task = ftask
        steps[step_i] = step
        logger.warning(
            "supervisor_no_fstate",
            step_id=step_i,
            command_type=command.root.type,
        )
        return SupervisorOutGraphCommand(
            update={
                "steps": steps,
            },
            goto="__end__",
        )

    # Assign task
    # Init trajectory if it's empty
    ftask = step.task
    if ftask is None or (ftask.formalizations == []):
        init_f = [Formalization(action="input", fstate=last_fstate)]
        if ftask is None:
            ftask = FormalizationTask(
                formalizations=init_f,
                status="pending",
            )
        else:
            ftask.formalizations = init_f

    step.task = ftask
    steps[step_i] = step
    goto = command.root.type + "_node"
    return SupervisorOutGraphCommand(
        update={"steps": steps, "step_i": step_i}, goto=goto
    )
