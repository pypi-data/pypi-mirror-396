from typing import cast

import structlog

from utils.llm import get_llm

from ..base import (
    ConversionSourceInfo,
    FormalizationState,
    FormalizationStateUpdate,
    FormalizationStatus,
)
from ..base.model_utils.iml import parse_iml
from ..command import (
    InitStateCommand,
    SuggestFormalizationActionCommand,
)
from ..fstate_transition import (
    gather_formalization_failure_info,
    gather_formalization_source_info,
    inappropriateness_check_trans,
)
from ..task import Formalization, FormalizationTask, PrecheckFailure
from ..tools.sync_model import diff_code, update_iml_code, update_src_code
from .base_handlers import BaseNodeHandler, SupervisorInGraphCommand
from .graph_state import GraphState
from .utils import (
    append_fstate_to_ftask,
    check_field_exists,
    mk_precheck_failure_response,
    mk_success_response,
    unpack_step_data,
)

logger = structlog.get_logger(__name__)


class InitStateNodeHandler(BaseNodeHandler):
    def __init__(self):
        super().__init__("init_state_node")

    def __call__(self, state: GraphState, config) -> SupervisorInGraphCommand:
        step_i, steps, step = unpack_step_data(state)
        command: InitStateCommand = step.command.root

        logger.info(
            "init_state_started",
            handler="init_state_node",
            step_id=step_i,
            src_lang=command.src_lang,
        )

        new_fstep = Formalization(
            action=command.type,
            fstate=FormalizationState(
                src_code=command.src_code,
                src_lang=command.src_lang,
            ),
        )
        ftask = FormalizationTask(
            formalizations=[new_fstep],
            status="done",
        )
        step.task = ftask
        steps[step_i] = step

        logger.info(
            "init_state_completed",
            handler="init_state_node",
            step_id=step_i,
        )

        return SupervisorInGraphCommand(
            update={"steps": steps}, goto="code_logician_supervisor"
        )


class GenFormalizationDataNodeHandler(BaseNodeHandler):
    def __init__(self):
        super().__init__("gen_formalization_data_node")

    async def __call__(self, state: GraphState, config) -> SupervisorInGraphCommand:
        # Unpack
        step_i, steps, step = unpack_step_data(state)
        ftask = step.task
        if ftask is None:
            raise ValueError("Missing task in GenFormalizationDataNodeHandler")
        fstate = ftask.last_fstate

        logger.info(
            "gen_formalization_data_started",
            handler="gen_formalization_data_node",
            step_id=step_i,
        )

        # Precheck fstate
        precheck_failures = check_field_exists(fstate)
        if precheck_failures:
            logger.warning(
                "gen_formalization_data_precheck_failed",
                handler="gen_formalization_data_node",
                step_id=step_i,
                failures=[f.field for f in precheck_failures],
            )
            command = mk_precheck_failure_response(precheck_failures, steps, step_i)
            return command
        fstate = cast(FormalizationState, fstate)

        if fstate.conversion_source_info is None:
            fstate.conversion_source_info = ConversionSourceInfo()

        if fstate.conversion_source_info.missing_func is None:  # type: ignore
            fupdate = await inappropriateness_check_trans(fstate, config)
            fstate, ftask = append_fstate_to_ftask(
                ftask, fstate, fupdate, "check_formalization"
            )

        fupdate = await gather_formalization_source_info(
            fstate, config, use_refactored_code=True
        )
        _new_fstate, updated_ftask = append_fstate_to_ftask(
            ftask, fstate, fupdate, "gen_formalization_data"
        )

        final_ftask = updated_ftask.model_copy(update={"status": "done"})

        logger.info(
            "gen_formalization_data_completed",
            handler="gen_formalization_data_node",
            step_id=step_i,
        )

        command = mk_success_response(steps, step_i, final_ftask)
        return command


class SuggestFormalizationActionNodeHandler(BaseNodeHandler):
    def __init__(self):
        super().__init__("suggest_formalization_action_node")

    async def __call__(self, state: GraphState, config) -> SupervisorInGraphCommand:
        step_i, steps, step = unpack_step_data(state)
        ftask = step.task
        if ftask is None:
            raise ValueError("Missing task in SuggestFormalizationActionNodeHandler")
        fstate = step.last_fstate
        command: SuggestFormalizationActionCommand = step.command.root
        feedback = command.feedback

        logger.info(
            "suggest_formalization_action_started",
            handler="suggest_formalization_action_node",
            step_id=step_i,
        )

        # Precheck: fstate and iml_code
        precheck_failures = check_field_exists(fstate)
        precheck_failures.extend(check_field_exists(fstate, "iml_code"))
        if precheck_failures:
            logger.warning(
                "suggest_formalization_action_precheck_failed",
                handler="suggest_formalization_action_node",
                step_id=step_i,
                failures=[f.field for f in precheck_failures],
            )
            command = mk_precheck_failure_response(precheck_failures, steps, step_i)
            return command
        fstate = cast(FormalizationState, fstate)

        # Precheck: status
        if fstate.status != FormalizationStatus.INADMISSIBLE:
            ftask.status = "precheck_failed"
            ftask.precheck_failures = [
                PrecheckFailure(
                    field="status",
                    reason="Suggestion is only needed for inadmissible models",
                )
            ]
            step.task = ftask
            steps[step_i] = step
            return SupervisorInGraphCommand(
                update={"steps": steps}, goto="code_logician_supervisor"
            )

        iml_code = fstate.iml_code
        failures_info = fstate.conversion_failures_info
        the_failure = None
        for failure in reversed(failures_info):
            if failure.iml_code == iml_code:
                the_failure = failure
                break

        # Gather failure info for current IML code if not found
        if the_failure is None:
            fupdate = await gather_formalization_failure_info(fstate, config)
            fstate = FormalizationState.model_validate(fstate.model_dump() | fupdate)
            ftask.formalizations = [
                *ftask.formalizations,
                Formalization(
                    action="gather_formalization_failure_info", fstate=fstate
                ),
            ]

        # Add human hint
        new_fstate = fstate.model_copy(deep=True)
        curr_human_hint = new_fstate.conversion_failures_info[-1].human_hint
        if curr_human_hint is not None:
            feedback = curr_human_hint + "\n\n" + feedback
        new_fstate.conversion_failures_info[-1].human_hint = feedback
        ftask.formalizations = [
            *ftask.formalizations,
            Formalization(action="suggest_formalization_action", fstate=new_fstate),
        ]
        ftask.status = "done"

        step.task = ftask
        steps[step_i] = step
        return SupervisorInGraphCommand(
            update={"steps": steps}, goto="code_logician_supervisor"
        )


class SyncSourceNodeHandler(BaseNodeHandler):
    def __init__(self):
        super().__init__("sync_source_node")

    # TODO: no idea whether this will work or not!
    async def __call__(self, state: GraphState, config) -> SupervisorInGraphCommand:
        """
        Old iml, old src, new iml -> new src

        For now, old pairs are simply from the last fstate that has different iml

        Should we restrict the old iml to be admitted?
        Should we accept parameters from command?
        Should we keep track of a field indicating the sync?
        """
        step_i, steps, step = unpack_step_data(state)
        ftask = step.task
        if ftask is None:
            raise ValueError("Missing task in SyncSourceNodeHandler")
        fstate = step.last_fstate

        # Precheck: fstate and iml_code
        precheck_failures = check_field_exists(fstate)
        precheck_failures.extend(check_field_exists(fstate, "iml_code"))
        if precheck_failures:
            command = mk_precheck_failure_response(precheck_failures, steps, step_i)
            return command

        fstate = cast(FormalizationState, fstate)
        iml_code = cast(str, fstate.iml_code)

        # Precheck: there should be at least one different IML from earlier fstate
        steps_up_to_i = steps[: step_i + 1]
        all_formalizations: list[Formalization] = []
        for step in steps_up_to_i:
            ftask = step.task
            if ftask is None:
                continue
            all_formalizations.extend(ftask.formalizations)
        old_src, old_iml = None, None
        for formalization in all_formalizations:
            if (
                formalization.fstate.iml_code is None
                or formalization.fstate.iml_code == iml_code
            ):
                continue
            else:
                old_src = formalization.fstate.src_code
                old_iml = formalization.fstate.iml_code
        if old_iml is None:
            ftask.status = "precheck_failed"
            ftask.precheck_failures = [
                PrecheckFailure(
                    field="iml_code",
                    reason="There exists no different IML model from the current IML",
                )
            ]
            step.task = ftask
            steps[step_i] = step
            return SupervisorInGraphCommand(
                update={"steps": steps}, goto="code_logician_supervisor"
            )
        old_src = cast(str, old_src)

        llm = get_llm(use_case="code")
        iml_diff = diff_code(old_iml, iml_code)

        new_src_code = await update_src_code(llm, old_src, iml_code, iml_diff)

        fupdate = FormalizationStateUpdate(src_code=new_src_code)
        _, updated_ftask = append_fstate_to_ftask(ftask, fstate, fupdate, "sync_source")
        final_ftask = updated_ftask.model_copy(update={"status": "done"})

        command = mk_success_response(steps, step_i, final_ftask)
        return command


class SyncModelNodeHandler(BaseNodeHandler):
    def __init__(self):
        super().__init__("sync_model_node")

    async def __call__(self, state: GraphState, config) -> SupervisorInGraphCommand:
        """
        Old iml, old src, new src -> new iml
        """
        step_i, steps, step = unpack_step_data(state)
        ftask = step.task
        if ftask is None:
            raise ValueError("Missing task in SyncModelNodeHandler")
        fstate = step.last_fstate

        # Precheck: fstate
        precheck_failures = check_field_exists(fstate)
        if precheck_failures:
            command = mk_precheck_failure_response(precheck_failures, steps, step_i)
            return command

        fstate = cast(FormalizationState, fstate)
        src_code = fstate.src_code

        # Precheck: there should be at least one different IML from earlier fstate
        steps_up_to_i = steps[: step_i + 1]
        all_formalizations: list[Formalization] = []
        for step in steps_up_to_i:
            ftask = step.task
            if ftask is None:
                continue
            all_formalizations.extend(ftask.formalizations)

        old_iml, old_src = None, None
        for formalization in all_formalizations:
            if formalization.fstate.src_code == src_code:
                continue
            else:
                old_iml = formalization.fstate.iml_model
                old_src = formalization.fstate.src_code

        if old_src is None:
            ftask.status = "precheck_failed"
            ftask.precheck_failures = [
                PrecheckFailure(
                    field="src_code",
                    reason=(
                        "There exists no different source program from the current "
                        "source program"
                    ),
                )
            ]
            step.task = ftask
            steps[step_i] = step
            return SupervisorInGraphCommand(
                update={"steps": steps}, goto="code_logician_supervisor"
            )
        old_iml = cast(str, old_iml)

        llm = get_llm(use_case="code")
        src_diff = diff_code(old_src, src_code)

        new_iml_model = await update_iml_code(llm, old_iml, old_src, src_diff)
        parsed_res = parse_iml(new_iml_model)
        if parsed_res is None:
            logger.warning("IML code has syntax errors and cannot be parsed")
            (
                iml_model,
                top_defs,
                linting_errors,
                decomp_req_data,
                verify_req_data,
            ) = new_iml_model, [], [], [], []
        else:
            (
                iml_model,
                top_defs,
                linting_errors,
                decomp_req_data,
                verify_req_data,
            ) = parsed_res
        assert iml_model == new_iml_model
        assert len(decomp_req_data) == 0
        assert len(verify_req_data) == 0

        fupdate = FormalizationStateUpdate(
            iml_code=new_iml_model,
            iml_model=new_iml_model,
            top_definitions=top_defs,
            linting_errors=linting_errors,
            status=FormalizationStatus.UNKNOWN,
        )
        _, updated_ftask = append_fstate_to_ftask(ftask, fstate, fupdate, "sync_model")
        final_ftask = updated_ftask.model_copy(update={"status": "done"})

        command = mk_success_response(steps, step_i, final_ftask)
        return command


def gen_assumption_candidates_node(state: GraphState, config) -> None:
    # ) -> SupervisorInGraphCommand:
    # populate FDB
    pass
