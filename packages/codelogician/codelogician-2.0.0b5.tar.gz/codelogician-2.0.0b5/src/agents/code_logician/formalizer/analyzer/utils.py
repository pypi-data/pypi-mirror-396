from agents.code_logician.formalizer.analyzer.source_analysis import (
    check_function_usage,
)
from utils.fdb.fdb import FDB


async def find_missing_func(
    fdb: FDB,
    src_code: str,
    src_lang: str | None = None,
) -> list[dict]:
    """
    Find inappropriate functions/operators in source code that are not supported by
    Imandra.

    Args:
        fdb: Formalism database instance
        src_code: Source code to analyze
        src_lang: Source code language

    Returns:
        List of inappropriate function/operator names found in the source code

    Example:
        >>> src_code = "def foo(x): return x ^ 2 + math.sqrt(x)"
        >>> missing_func = find_missing_func(fdb, src_code, "python")
        >>> for mf in missing_func:
            print(mf['src_code'])
        int.__xor__
        math.sqrt
    """
    if src_lang.lower() != "python":
        return []
    all_missing_func: list[FDB.MissingFunc] = await fdb.get_all_missing_func()

    # TODO: this should be retrieved from the database
    operator_override = {
        "int.__xor__": "^",
    }

    # Filter missing func
    missing_func: list[FDB.MissingFunc] = []
    for mf in all_missing_func:
        mf_in_src: str = mf.src_code
        if operator := operator_override.get(mf_in_src):
            if operator in src_code:
                missing_func.append(mf)
        else:
            if check_function_usage(src_code, mf_in_src):
                missing_func.append(mf)
    return [mf.to_dict() for mf in missing_func]
