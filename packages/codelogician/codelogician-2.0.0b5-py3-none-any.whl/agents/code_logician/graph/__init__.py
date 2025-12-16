import inspect

from langgraph.graph import START, StateGraph

# Use absolute imports to support exec_module (used by langgraph runtime)
# Relative imports fail when module is loaded via exec_module with custom name
from agents.code_logician.graph.agent_formalizer.node import (
    agent_formalizer_core_node,
    agent_formalizer_end_node,
    agent_formalizer_hitl_node,
    agent_formalizer_node,
)
from agents.code_logician.graph.base_handlers import BaseNodeHandler
from agents.code_logician.graph.custom_handlers import (
    GenFormalizationDataNodeHandler,
    InitStateNodeHandler,
    SuggestFormalizationActionNodeHandler,
    SyncModelNodeHandler,
    SyncSourceNodeHandler,
)
from agents.code_logician.graph.graph_state import GraphState
from agents.code_logician.graph.message_handlers import (
    EmbedNodeHandler,
    GetStateElementNodeHandler,
    SearchFDBNodeHandler,
)
from agents.code_logician.graph.supervisor import code_logician_supervisor
from agents.code_logician.graph.tool_handlers import (
    AdmitModelNodeHandler,
    CheckFormalizationNodeHandler,
    EditStateElementNodeHandler,
    GenFormalizationFailureDataNodeHandler,
    GenModelNodeHandler,
    GenProgramRefactorNodeHandler,
    GenRegionDecompsNodeHandler,
    GenTestCasesNodeHandler,
    GenVgsNodeHandler,
    InjectCustomExamplesNodeHandler,
    InjectFormalizationContextNodeHandler,
    SetModelNodeHandler,
    SuggestApproximationNodeHandler,
    SuggestAssumptionsNodeHandler,
)

builder = StateGraph(GraphState)

nodes = [
    code_logician_supervisor,
    InitStateNodeHandler,
    EditStateElementNodeHandler,
    GetStateElementNodeHandler,
    SearchFDBNodeHandler,
    EmbedNodeHandler,
    CheckFormalizationNodeHandler,
    GenProgramRefactorNodeHandler,
    InjectFormalizationContextNodeHandler,
    InjectCustomExamplesNodeHandler,
    GenFormalizationDataNodeHandler,
    GenFormalizationFailureDataNodeHandler,
    AdmitModelNodeHandler,
    GenModelNodeHandler,
    SetModelNodeHandler,
    GenVgsNodeHandler,
    GenRegionDecompsNodeHandler,
    GenTestCasesNodeHandler,
    SyncSourceNodeHandler,
    SyncModelNodeHandler,
    agent_formalizer_core_node,
    agent_formalizer_end_node,
    agent_formalizer_hitl_node,
    agent_formalizer_node,
    SuggestFormalizationActionNodeHandler,
    SuggestAssumptionsNodeHandler,
    SuggestApproximationNodeHandler,
]
for node in nodes:
    if inspect.isclass(node) and issubclass(node, BaseNodeHandler):
        node_instance = node()
        builder.add_node(node_instance.node_name, node_instance)
    else:
        builder.add_node(node)

builder.add_edge(START, "code_logician_supervisor")

graph = builder.compile()


__all__ = [
    "GraphState",
    "builder",
    "graph",
]
