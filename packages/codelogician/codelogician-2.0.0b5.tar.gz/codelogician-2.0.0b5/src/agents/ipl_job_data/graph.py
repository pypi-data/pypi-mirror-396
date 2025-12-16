from langgraph.graph import END, START, StateGraph

from agents.ipl_job_data.base import GraphConfig, GraphState, InputState
from agents.ipl_job_data.nodes import get_data
from utils.agent.base import AgentGraph, ImandraMetadata, NodeMetadata

builder = StateGraph(
    GraphState,
    input_schema=InputState,
    context_schema=GraphConfig,
)

builder.add_node(
    "get_data",
    get_data,
    metadata=NodeMetadata(imandra=ImandraMetadata()),
)

builder.add_edge(START, "get_data")
# builder.add_edge("invoke_decomp", "await_decomp")
builder.add_edge("get_data", END)

graph = builder.compile()

agent = AgentGraph(
    agent_type="one_shot_tool",
    full_name="Grab data associated with a job UUID",
    use_case="Grabs the associated data with a job UUID, optionally waiting \
    for it to be available or returning that it is not yet finished.",
    task_name="Get data for IPL Decomposition or Unsat Analysis",
    tool_description="""A tool to query for the status of a job UUID and grab \
    the data if it is finished.
    """,
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
