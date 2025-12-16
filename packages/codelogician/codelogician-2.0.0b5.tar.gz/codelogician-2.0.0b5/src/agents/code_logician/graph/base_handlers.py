from abc import abstractmethod
from typing import cast

import structlog

from ..base import FormalizationState, FormalizationStateUpdate
from ..task import PrecheckFailure
from .graph_state import GraphState
from .utils import (
    SupervisorInGraphCommand,
    append_fstate_to_ftask,
    check_field_exists,
    mk_precheck_failure_response,
    mk_success_response,
    unpack_step_data,
)

logger = structlog.get_logger(__name__)


class BaseNodeHandler:
    def __init__(self, node_name: str):
        self.node_name = node_name

    @abstractmethod
    async def __call__(self, state: GraphState, config):
        pass


class MessageNodeHandler(BaseNodeHandler):
    @abstractmethod
    def __call__(self, state: GraphState, config) -> SupervisorInGraphCommand:
        pass


class ToolNodeHandler(BaseNodeHandler):
    def run_prechecks(
        self, fstate: FormalizationState, **kwargs
    ) -> list[PrecheckFailure]:
        return []

    @abstractmethod
    async def apply_formalization(
        self,
        fstate: FormalizationState,
        config,
        **kwargs,
    ) -> FormalizationStateUpdate:
        pass

    async def __call__(self, state: GraphState, config) -> SupervisorInGraphCommand:
        # Unpack data
        step_i, steps, step = unpack_step_data(state)
        command = step.command.root
        command_kargs: dict = command.model_dump()
        command_kargs.pop("type")
        ftask = step.task
        if ftask is None:
            raise ValueError("Missing task in ToolNodeHandler")
        fstate = ftask.last_fstate

        logger.info(
            "handler_started",
            handler=self.node_name,
            step_id=step_i,
            command_type=command.type,
        )

        # Run prechecks
        precheck_failures = check_field_exists(fstate)
        precheck_failures.extend(self.run_prechecks(fstate, **command_kargs))

        if precheck_failures:
            logger.warning(
                "precheck_failed",
                handler=self.node_name,
                step_id=step_i,
                failures=[f.field for f in precheck_failures],
            )
            command = mk_precheck_failure_response(precheck_failures, steps, step_i)
            return command
        fstate = cast(FormalizationState, fstate)

        # Apply formalization changes
        try:
            fupdate = await self.apply_formalization(fstate, config, **command_kargs)
            _, updated_ftask = append_fstate_to_ftask(
                ftask, fstate, fupdate, command.type
            )
            final_ftask = updated_ftask.model_copy(update={"status": "done"})
            logger.info(
                "handler_completed",
                handler=self.node_name,
                step_id=step_i,
                status="success",
            )
        except Exception as e:
            logger.error(
                "handler_failed",
                handler=self.node_name,
                step_id=step_i,
                error=str(e),
                error_type=type(e).__name__,
            )
            final_ftask = ftask.model_copy(
                update={
                    "status": "error",
                    "metadata": {**ftask.metadata, "error": str(e)},
                }
            )

        command = mk_success_response(steps, step_i, final_ftask)
        return command
