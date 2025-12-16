from typing import Literal

import structlog
from langgraph.graph import START, StateGraph
from pydantic import create_model

from agents.formalizer.base import GraphConfig, GraphState, InputBase, InputState
from agents.formalizer.nodes import translate
from utils.agent.base import AgentGraph, ImandraMetadata, NodeMetadata
from utils.imandra.utils import available_reasoners

logger = structlog.get_logger("agents.formalizer.graph")


builder = StateGraph(
    GraphState,
    input_schema=InputState,
    context_schema=GraphConfig,
)
builder.add_node(
    "translate",
    translate,
    metadata=NodeMetadata(imandra=ImandraMetadata(task_name="Formalizing input")),
)

builder.add_edge(START, "translate")

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
    full_name="Reasoner Formalizer",
    use_case="formalize English prose into stuctured (formal) input for Reasoners",
    task_name="Formalize input",
    tool_description="Formalize English prose into structured (formal) Reasoner input",
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
