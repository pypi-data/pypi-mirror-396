from typing import Any, Protocol

from ..base import FormalizationState, FormalizationStateUpdate
from .fdb import (
    gather_formalization_failure_info,
    gather_formalization_source_info,
    gather_formalization_source_info_trans,
)
from .formalize_to_iml import admit_model, convert_to_iml, set_model
from .functional_refactor import functional_refactoring_trans
from .gen_vgs import gen_vgs_trans
from .hitl import (
    handle_check_formalization_hitl_response,
    handle_formalization_action_hitl_response,
)
from .inappropriateness_check import inappropriateness_check_trans
from .inject_context import add_custom_examples, inject_context
from .opaque import choose_approximation, choose_assumptions
from .region_decomp import gen_region_decomp, gen_test_cases

__all__ = [
    "add_custom_examples",
    "admit_model",
    "choose_approximation",
    "choose_assumptions",
    "convert_to_iml",
    "functional_refactoring_trans",
    "gather_formalization_failure_info",
    "gather_formalization_source_info",
    "gather_formalization_source_info_trans",
    "gen_region_decomp",
    "gen_test_cases",
    "gen_vgs_trans",
    "handle_check_formalization_hitl_response",
    "handle_formalization_action_hitl_response",
    "inappropriateness_check_trans",
    "inject_context",
    "set_model",
]


class FormalizationStateTransition(Protocol):
    __name__: str

    def __call__(
        self,
        fstate: FormalizationState,
        config: Any,
        *args,
        **kwargs,
    ) -> FormalizationStateUpdate: ...


class AsyncFormalizationStateTransition(Protocol):
    __name__: str

    async def __call__(
        self,
        fstate: FormalizationState,
        config: Any,
        *args,
        **kwargs,
    ) -> FormalizationStateUpdate: ...
