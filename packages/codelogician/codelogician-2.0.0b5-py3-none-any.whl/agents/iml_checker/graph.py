"""
Iml Checker

Usage
- Could be used standalone
- Or as a sub-graph of CodeLogician (Python) / CodeLogician (General)

                         +-----------+
                         | __start__ |
                         +-----------+
                                *
                                *
                                *
                       +---------------+
                       | imandra_check |
                       +---------------+..
                   ....         .         ....
               ....              .            ...
             ..                  .               ....
+----------------+          +--------+               ..
| retrieve_hints |          | decomp |           ....
+----------------+.         +--------+        ...
                   ....          .        ....
                       ....     .     ....
                           ..   .   ..
                          +---------+
                          | __end__ |
                          +---------+

      (fail)                   (success)      (success)
"""

from collections.abc import Callable
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langgraph.graph import START, StateGraph

from agents.iml_checker.base import GraphConfig, GraphState, InputState
from agents.iml_checker.nodes import (
    imandra_check,
    # mk_retrieve_hints,
    retrieve_hints,
)
from utils.agent.base import AgentGraph, ImandraMetadata, NodeMetadata

# from utils.fdb.fdb import get_fdb

current_dir = Path(__file__).resolve().parent
fdb_table_dir = current_dir / "../../utils/fdb/data/table"


def get_graph_builder(retrieve_hints: Callable[[GraphState], GraphState]):
    """
    node retrieve_hints depends on fdb
    """
    builder = StateGraph(
        GraphState, input_schema=InputState, context_schema=GraphConfig
    )

    # Add nodes
    builder.add_node(
        "imandra_check",
        imandra_check,
        metadata=NodeMetadata(imandra=ImandraMetadata(task_name="Validating IML code")),
    )  # imandra call
    builder.add_node(
        "retrieve_hints",
        retrieve_hints,
        metadata=NodeMetadata(
            imandra=ImandraMetadata(task_name="Suggesting hints from similar errors")
        ),
    )

    # Add edges
    builder.add_edge(START, "imandra_check")
    return builder


# Default compiled graph
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
# fdb = get_fdb()
# retrieve_hints = mk_retrieve_hints(fdb)
builder = get_graph_builder(retrieve_hints)


def get_graph(checkpointer=None):
    return builder.compile(
        checkpointer=checkpointer,
    )


graph = builder.compile()

agent = AgentGraph(
    agent_type="one_shot_tool",
    full_name="Imandra Checker",
    use_case="for IML code, check with Imandra to see if the code is correct",
    task_name="Handle IML code",
    tool_description="""Admit IML code and check for errors. Used when the user \
        request is about checking IML code and there's IML code present \
        in the user request.""",
    input_schema=InputState,
    state_schema=GraphState,
    config=GraphConfig,
)

if __name__ == "__main__":
    import datetime

    with Path(f"mermaid_{datetime.datetime.now().strftime('%m%d%H%M')}.md").open(
        "w"
    ) as f:
        mermaid: str = graph.get_graph(xray=True).draw_mermaid()
        mermaid = "```mermaid\n" + mermaid + "\n```"
        f.write(mermaid)
