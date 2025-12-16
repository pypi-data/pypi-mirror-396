from typing import Literal

import structlog
from langgraph.graph import START, StateGraph
from pydantic import create_model

from agents.reasoner_invoker.base import (
    GraphConfig,
    GraphState,
    InputState,
)
from agents.reasoner_invoker.nodes import (
    attempt_change,
    call_reasoner,
    confirm_attempt_change,
    retrieve_correction_context,
)
from utils.agent.base import AgentGraph, ImandraMetadata, InputBase, NodeMetadata
from utils.imandra.utils import available_reasoners

logger = structlog.get_logger("agents.reasoner_invoker.graph")


builder = StateGraph(
    GraphState,
    input_schema=InputState,
    context_schema=GraphConfig,
)
builder.add_node(
    "call_reasoner",
    call_reasoner,
    metadata=NodeMetadata(imandra=ImandraMetadata(task_name="Invoking reasoner")),
)
builder.add_node(
    "confirm_attempt_change",
    confirm_attempt_change,
    metadata=NodeMetadata(
        imandra=ImandraMetadata(task_name="Confirming attempt to fix reasoner input")
    ),
)
builder.add_node(
    "retrieve_correction_context",
    retrieve_correction_context,
    metadata=NodeMetadata(
        imandra=ImandraMetadata(
            task_name="Retrieving context for fixing reasoner input"
        )
    ),
)
builder.add_node(
    "attempt_change",
    attempt_change,
    metadata=NodeMetadata(
        imandra=ImandraMetadata(task_name="Attempting to fix reasoner input")
    ),
)

builder.add_edge(START, "call_reasoner")

graph = builder.compile()


def input_schema():
    return create_model(
        "InputState",
        __base__=InputBase,
        reasoner=(Literal[*available_reasoners()], ...),
        **{
            k: (v.annotation, v)
            for k, v in InputState.model_fields.items()
            if k != "reasoner"
        },
    )


agent = AgentGraph(
    agent_type="interruptible_agent",
    full_name="Reasoner Invoker",
    use_case="invoke Reasoners with provided input",
    task_name="Call reasoner",
    tool_description="""Invoke a Reasoner with user-provided input""",
    input_schema=input_schema,
    state_schema=GraphState,
    config=GraphConfig,
)

if __name__ == "__main__":
    import datetime
    from pathlib import Path

    with Path(f"mermaid_{datetime.datetime.now().strftime('%m%d%H%M')}.md").open(
        "w"
    ) as f:
        mermaid: str = graph.get_graph(xray=True).draw_mermaid()
        mermaid = "```mermaid\n" + mermaid + "\n```"
        f.write(mermaid)
