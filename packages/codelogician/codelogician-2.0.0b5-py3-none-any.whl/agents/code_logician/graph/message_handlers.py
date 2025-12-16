from typing import Any

import structlog

from utils.fdb.fdb import FDB, get_fdb

from ..command import (
    EmbedCommand,
    GetStateElementCommand,
    SearchFDBCommand,
)
from ..tools.code_search import EMBEDDING_METADATA, embed_code, embed_query
from .base_handlers import MessageNodeHandler, SupervisorInGraphCommand
from .graph_state import GraphState
from .utils import unpack_step_data

logger = structlog.get_logger(__name__)


class SearchFDBNodeHandler(MessageNodeHandler):
    def __init__(self):
        super().__init__("search_fdb_node")

    async def __call__(self, state: GraphState, config) -> SupervisorInGraphCommand:
        fdb: FDB = get_fdb()
        step_i, steps, step = unpack_step_data(state)
        command: SearchFDBCommand = step.command.root

        logger.info(
            "fdb_search_started",
            handler="search_fdb_node",
            step_id=step_i,
            search_name=command.name,
            query=command.query,
            top_k=command.top_k,
        )

        try:
            res = await fdb.search(
                name=command.name,
                query=command.query,
                top_k=command.top_k,
                as_dict=True,
            )
            step.message = {"fdb_search_res": res}
            logger.info(
                "fdb_search_completed",
                handler="search_fdb_node",
                step_id=step_i,
                results_count=len(res) if isinstance(res, list) else 1,
            )
        except FDB.FDBSearchError as e:
            step.message = {"error": str(e)}
            logger.error(
                "fdb_search_failed",
                handler="search_fdb_node",
                step_id=step_i,
                error=str(e),
            )

        steps[step_i] = step
        return SupervisorInGraphCommand(
            update={"steps": steps}, goto="code_logician_supervisor"
        )


class GetStateElementNodeHandler(MessageNodeHandler):
    def __init__(self):
        super().__init__("get_state_element_node")

    async def __call__(self, state: GraphState, config) -> SupervisorInGraphCommand:
        step_i, steps, step = unpack_step_data(state)
        fstate = step.last_fstate
        command: GetStateElementCommand = step.command.root
        element_names: list[str] = command.element_names

        logger.info(
            "get_state_element_started",
            handler="get_state_element_node",
            step_id=step_i,
            element_names=element_names,
            has_fstate=fstate is not None,
        )

        if fstate is None:
            message = {"error": "Missing formalization state"}
            logger.warning(
                "get_state_element_no_fstate",
                handler="get_state_element_node",
                step_id=step_i,
            )
        else:
            message = {}
            for name in element_names:
                # NOTE: we don't handle invalid names
                if name in {*fstate.model_fields_set, "test_cases"}:
                    message[name] = getattr(fstate, name)
            logger.info(
                "get_state_element_completed",
                handler="get_state_element_node",
                step_id=step_i,
                retrieved_fields=list(message.keys()),
            )

        step.message = message
        step.task = None
        steps[step_i] = step
        return SupervisorInGraphCommand(
            update={"steps": steps}, goto="code_logician_supervisor"
        )


class EmbedNodeHandler(MessageNodeHandler):
    def __init__(self):
        super().__init__("embed_node")

    async def __call__(self, state: GraphState, config) -> SupervisorInGraphCommand:
        step_i, steps, step = unpack_step_data(state)
        fstate = step.last_fstate
        command: EmbedCommand = step.command.root
        query = command.query

        logger.info(
            "embed_started",
            handler="embed_node",
            step_id=step_i,
            has_fstate=fstate is not None,
            query_provided=query is not None,
        )

        if fstate is None:
            message = {"error": "Missing formalization state"}
            logger.warning(
                "get_state_element_no_fstate",
                handler="get_state_element_node",
                step_id=step_i,
            )
        else:
            message: dict[str, Any] = {
                "metadata": EMBEDDING_METADATA,
            }
            if query is not None:
                query_embedding = embed_query(query)
                message["query_embedding"] = query_embedding
            else:
                src_code = fstate.src_code
                src_lang = fstate.src_lang
                src_embeddings = embed_code(src_code, src_lang)
                src_embeddings = [se.model_dump() for se in src_embeddings]
                message["src_embeddings"] = src_embeddings

                iml_code = fstate.iml_code
                if iml_code is not None:
                    iml_embeddings = embed_code(iml_code, "iml")
                    iml_embeddings = [ie.model_dump() for ie in iml_embeddings]
                    message["iml_embeddings"] = iml_embeddings

        step.message = message
        step.task = None
        steps[step_i] = step
        return SupervisorInGraphCommand(
            update={"steps": steps}, goto="code_logician_supervisor"
        )
