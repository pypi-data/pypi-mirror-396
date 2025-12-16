import os

from utils.fdb.fdb import FDB, get_fdb

from ..base import (
    ConversionFailureInfo,
    ConversionSourceInfo,
    FormalizationState,
    FormalizationStateUpdate,
)
from ..tools.fdb import (
    search_iml_api_refs_by_eval_error,
    search_sim_errs_by_eval_error,
)

NO_CONVERSION_EXAMPLES = int(os.getenv("CL_CONFIG_NO_CONVERSION_EXAMPLES", 3))
NO_API_REFERENCES = int(os.getenv("CL_CONFIG_NO_API_REFERENCES", 10))
NO_ERROR_HINTS = int(os.getenv("CL_CONFIG_NO_ERROR_HINTS", 1))


async def need_inappropriateness_check(fstate: FormalizationState) -> bool:
    conversion_source_info: ConversionSourceInfo = fstate.conversion_source_info
    return conversion_source_info.missing_func is None


# dep: inappropriateness_check --> gather_formalization_source_info
async def gather_formalization_source_info(
    fstate: FormalizationState, config: dict, use_refactored_code: bool = False
) -> FormalizationStateUpdate:
    """
    Gather meta examples, relevant examples, and IML API references based on the
    source code.
    """
    src_code = fstate.src_code
    if use_refactored_code and fstate.refactored_code:
        src_code = fstate.refactored_code[-1][1]
    src_lang = fstate.src_lang
    curr_info: ConversionSourceInfo = fstate.conversion_source_info

    fdb = get_fdb()
    meta_egs: list[FDB.ConversionPair] = await fdb.get_meta_conversion(src_lang)
    relevant_egs: list[FDB.ConversionPair] = await fdb.search_conversion_by_src_code(
        src_code, src_lang, top_k=NO_CONVERSION_EXAMPLES
    )
    iml_ars: list[FDB.IMLAPIReference] = await fdb.search_iml_func_by_src_code(
        src_code, src_lang, top_k=NO_API_REFERENCES
    )
    new_info = curr_info.model_copy(
        update={
            "meta_eg": meta_egs,
            "relevant_eg": relevant_egs,
            "iml_api_refs": iml_ars,
        }
    )

    return FormalizationStateUpdate(conversion_source_info=new_info)


async def gather_formalization_source_info_trans(
    fstate: FormalizationState, config
) -> FormalizationStateUpdate:
    use_refactored_code = len(fstate.refactored_code) > 0
    return await gather_formalization_source_info(fstate, config, use_refactored_code)


async def gather_formalization_failure_info(
    fstate: FormalizationState, config
) -> FormalizationStateUpdate:
    iml_code = fstate.iml_code
    eval_res = fstate.eval_res
    if iml_code is None:
        raise ValueError("IML code is required")
    if eval_res is None:
        raise ValueError("eval_res is required")

    fdb: FDB = get_fdb()
    curr_failures: list[ConversionFailureInfo] = fstate.conversion_failures_info

    # RAG: similar errors
    sim_errs: list[FDB.Error] = await search_sim_errs_by_eval_error(fdb, eval_res)

    # RAG: more IML API references
    source_info = fstate.conversion_source_info
    existing_refs = source_info.iml_api_refs if source_info else []
    for f in curr_failures:
        existing_refs.extend(f.iml_api_refs)
    iml_api_refs: list[FDB.IMLAPIReference] = await search_iml_api_refs_by_eval_error(
        fdb, iml_code, eval_res, existing_refs
    )

    # Populate
    new_info = ConversionFailureInfo(
        iml_code=iml_code,
        eval_res=eval_res,
        sim_errs=sim_errs,
        iml_api_refs=iml_api_refs,
        linting_errors=fstate.linting_errors,
    )
    new_failures = [*curr_failures, new_info]
    return FormalizationStateUpdate(conversion_failures_info=new_failures)
