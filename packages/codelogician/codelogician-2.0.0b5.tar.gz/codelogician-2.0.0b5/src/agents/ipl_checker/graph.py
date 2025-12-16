from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict

from agents.ipl_checker.base import GraphConfig, GraphState, InputState
from agents.ipl_checker.nodes import ipl_check
from utils.agent.base import AgentGraph, ImandraMetadata, NodeMetadata


def get_graph_builder():
    builder = StateGraph(
        GraphState,
        input_schema=InputState,
        context_schema=TypedDict,
    )

    builder.add_node(
        "ipl_check",
        ipl_check,
        metadata=NodeMetadata(imandra=ImandraMetadata(task_name="Validating IPL code")),
    )

    builder.add_edge(START, "ipl_check")
    return builder


builder = get_graph_builder()


def get_graph(checkpointer=None):
    return builder.compile(
        checkpointer=checkpointer,
    )


graph = builder.compile()

agent = AgentGraph(
    agent_type="one_shot_tool",
    full_name="IPL Checker",
    use_case="for IPL code, check if the code is corrent",
    task_name="Check IPL code",
    tool_description="""Check IPL code for errors and/or warnings. \
        Used when the user request is about checking IPL code \
        and there's IPL code present in the user request.""",
    input_schema=InputState,
    state_schema=GraphState,
    config=GraphConfig,
)

if __name__ == "__main__":
    print("IPL checker")
