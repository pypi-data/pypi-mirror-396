from utils.fdb.fdb import FDB

from ..base import (
    ConversionSourceInfo,
    FormalizationState,
    FormalizationStateUpdate,
)


def inject_context(
    fstate: FormalizationState, config: dict, context: str
) -> FormalizationStateUpdate:
    """
    Inject additional context into ConversionSourceInfo.user_inject.
    """
    curr_info: ConversionSourceInfo = fstate.conversion_source_info

    # TODO: limit length of context
    # TODO: detect malicious context

    new_info = curr_info.model_copy(
        update={
            "user_inject": context,
        }
    )

    return FormalizationStateUpdate(conversion_source_info=new_info)


def mk_custom_example(
    src_code: str, iml_code: str, src_lang: str
) -> FDB.ConversionPair:
    return FDB.ConversionPair(
        src_code=src_code,
        src_lang=src_lang,
        refactored_code=[],
        src_tags=[],
        iml_code=iml_code,
        iml_tags=[],
        is_meta_eg=False,
        is_custom_eg=True,
    )


def add_custom_examples(
    fstate: FormalizationState,
    config: dict,
    examples: list[tuple[str, str]],
) -> FormalizationStateUpdate:
    src_lang = fstate.src_lang
    curr_info: ConversionSourceInfo = fstate.conversion_source_info

    relevant_egs = curr_info.relevant_eg

    # TODO: add guardrails for malicious content

    custom_egs = [
        mk_custom_example(src_code, iml_code, src_lang)
        for src_code, iml_code in examples
    ]

    new_info = ConversionSourceInfo.model_validate(
        curr_info.model_dump() | {"relevant_eg": relevant_egs + custom_egs}
    )

    return FormalizationStateUpdate(conversion_source_info=new_info)
