from typing import Any

from langgraph.graph import START, StateGraph

from agents.spec_logician.formal_spec.base import GraphConfig, GraphState, InputState
from agents.spec_logician.formal_spec.nodes import (
    generate_feature,
    regenerate_feature,
    run_checks,
)
from utils.agent.base import AgentGraph, ImandraMetadata, NodeMetadata


def mk_metadata(task_name: str) -> dict[str, Any]:
    return NodeMetadata(imandra=ImandraMetadata(task_name=task_name))


def get_graph_builder():
    builder = StateGraph(
        GraphState,
        input_schema=InputState,
        context_schema=GraphConfig,
    )

    builder.add_node(
        "generate_feature",
        generate_feature,
        metadata=mk_metadata("Generate Formal Feature in JSON format"),
    )
    builder.add_node(
        "regenerate_feature",
        regenerate_feature,
        metadata=mk_metadata("Generate Formal Feature in JSON format"),
    )

    builder.add_node(
        "run_checks",
        run_checks,
        metadata=mk_metadata("Run automatic checks on generated Formal Feature"),
    )

    builder.add_edge(START, "generate_feature")
    return builder


builder = get_graph_builder()


def get_graph(checkpointer=None):
    return builder.compile(
        checkpointer=checkpointer,
    )


graph = builder.compile()

agent = AgentGraph(
    agent_type="interruptible_agent",
    full_name="SpecLogician (Formal Spec)",
    use_case="""Translate natural language Cucumber Features/Scenarios \
    to Formal Spec Features/Scenarios.
    """,
    task_name="SpecLogician (Formal Spec)",
    tool_description="""Call SpecLogician to translate \
    natural language Cucumber Features/Scenarios \
    to Formal Spec Features/Scenarios.
    """,
    input_schema=InputState,
    state_schema=GraphState,
    config=GraphConfig,
)

if __name__ == "__main__":
    print("SpecLogician (Formal Spec)")
