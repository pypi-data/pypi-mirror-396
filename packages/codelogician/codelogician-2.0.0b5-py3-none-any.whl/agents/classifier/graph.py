from collections import Counter
from pathlib import Path

import structlog
from langchain_core.vectorstores.in_memory import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field, create_model

from agents.classifier.base import GraphConfig, GraphState, InputState, agents
from utils.agent.base import Agent, AgentGraph, EndResult, ImandraMetadata, NodeMetadata
from utils.llm import get_llm

logger = structlog.get_logger("agents.classifier")

# Load vector store
cur_dir = Path(__file__).parent
vst_path = cur_dir / "vst.json"
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vst = InMemoryVectorStore.load(vst_path, embeddings)


PredictedLang = create_model(
    "PredictedLang",
    __doc__="Field values correspond to the probability that the problem relates to \
        the given task handler. All field values must be positive if defined.",
    **{
        f"{agent.removeprefix('agent/')}_prob": (
            float | None,
            Field(None, description=meta.use_case),
        )
        for agent, meta in agents.items()
    },
)


def normalise(input: dict[Agent, float]) -> dict[Agent, float]:
    """Normalise probabilities to sum to 1"""
    return {
        agent: (
            prob / sum(input.values()) if sum(input.values()) > 0 else 1 / len(input)
        )
        for agent, prob in input.items()
    }


async def classifier(state: InputState, config):
    """Classify task
    - 1. Python
    - 2. General
    - 3. IML
    """
    logger.info("classifier_node_started")
    problem = state.problem
    model_name = config.get("configurable", {}).get("llm_model_name")
    llm = get_llm(model_name)

    # TODO: better prob calculation

    # 1. LLM prediction
    llm_pred_lang: BaseModel
    llm_pred_lang = await llm.with_structured_output(PredictedLang).ainvoke(problem)
    llm_probs: dict[Agent, float] = {
        f"agent/{agent.removesuffix('_prob')}": prob
        for agent, value in llm_pred_lang.model_dump().items()
        if (prob := value)
    }
    print(llm_probs)
    llm_probs = normalise(llm_probs)
    print("normalise")
    print(llm_probs)

    # 2. Vector search
    similar_docs = vst.similarity_search(problem, k=3)
    similar_handler = [doc.metadata["assigned_task_handler"] for doc in similar_docs]
    handler_counts = Counter(similar_handler)
    v_probs: dict[Agent, float] = {
        agent: count / len(handler_counts)
        for agent in agents
        if (count := handler_counts.get(agent))
    }
    v_probs = normalise(v_probs)

    # 3. Combine, argmax
    scores: dict[Agent, float] = {
        agent: llm_probs.get(agent, 0) + v_probs.get(agent, 0) * 0.2 for agent in agents
    }
    scores = normalise(scores)

    assigned_task_handler: Agent = max(scores, key=scores.get)

    return {
        "task_handler": assigned_task_handler,
        "scores": {agent: round(s, 2) for agent, s in scores.items()},
        "end_result": EndResult(result="success"),
    }


builder = StateGraph(
    GraphState,
    input_schema=InputState,
    context_schema=GraphConfig,
)
builder.add_node(
    "classifier",
    classifier,
    metadata=NodeMetadata(
        imandra=ImandraMetadata(task_name="Evaluating classification")
    ),
)
builder.add_edge(START, "classifier")
builder.add_edge("classifier", END)

graph = builder.compile()

agent = AgentGraph(
    agent_type="one_shot_tool",
    full_name="Classifier",
    use_case="classify the problem to determine which agent to invoke",
    task_name="Classify problem",
    tool_description="""Call Classifier agent to classify the problem. Used when \
        there's a problem to be solved in the user request to point to the right agent.
        """,
    input_schema=InputState,
    state_schema=GraphState,
    config=GraphConfig,
)


if __name__ == "__main__":
    import datetime

    with Path(f"mermaid_{datetime.datetime.now().strftime('%m%d%H%M')}.md").open(
        "w"
    ) as f:
        mermaid: str = graph.get_graph(xray=True).draw_mermaid()
        mermaid = "```mermaid\n" + mermaid + "\n```"
        f.write(mermaid)
