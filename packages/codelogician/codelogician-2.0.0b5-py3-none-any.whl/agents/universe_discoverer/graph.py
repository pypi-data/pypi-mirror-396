import os
from functools import lru_cache

import structlog
from langchain_classic.callbacks.tracers.logging import LoggingCallbackHandler
from langgraph.graph import END, START, StateGraph

from agents.universe_discoverer.base import (
    GraphConfig,
    GraphState,
    InputState,
)
from utils.agent.base import AgentGraph, EndResult, ImandraMetadata, NodeMetadata

# from langchain_classic.chains import GraphCypherQAChain
# from langchain_classic.graphs import Neo4jGraph
# from langchain_community.chains import GraphCypherQAChain
# from langchain_community.graphs import Neo4jGraph
from utils.langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from utils.llm import get_llm

logger = structlog.get_logger("agents.universe_discoverer.graph")


@lru_cache(maxsize=4)
def _get_cypher_chain(llm_model_name: str | None):
    neo4j_graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
    )

    cypher_chain = GraphCypherQAChain.from_llm(
        get_llm(use_case="code"),
        graph=neo4j_graph,
        verbose=False,
        return_intermediate_steps=True,
        allow_dangerous_requests=True,
    )
    cypher_chain.callbacks = [LoggingCallbackHandler(logger)]
    return cypher_chain


async def discover(state: InputState, config):
    query = state.query
    llm_model_name = config.get("configurable", {}).get("llm_model_name")
    cypher_chain = _get_cypher_chain(llm_model_name)

    response = (await cypher_chain.ainvoke({"query": query}))["result"]

    return {
        "query": query,
        "response": response,
        "end_result": EndResult(result="success"),
    }


builder = StateGraph(
    GraphState,
    input_schema=InputState,
    context_schema=GraphConfig,
)
builder.add_node(
    "discover",
    discover,
    metadata=NodeMetadata(imandra=ImandraMetadata(task_name="Searching the Universe")),
)
builder.add_edge(START, "discover")
builder.add_edge("discover", END)

graph = builder.compile()

agent = AgentGraph(
    agent_type="one_shot_tool",
    full_name="Universe Discoverer",
    use_case=(
        "search the universe knowledge base to find out what tools, reasoners and "
        "agents are available"
    ),
    task_name="Discover Imandra Universe",
    tool_description="""Call Universe Discoverer agent to search the universe \
        knowledge base. Used when the user request is about what tools, reasoners and \
        agents are available (in the Imandra Universe).""",
    input_schema=InputState,
    state_schema=GraphState,
    config=GraphConfig,
)


if __name__ == "__main__":
    from pathlib import Path

    with (Path(__file__).parent.parent.parent / "mermaid.md").open("w") as f:
        mermaid: str = graph.get_graph(xray=True).draw_mermaid()
        mermaid = "```mermaid\n" + mermaid + "\n```"
        f.write(mermaid)
