import structlog
from langgraph.graph import START, StateGraph

from agents.prose_reasoner.base import (
    GraphConfig,
    GraphState,
    InputState,
)
from agents.prose_reasoner.nodes import formalize, invoke
from utils.agent.base import AgentGraph, ImandraMetadata, NodeMetadata

logger = structlog.get_logger("agents.prose_reasoner.graph")


builder = StateGraph(
    GraphState,
    input_schema=InputState,
    context_schema=GraphConfig,
)
builder.add_node(
    "formalize",
    formalize,
    metadata=NodeMetadata(imandra=ImandraMetadata(task_name="Formalizing input")),
)
builder.add_node(
    "invoke",
    invoke,
    metadata=NodeMetadata(imandra=ImandraMetadata(task_name="Reasoning")),
)

builder.add_edge(START, "formalize")

graph = builder.compile()

agent = AgentGraph(
    agent_type="interruptible_agent",
    full_name="Prose Reasoner",
    use_case="Formalize and reason about English prose, using Universe Reasoners",
    task_name="Formalize and reason",
    tool_description="Formalize English prose and evaluate it using a Reasoner",
    input_schema=InputState,
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
