from typing import cast

import structlog

from ..base import FormalizationState, FormalizationStateUpdate
from ..tools.functional_refactor import functional_refactoring

logger = structlog.get_logger(__name__)


async def functional_refactoring_trans(
    fstate: FormalizationState, config
) -> FormalizationStateUpdate:
    """
    <Node> Functional refactoring
    """

    src_lang = fstate.src_lang
    src_code = fstate.src_code

    refactoring_res = await functional_refactoring(
        src_lang=src_lang,
        src_code=src_code,
        refactoring_min_lines=config.get("configurable", {}).get(
            "refactoring_min_lines", 50
        ),
        use_batch_refactoring=cast(
            bool, config.get("configurable", {}).get("use_batch_refactoring", True)
        ),
    )

    return FormalizationStateUpdate(refactored_code=refactoring_res)
