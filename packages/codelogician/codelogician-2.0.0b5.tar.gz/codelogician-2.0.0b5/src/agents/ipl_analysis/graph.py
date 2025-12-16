from langgraph.graph import END, START, StateGraph

from agents.ipl_analysis.base import GraphConfig, GraphState, InputState
from agents.ipl_analysis.nodes import invoke_ipl_analysis  # , await_decomp
from utils.agent.base import AgentGraph, ImandraMetadata, NodeMetadata

builder = StateGraph(
    GraphState,
    input_schema=InputState,
    context_schema=GraphConfig,
)

builder.add_node(
    "invoke_analysis",
    invoke_ipl_analysis,
    metadata=NodeMetadata(imandra=ImandraMetadata()),
)


builder.add_edge(START, "invoke_analysis")
builder.add_edge("invoke_analysis", END)

graph = builder.compile()

agent = AgentGraph(
    agent_type="one_shot_tool",
    full_name="Perform analysis on an IPL model",
    use_case="Perform either Decomposition or Unsat Analysis on an IPL model",
    task_name="IPL Decomposition or Unsat Analysis",
    tool_description="""A tool to decompose an IPL model's message flows into regions, \
    or to find unreachable paths expressed in message flows via unsat analysis. 
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
