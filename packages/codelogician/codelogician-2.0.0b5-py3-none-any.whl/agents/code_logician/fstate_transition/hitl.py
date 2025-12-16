import structlog

from ..base import FormalizationState, FormalizationStateUpdate

logger = structlog.get_logger(__name__)


def handle_check_formalization_hitl_response(
    fstate: FormalizationState, config, hitl_response: str
) -> FormalizationStateUpdate:
    if len(hitl_response.strip()) < (len(fstate.src_code) / 10):
        logger.warning("Provided rewrite is too short, ignoring")
        return FormalizationStateUpdate()
    else:
        return FormalizationStateUpdate(src_code=hitl_response)


def handle_formalization_action_hitl_response(
    fstate: FormalizationState, config, hitl_response: str
) -> FormalizationStateUpdate:
    last_conv_f_info = fstate.conversion_failures_info[-1]
    last_conv_f_info.human_hint = hitl_response
    return FormalizationStateUpdate(
        conversion_failures_info=[
            *fstate.conversion_failures_info[:-1],
            last_conv_f_info,
        ]
    )
