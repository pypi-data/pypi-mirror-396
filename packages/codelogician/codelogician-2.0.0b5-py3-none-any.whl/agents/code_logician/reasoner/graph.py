from langgraph.graph import START, StateGraph

from agents.code_logician.reasoner.base import (
    GraphConfig,
    GraphState,
    InputState,
)
from agents.code_logician.reasoner.nodes.nodes import (
    extract_decompose_reqs,
    extract_verify_reqs,
    fix_iml_verify_queries,
    gen_iml_verify_queries,
    reasoner_entry,
    run_decompose,
    run_verify,
    sync_iml,
    sync_src,
)
from utils.agent.base import ImandraMetadata, NodeMetadata

builder = StateGraph(
    GraphState,
    input_schema=InputState,
    context_schema=GraphConfig,
)
builder.add_node("reasoner_entry", reasoner_entry)
builder.add_node(
    "extract_verify_reqs",
    extract_verify_reqs,
    metadata=NodeMetadata(
        imandra=ImandraMetadata(task_name="Extracting verification requests")
    ),
)
builder.add_node(
    "gen_iml_verify_queries",
    gen_iml_verify_queries,
    metadata=NodeMetadata(
        imandra=ImandraMetadata(task_name="Generating IML verification queries")
    ),
)
builder.add_node("run_verify", run_verify)
builder.add_node(
    "fix_iml_verify_queries",
    fix_iml_verify_queries,
    metadata=NodeMetadata(
        imandra=ImandraMetadata(task_name="Fixing errors in IML verification queries")
    ),
)
builder.add_node(
    "extract_decompose_reqs",
    extract_decompose_reqs,
    metadata=NodeMetadata(
        imandra=ImandraMetadata(task_name="Extracting decomposition requests")
    ),
)
builder.add_node("run_decompose", run_decompose)
builder.add_node(
    "sync_iml",
    sync_iml,
    metadata=NodeMetadata(
        imandra=ImandraMetadata(task_name="Syncing IML code with source code")
    ),
)
builder.add_node(
    "sync_src",
    sync_src,
    metadata=NodeMetadata(
        imandra=ImandraMetadata(task_name="Syncing source code with IML code")
    ),
)

builder.add_edge(START, "reasoner_entry")

graph = builder.compile()
