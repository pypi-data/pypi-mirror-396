import asyncio
import os
import textwrap
from typing import cast

from langsmith import traceable
from pydantic import BaseModel, Field

from agents.code_logician.imandrax_model_utils import error_to_llm_context
from utils.fdb.fdb import FDB, FDBFormatter
from utils.imandra.imandrax.proto_models.simple_api import EvalRes
from utils.llm import get_llm

N_CONVERSION_EXAMPLES = int(os.getenv("CL_CONFIG_NO_CONVERSION_EXAMPLES", 3))
N_API_REFERENCE_QUERY = int(os.getenv("CL_CONFIG_N_API_REFERENCE_QUERY", 2))
N_API_REFERENCE_PER_QUERY = int(os.getenv("CL_CONFIG_NO_API_REFERENCES", 5))
N_HINTS_PER_ERROR = int(os.getenv("CL_CONFIG_NO_ERROR_HINTS", 3))
N_NON_PO_ERROR = 1
N_PO_ERROR = 1


async def search_sim_errs_by_eval_error(fdb: FDB, eval_res: EvalRes) -> list[FDB.Error]:
    """
    For each error in eval_res, retrieve hints from similar errors.
    """
    eval_err = [
        *eval_res.errors[:N_NON_PO_ERROR],
        *eval_res.po_errors[:N_PO_ERROR],
    ]
    if eval_err is None:
        raise ValueError("eval_res.errors is required")

    err_strs: list[str] = [error_to_llm_context(e) for e in eval_err]
    sim_errs: list[FDB.Error] = []
    fdb_tasks = [
        fdb.search_error(err_str, top_k=N_HINTS_PER_ERROR) for err_str in err_strs
    ]
    results = await asyncio.gather(*fdb_tasks)
    for r in results:
        if r:
            sim_errs.extend(r)
    return sim_errs


@traceable
async def search_iml_api_refs_by_eval_error(
    fdb: FDB,
    iml_code: str,
    eval_res: EvalRes,
    existing_iml_api_refs: list[FDB.IMLAPIReference] | None = None,
) -> list[FDB.IMLAPIReference]:
    """
    For the first error in eval_err, retrieve new IML API references as re-try context.
    """
    eval_err = eval_res.errors
    if eval_err is None:
        raise ValueError("eval_res.errors is required")
    err_str = error_to_llm_context(eval_err[0])

    if existing_iml_api_refs is None:
        existing_iml_api_refs_str = "None"
    else:
        existing_iml_api_refs_str = ""
        for ref in existing_iml_api_refs:
            ref_str = ref.name if ref.module == "" else f"{ref.module}.{ref.name}"
            ref_str = f"`{ref_str}`"
            existing_iml_api_refs_str += f"- {ref_str}\n"

    # Query
    llm = get_llm(model_name="claude-3-5-haiku-latest")
    message = textwrap.dedent("""
        A user is writing IML code and encountered an error. We have a vector database
        of IML API references. You are given the IML code, error message, and the
        existing IML API references. Please come up with a query to retrieve new IML API
        references that will be helpful for the user to fix the error.

        Due to the embedding mechanism of the vector database, the query should be a
        natural language description of the pattern of the relevant IML API references
        you want to find.

        For example, the top 3 results of "create a list from a single element"
        will be IML API references of `List.return`(function), `List.empty`
        (function), and `list` (type). The results are ordered by relevance.

        Other example queries:
            "Remove duplicates from a list",
            "Merge two arrays without duplicates",
            "Accumulating multiple validation errors",
            "Chain operations that might fail",
            "Reduce collection to single value",

        ---

        IML code:
        ```
        {iml_code}
        ```

        Error message:

        {err_str}

        Already retrieved IML API references (skip these):
        {existing_iml_api_refs_str}

        Only return the queries (1-3), no other explanation or comments.
        Return as per json schema.
    """)
    message = message.format(
        iml_code=iml_code,
        err_str=err_str,
        existing_iml_api_refs_str=existing_iml_api_refs_str,
    )

    class Queries(BaseModel):
        queries: list[str] = Field(description="List of queries")

    res = await llm.with_structured_output(Queries).ainvoke(message)
    res = cast(Queries, res)
    queries = res.queries

    # Search
    exclude_ids = (
        [ref.id for ref in existing_iml_api_refs] if existing_iml_api_refs else None
    )

    fdb_tasks = [
        fdb.search_iml_func(
            query=query,
            top_k=N_API_REFERENCE_PER_QUERY,
            exclude_ids=exclude_ids,
        )
        for query in queries[:N_API_REFERENCE_QUERY]
    ]
    fdb_results = await asyncio.gather(*fdb_tasks)
    iml_api_refs: list[FDB.IMLAPIReference] = []
    for r in fdb_results:
        if r:
            iml_api_refs.extend(r)
    return iml_api_refs


async def search_conversion_examples(fdb: FDB, src_code: str, src_lang: str) -> str:
    """
    Use vector search to retrieve conversion examples. Each example contains a string
    of source code, and its corresponding IML code.

    Args:
        src_code: str
            The source code to search with
        src_lang: str
            The language of the source code

    Returns:
        str: Conversion examples.
    """
    conversion_examples: list[
        FDB.ConversionPair
    ] = await fdb.search_conversion_by_src_code(
        src_code=src_code, src_lang=src_lang, top_k=N_CONVERSION_EXAMPLES
    )
    return FDBFormatter.format_conversion_pair(conversion_examples)


async def search_iml_code_examples(fdb: FDB, code: str) -> str:
    """
    Use vector search to find similar IML code examples from our database.

    The search works by comparing your code snippet against embedded vectors of known
    working IML programs. Here are two of many possible usages:
    1. When you have a partial IML implementation and want to see complete working
    examples.
    2. When your code has errors and you want to see correct implementations for
    reference.

    code: str
        The IML code snippet to search with
    """
    iml_code_examples: list[FDB.IMLCode] = await fdb.search_iml_code_by_iml_code(
        iml_code=code,
        top_k=N_CONVERSION_EXAMPLES,
    )
    return FDBFormatter.format_iml_code(iml_code_examples)
