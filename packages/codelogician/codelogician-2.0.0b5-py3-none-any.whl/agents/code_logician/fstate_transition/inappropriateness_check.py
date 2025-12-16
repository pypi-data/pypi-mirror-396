from utils.fdb.fdb import FDB, get_fdb

from ..base import FormalizationState, FormalizationStateUpdate
from ..tools.inappropriateness_check import find_missing_func


async def inappropriateness_check_trans(
    fstate: FormalizationState, config
) -> FormalizationStateUpdate:
    """
    <Node> Check if the Python code is within the scope of Imandra's capability.
    """
    # print("--- Node: INAPPROPRIATENESS CHECK ---")
    src_code = fstate.src_code
    src_lang = fstate.src_lang
    conv_src_info = fstate.conversion_source_info
    if conv_src_info is None:
        raise ValueError("conversion_source_info is None")

    fdb = get_fdb()
    missing_func: list[FDB.MissingFunc] = await find_missing_func(
        fdb, src_code, src_lang
    )

    # # Logging
    # inappropriateness: list[str] = [mf.src_code for mf in missing_func]
    # if missing_func:
    #     info = f"Inappropriateness found: {inappropriateness}"
    # else:
    #     info = "Passed appropriateness check."
    # print(info)

    # Update
    new_conv_src_info = conv_src_info.model_copy(update={"missing_func": missing_func})
    update = FormalizationStateUpdate(conversion_source_info=new_conv_src_info)

    return update
