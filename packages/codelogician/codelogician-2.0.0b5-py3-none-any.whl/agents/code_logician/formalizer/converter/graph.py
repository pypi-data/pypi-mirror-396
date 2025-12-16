from typing import Literal

from google.protobuf.json_format import MessageToDict
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.types import Command
from pydantic import BaseModel, Field
from pydantic_ai import format_as_xml

from agents.code_logician.formalizer.analyzer.utils import find_missing_func
from agents.code_logician.formalizer.converter.base import (
    Formalization,
    FormalizationContext,
    GraphState,
    InputState,
)
from agents.code_logician.formalizer.converter.prompts import (
    final_caveats,
    iml_101,
    lang_agnostic_meta_eg_overview,
    lang_agnostic_meta_egs,
)
from agents.code_logician.imandrax_model_utils import (
    error_to_llm_context,
    eval_res_errors_to_llm_context,
)
from utils.agent.base import EndResult, ImandraMetadata, NodeMetadata
from utils.fdb.fdb import FDB, FDBFormatter, get_fdb
from utils.imandra.imandrax.async_client import get_imandrax_client
from utils.imandra.imandrax.proto_models.simple_api import EvalRes
from utils.llm import (
    anthropic_mark_cache_control,
    get_llm,
    support_anthropic_prompt_caching,
)

# current_dir = Path(__file__).resolve().parent
# fdb_table_dir = current_dir / "../../../../utils/fdb/data/table"

# embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
# general_fdb = GeneralFDB(fdb_table_dir, embeddings)
# py_fdb = PyFDB(fdb_table_dir, embeddings)


async def retrieve_conversion_context(
    src_code: str, src_lang: str, fdb: FDB
) -> FormalizationContext:
    meta_egs = []
    relevant_egs = []
    missing_funcs = []

    meta_egs: list[FDB.ConversionPair] = await fdb.get_meta_conversion(src_lang)
    relevant_egs: list[FDB.ConversionPair] = await fdb.search_conversion_by_src_code(
        src_code, src_lang, top_k=3
    )
    iml_funcs: list[FDB.IMLAPIReference] = await fdb.search_iml_func_by_src_code(
        src_code, src_lang, top_k=10
    )
    missing_funcs: list[FDB.MissingFunc] = await find_missing_func(
        fdb, src_code, src_lang
    )

    def fdb_dataclass_objs_to_dicts(dataclass_objs) -> list[dict]:
        return [o.to_dict() for o in dataclass_objs if not isinstance(o, dict)]

    return FormalizationContext(
        meta_eg=fdb_dataclass_objs_to_dicts(meta_egs),
        relevant_eg=fdb_dataclass_objs_to_dicts(relevant_egs),
        iml_func=fdb_dataclass_objs_to_dicts(iml_funcs),
        missing_func=fdb_dataclass_objs_to_dicts(missing_funcs),
    )


async def search_suggestions_by_eval_error(
    eval_res: EvalRes, fdb: FDB
) -> list[str] | None:
    """
    For each error in eval_res, retrieve one hint from similar errors.
    """
    if not eval_res.errors:
        return None

    err_strs: list[str] = [error_to_llm_context(e) for e in eval_res.errors]
    sim_errs: list[dict] = [
        (await fdb.search_error(err_str, top_k=1))[0] for err_str in err_strs
    ]
    return [e.solution_description for e in sim_errs]


async def retrieve_context(state: InputState) -> Command[Literal["convert_to_iml"]]:
    """
    <Node> Retrieve context

    context:
        - initial context:
            - IML functions
            - Language-specific meta examples
            - Relevant examples
            - Missing functions

        - error context for failed formalization (EvalRes)
    """
    print("--- Node: RETRIEVING CONTEXT ---")
    src_code = state.src_code
    src_lang = state.src_lang
    f_ctx = state.context

    update = {}

    fdb = get_fdb()

    # Retrieve initial context
    if not f_ctx.iml_func:
        init_f_ctx = await retrieve_conversion_context(src_code, src_lang, fdb)
        update["context"] = init_f_ctx

    # Retrieve error context for failed formalization
    updated_f = None
    if state.formalizations and state.formalizations[-1].eval_res.errors:
        f = state.formalizations[-1]
        suggestions_f_sim_errs: list[str] = await search_suggestions_by_eval_error(
            f.eval_res, fdb
        )
        updated_f = f.model_copy(update={"similar_error_hint": suggestions_f_sim_errs})

    if updated_f:
        update["formalizations"] = [*state.formalizations[:-1], updated_f]

    return Command(goto="convert_to_iml", update=update)


def format_formalization_msgs(
    src_code: str,
    src_lang: str,
    ctx: FormalizationContext,
    formalizations: list[Formalization],
    cache_prompt: bool,
) -> list[BaseMessage]:
    """
    Prepare messages for conversion.

    Args:
        src_code: Source code
        ctx: Retrived context
        formalizations: Previous formalizations attempts
        cache_prompt: Whether to cache the prompt

    Returns:
        The messages for the conversion.
        [
            Sys: IML 101 + lang agnostic meta examples (cache point)
            HAs: py meta examples (empty if src_lang != "python") (cache point)
            HAs: retrieved examples (empty if src_lang != "python")
            H: context message
            H: source code
            AHs: previous formalization
        ]
    """
    # System message: IML 101 + lang agnostic meta examples
    sys_msg = SystemMessage(
        content=iml_101
        + ("\n\n" + lang_agnostic_meta_eg_overview + "\n\n")
        + format_as_xml(
            lang_agnostic_meta_egs, root_tag="IML_examples", item_tag="IML_example"
        )
    )

    # Language-specific meta examples
    lang_meta_eg_msgs = []
    if ctx.meta_eg:
        for eg in ctx.meta_eg:
            lang_meta_eg_msgs.extend(
                [
                    HumanMessage(content=eg["src_code"]),
                    AIMessage(content=IMLCode(**eg).model_dump_json()),
                ]
            )

    # Relevant examples
    relevant_egs_msgs = []
    if ctx.relevant_eg:
        for eg in ctx.relevant_eg:
            relevant_egs_msgs.extend(
                [
                    HumanMessage(content=eg["src_code"]),
                    AIMessage(content=IMLCode(**eg).model_dump_json()),
                ]
            )

    # Context messages (IML API Reference and Missing functions)
    # IML API Reference
    ctx_s = "Some relevant IML API references:\n\n"
    ctx_s += FDBFormatter.format_iml_api_reference(ctx.iml_func)

    # Missing functions
    if ctx.missing_func:
        ctx_s += (
            "\n\nMissing functions in the source code and their IML counterparts:\n"
        )
        ctx_s += FDBFormatter.format_missing_func(ctx.missing_func)
    ctx_msg = HumanMessage(
        content=(
            "Here are some relevant context for the code that you are going to "
            "formalize:\n\n" + ctx_s
        )
    )

    # Source code
    src_msg = HumanMessage(
        content=(
            f"<final_caveats>\n{final_caveats}\n</final_caveats>\n\n"
            f"<source_code>\n{src_code}\n</source_code>\n\n"
        )
    )

    # Previous formalization
    prev_f_msgs = []
    for f in formalizations:
        answer_msg = AIMessage(content=f.iml_code)
        error_msg = HumanMessage(
            "Your previous attempt has errors. Here are the errors and hints "
            "(hints are from similar errors and might not be relevant):\n"
            + f"<errors>\n{eval_res_errors_to_llm_context(f.eval_res)}\n</errors>"
            + "\n\n"
            + format_as_xml(
                f.similar_error_hint,
                root_tag="reference_hints",
                item_tag="hint",
            )
            + "\n\n"
            + f"<human_suggestion>\n{f.human_error_hint}\n</human_suggestion>"
            + "\n\n Please fix the errors and try again."
        )
        prev_f_msgs.extend([answer_msg, error_msg])

    if cache_prompt:
        sys_msg = anthropic_mark_cache_control(sys_msg)
        if lang_meta_eg_msgs:
            lang_meta_eg_msgs[-1] = anthropic_mark_cache_control(lang_meta_eg_msgs[-1])

    return [
        sys_msg,
        *lang_meta_eg_msgs,
        *relevant_egs_msgs,
        ctx_msg,
        src_msg,
        *prev_f_msgs,
    ]


class IMLCode(BaseModel):
    iml_code: str = Field(description="The IML code")


async def convert_to_iml(state: InputState, config) -> Command[Literal["__end__"]]:
    """
    <Node> Convert to IML

    1. Compose formalization messages
    - IML 101 with meta examples (S)
    - (Python only) Relevant examples (few shot messages, HAHAHA...)
    - Context messages (H)
    - Source code (H)
    - (Previous formalization) IML code (A)
    - (Previous formalization) error and hints (H)

    2. Convert and check
    """
    print("--- Node: CONVERT TO IML ---")
    src_code = state.src_code
    src_lang = state.src_lang
    ctx = state.context
    formalizations = state.formalizations
    llm = get_llm(use_case="code")
    imandra_api_key = (
        config.get("configurable", {})
        .get("langgraph_auth_user", {})
        .get("imandra_api_key")
    )
    cache_prompt = config.get("configurable", {}).get("cache_prompt", False)
    cache_prompt = cache_prompt and support_anthropic_prompt_caching(llm)

    msgs = format_formalization_msgs(
        src_code, src_lang, ctx, formalizations, cache_prompt
    )

    # Convert to IML
    iml_code: str = (
        await llm.with_structured_output(schema=IMLCode).ainvoke(msgs)
    ).iml_code

    # Check IML
    async with get_imandrax_client(imandra_api_key) as imx_client:
        _imx_eval_res = await imx_client.eval_src(iml_code)
        imx_eval_res = EvalRes(**MessageToDict(_imx_eval_res))

    new_f = Formalization(
        iml_code=iml_code,
        eval_res=imx_eval_res,
        error_hint=[],
    )

    update = {
        "formalizations": [*formalizations, new_f],
    }
    if imx_eval_res.errors:
        update["end_result"] = EndResult(
            result="failure",
            info="Error found in IML code.",
        )
    else:
        update["end_result"] = EndResult(
            result="success",
            info="Formalization completed.",
        )

    return Command(
        goto="__end__",
        update=update,
    )


builder = StateGraph(GraphState, input_schema=InputState)

builder.add_node(
    "retrieve_context",
    retrieve_context,
    metadata=NodeMetadata(imandra=ImandraMetadata(task_name="Retrieving context")),
)
builder.add_node(
    "convert_to_iml",
    convert_to_iml,
    metadata=NodeMetadata(
        imandra=ImandraMetadata(task_name="Formalizing Python code to IML")
    ),
)

builder.add_edge(START, "retrieve_context")


graph = builder.compile()
