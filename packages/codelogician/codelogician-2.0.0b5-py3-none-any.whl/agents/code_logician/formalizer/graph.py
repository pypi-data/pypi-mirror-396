from langgraph.graph import START, StateGraph

from agents.code_logician.formalizer.base import (
    CLCogitoInputState,
    GraphConfig,
    GraphState,
    InputState,
    NonPyGraphConfig,
)
from agents.code_logician.formalizer.nodes import cl_call_agent, cl_hil, cl_manager
from utils.agent.base import AgentGraph, ImandraMetadata, NodeMetadata

builder = StateGraph(
    GraphState,
    input_schema=InputState,
    context_schema=GraphConfig,
)

builder.add_node("cl_manager", cl_manager)
builder.add_node("cl_call_agent", cl_call_agent)
builder.add_node(
    "cl_hil",
    cl_hil,
    metadata=NodeMetadata(imandra=ImandraMetadata(task_name="Waiting for feedback")),
)

builder.add_edge(START, "cl_manager")

graph = builder.compile()


# These two agents only differ in the default routing config
cl_py_agent = AgentGraph(
    agent_type="interruptible_agent",
    full_name="CodeLogician",
    use_case="generate IML code for Python code",
    task_name="CodeLogician",
    tool_description="""Call CodeLogician agent to convert Python code \
        to IML code. Used when the user request is about converting \
        Python code to IML code.""",
    input_schema=CLCogitoInputState,
    state_schema=GraphState,
    config=GraphConfig,
)


cl_non_py_agent = AgentGraph(
    agent_type="interruptible_agent",
    full_name="CodeLogician",
    use_case="generate IML code for source code in languages other than Python",
    task_name="CodeLogician",
    tool_description="""Call CodeLogician agent to convert non-Python code \
        to IML code. Used when the user request is about converting \
        non-Python code to IML code.""",
    input_schema=CLCogitoInputState,
    state_schema=GraphState,
    config=NonPyGraphConfig,
)
