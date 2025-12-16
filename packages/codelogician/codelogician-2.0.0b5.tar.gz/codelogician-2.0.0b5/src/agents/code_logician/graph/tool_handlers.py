import structlog

from ..base import (
    VG,
    FormalizationState,
    FormalizationStateUpdate,
    FormalizationStatus,
    RegionDecomp,
)
from ..base.model_utils.iml import parse_iml
from ..fstate_transition import (
    add_custom_examples,
    admit_model,
    choose_approximation,
    choose_assumptions,
    convert_to_iml,
    functional_refactoring_trans,
    gather_formalization_failure_info,
    gen_region_decomp,
    gen_test_cases,
    gen_vgs_trans,
    inappropriateness_check_trans,
    inject_context,
    set_model,
)
from ..task import PrecheckFailure
from .base_handlers import ToolNodeHandler
from .utils import check_field_exists

logger = structlog.get_logger(__name__)


class EditStateElementNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("edit_state_element_node")

    def run_prechecks(
        self, fstate: FormalizationState, *, update: dict
    ) -> list[PrecheckFailure]:
        # Reject fstatus change
        if "status" in update:
            return [
                PrecheckFailure(
                    field="command.args",
                    reason="Formalization status cannot be changed directly",
                ),
            ]
        for field_name in ["iml_model", "tof_definitions", "linting_errors"]:
            if field_name in update:
                return [
                    PrecheckFailure(
                        field="command.args",
                        reason=f"Formalization {field_name} is derived from `iml_code` "
                        "and cannot be changed directly",
                    ),
                ]

        return []

    async def apply_formalization(
        self, fstate: FormalizationState, config, *, update: dict
    ) -> FormalizationStateUpdate:
        # Change fstatus if there's IML change
        if "iml_code" in update:
            iml_code = update["iml_code"]
            parsed_res = parse_iml(iml_code)
            if parsed_res is None:
                logger.warning("IML code has syntax errors and cannot be parsed")
                (
                    iml_model,
                    top_defs,
                    linting_errors,
                    decomp_req_data,
                    verify_req_data,
                ) = iml_code, [], [], [], []
            else:
                (
                    iml_model,
                    top_defs,
                    linting_errors,
                    decomp_req_data,
                    verify_req_data,
                ) = parsed_res
            region_decomps = [
                RegionDecomp(data=decomp_req_data_item)
                for decomp_req_data_item in decomp_req_data
            ]
            vgs = [
                VG(data=verify_req_data_item)
                for verify_req_data_item in verify_req_data
            ]
            update1 = {
                "status": FormalizationStatus.UNKNOWN,
                "eval_res": None,
                "iml_model": iml_model,
                "top_definitions": top_defs,
                "linting_errors": linting_errors,
                "region_decomps": region_decomps,
                "vgs": vgs,
            }
            update |= update1
        return FormalizationStateUpdate(
            **{k: v for k, v in update.items() if k in FormalizationState.model_fields}
        )


class CheckFormalizationNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("check_formalization_node")

    async def apply_formalization(
        self, fstate: FormalizationState, config, **kwargs
    ) -> FormalizationStateUpdate:
        return await inappropriateness_check_trans(fstate, config)


class GenProgramRefactorNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("gen_program_refactor_node")

    async def apply_formalization(
        self, fstate: FormalizationState, config, **kwargs
    ) -> FormalizationStateUpdate:
        return await functional_refactoring_trans(fstate, config)


class InjectFormalizationContextNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("inject_formalization_context_node")

    async def apply_formalization(
        self, fstate: FormalizationState, config, *, context: str
    ) -> FormalizationStateUpdate:
        return inject_context(fstate, config, context)


class InjectCustomExamplesNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("inject_custom_examples_node")

    async def apply_formalization(
        self,
        fstate: FormalizationState,
        config,
        *,
        examples: list[tuple[str, str]],
    ) -> FormalizationStateUpdate:
        return add_custom_examples(fstate, config, examples)


class GenFormalizationFailureDataNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("gen_formalization_failure_data_node")

    def run_prechecks(
        self, fstate: FormalizationState, **kwargs
    ) -> list[PrecheckFailure]:
        precheck_failures = []
        precheck_failures.extend(check_field_exists(fstate, "iml_code"))
        precheck_failures.extend(check_field_exists(fstate, "eval_res"))
        precheck_failures.extend(
            check_field_exists(
                fstate,
                "eval_res",
                "errors",
                message="No evaluation errors found",
                use_bool_val=True,
            )
        )
        return precheck_failures

    async def apply_formalization(
        self, fstate: FormalizationState, config, **kwargs
    ) -> FormalizationStateUpdate:
        return await gather_formalization_failure_info(fstate, config)


class GenModelNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("gen_model_node")

    async def apply_formalization(
        self, fstate: FormalizationState, config, **kwargs
    ) -> FormalizationStateUpdate:
        return await convert_to_iml(fstate, config)


class AdmitModelNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("admit_model_node")

    def run_prechecks(
        self, fstate: FormalizationState, **kwargs
    ) -> list[PrecheckFailure]:
        return check_field_exists(fstate, "iml_code")

    async def apply_formalization(
        self, fstate: FormalizationState, config, **kwargs
    ) -> FormalizationStateUpdate:
        return await admit_model(fstate, config)


class SetModelNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("set_model_node")

    async def apply_formalization(
        self, fstate: FormalizationState, config, *, model: str
    ) -> FormalizationStateUpdate:
        # NOTE: here the parameter is called model but it's actually the IML code that
        # could contain requests
        return await set_model(fstate, config, model)


class GenVgsNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("gen_vgs_node")

    def run_prechecks(
        self, fstate: FormalizationState, *, description: str
    ) -> list[PrecheckFailure]:
        precheck_failures = []
        precheck_failures.extend(check_field_exists(fstate, "iml_model"))

        # Precheck: formalization status
        if fstate.status in [
            FormalizationStatus.INADMISSIBLE,
            FormalizationStatus.UNKNOWN,
        ]:
            precheck_failures.append(
                PrecheckFailure(
                    field="status",
                    reason=f"Invalid formalization status: {fstate.status}",
                )
            )
        return precheck_failures

    async def apply_formalization(
        self, fstate: FormalizationState, config, *, description: str
    ) -> FormalizationStateUpdate:
        return await gen_vgs_trans(fstate, config, description=description)


class GenRegionDecompsNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("gen_region_decomps_node")

    def run_prechecks(
        self, fstate: FormalizationState, *, function_name: str | None
    ) -> list[PrecheckFailure]:
        precheck_failures = []
        precheck_failures.extend(check_field_exists(fstate, "iml_model"))

        # Precheck: formalization status
        if fstate.status in [
            FormalizationStatus.INADMISSIBLE,
            FormalizationStatus.UNKNOWN,
            FormalizationStatus.ADMITTED_WITH_OPAQUENESS,
        ]:
            precheck_failures.append(
                PrecheckFailure(
                    field="status",
                    reason=f"Invalid formalization status: {fstate.status}",
                )
            )
        return precheck_failures

    async def apply_formalization(
        self, fstate: FormalizationState, config, *, function_name: str | None
    ) -> FormalizationStateUpdate:
        if function_name is None:
            method = "comments"
            nat_lang_req = None
        else:
            method = "nat_lang_req"
            nat_lang_req = f"decompose {function_name}"
        return await gen_region_decomp(fstate, config, method, nat_lang_req)


class GenTestCasesNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("gen_test_cases_node")

    def run_prechecks(
        self, fstate: FormalizationState, *, decomp_idx: int
    ) -> list[PrecheckFailure]:
        precheck_failures = []
        region_decomps = fstate.region_decomps

        raw_decomp_exist = False
        for decomp in region_decomps:
            if decomp.raw is not None:
                raw_decomp_exist = True
                break
        if not raw_decomp_exist:
            precheck_failures.append(
                PrecheckFailure(
                    field="region_decomps",
                    reason="No raw decomp found",
                )
            )

        if (decomp_idx + 1) > len(fstate.region_decomps):
            precheck_failures.append(
                PrecheckFailure(
                    field="command.args",
                    reason=f"Invalid decomp_idx: {decomp_idx}",
                )
            )

        decomp = fstate.region_decomps[decomp_idx]
        if (decomp_res := decomp.res) is None or decomp_res.errors:
            precheck_failures.append(
                PrecheckFailure(
                    field="region_decomps",
                    reason=f"Invalid decomp {decomp_idx}: {decomp}",
                )
            )
        return precheck_failures

    async def apply_formalization(
        self, fstate: FormalizationState, config, *, decomp_idx: int
    ) -> FormalizationStateUpdate:
        return await gen_test_cases(fstate, config, decomp_idx)


class SuggestAssumptionsNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("suggest_assumptions_node")

    def run_prechecks(
        self, fstate: FormalizationState, **kwargs
    ) -> list[PrecheckFailure]:
        """
        Note: precheck will always fail because we don't have any candidates
        """
        from functools import reduce

        precheck_failures = []

        if len(fstate.opaque_funcs) == 0:
            precheck_failures.append(
                PrecheckFailure(field="opaques", reason="No opaque functions")
            )

        all_candidates = reduce(
            list.__add__,
            [
                opaque_func.opaque_data.assumption_candidates
                for opaque_func in fstate.opaque_funcs
                if opaque_func.opaque_data is not None
            ],
            [],
        )
        if len(all_candidates) == 0:
            precheck_failures.append(
                PrecheckFailure(field="opaques", reason="No assumption candidates")
            )

        return precheck_failures

    async def apply_formalization(
        self, fstate: FormalizationState, config, *, feedback: str
    ) -> FormalizationStateUpdate:
        return await choose_assumptions(fstate, config, feedback)


class SuggestApproximationNodeHandler(ToolNodeHandler):
    def __init__(self):
        super().__init__("suggest_approximation_node")

    def run_prechecks(
        self, fstate: FormalizationState, **kwargs
    ) -> list[PrecheckFailure]:
        """
        Note: precheck will always fail because we don't have any candidates
        """
        from functools import reduce

        precheck_failures = []

        if len(fstate.opaque_funcs) == 0:
            precheck_failures.append(
                PrecheckFailure(field="opaques", reason="No opaque functions")
            )

        all_candidates = reduce(
            list.__add__,
            [
                opaque_func.opaque_data.approximation_candidates
                for opaque_func in fstate.opaque_funcs
                if opaque_func.opaque_data is not None
            ],
            [],
        )
        if len(all_candidates) == 0:
            precheck_failures.append(
                PrecheckFailure(field="opaques", reason="No approximation candidates")
            )

        return precheck_failures

    async def apply_formalization(
        self, fstate: FormalizationState, config, *, feedback: str
    ) -> FormalizationStateUpdate:
        return await choose_approximation(fstate, config, feedback)
