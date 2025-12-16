from typing import Literal

from langchain_core.messages import HumanMessage
from langgraph.types import Command, interrupt

from agents.code_logician.formalizer.analyzer.base import GraphState as AGraphState
from agents.code_logician.formalizer.analyzer.graph import graph as analyzer
from agents.code_logician.formalizer.base import (
    CLTask,
    InputState,
    RoutingConfig,
    TaskStatus,
)
from agents.code_logician.formalizer.converter.base import GraphState as CGraphState
from agents.code_logician.formalizer.converter.graph import graph as converter
from agents.code_logician.formalizer.decomposer.base import GraphState as DGraphState
from agents.code_logician.formalizer.decomposer.graph import graph as decomposer
from agents.code_logician.formalizer.refactorer.base import GraphState as RGraphState
from agents.code_logician.formalizer.refactorer.graph import graph as refactorer
from utils.agent.base import EndResult

agents = {
    "analyzer": analyzer,
    "refactorer": refactorer,
    "converter": converter,
    "decomposer": decomposer,
}


AgentGraphState = AGraphState | RGraphState | CGraphState | DGraphState


def cl_manager(
    state: InputState, config
) -> Command[Literal["cl_call_agent", "cl_hil", "__end__"]]:
    print("--- Node: CodeLogician Manager ---")
    src_lang = state.src_lang
    tasks = state.tasks
    routing_config = config.get("configurable", {})["routing_config"]
    if isinstance(routing_config, dict):
        routing_config = RoutingConfig.model_validate(routing_config)

    update = {}
    # Init tasks from config
    if not tasks:
        print("\tInitializing tasks from routing config")
        print(f"\t{routing_config.__repr__()}")
        tasks = routing_config.to_tasks()
        if src_lang.lower() != "python":
            tasks = [
                task
                for task in tasks
                if task.task not in [CLTask.ANALYSIS, CLTask.HIL_ANALYSIS]
            ]
        update["tasks"] = tasks
    else:
        tasks = state.tasks

    # Routing
    state.tasks = tasks
    _curr_idx, curr_task = state.curr_task()
    if curr_task is None:
        goto = "__end__"
        info = "All tasks completed"
        update["end_result"] = EndResult(
            result="success",
            info=info,
        )
        print(f"\t{info}")
    elif curr_task.task.value.startswith("hil_"):
        goto = "cl_hil"
    else:
        goto = "cl_call_agent"

    return Command(goto=goto, update=update)


async def cl_call_agent(state: InputState, config) -> Command[Literal["cl_manager"]]:
    tasks = state.tasks
    curr_idx, curr_task = state.curr_task()
    if curr_task is None:
        raise ValueError("No pending task found")
    next_task = tasks[curr_idx + 1] if curr_idx + 1 < len(tasks) else None
    print(f"--- Node: CL_CALL_AGENT ({curr_task.task.value}) ---")

    agent_name = curr_task.task.get_agent_name()
    graph = agents[agent_name]
    inputs = state.get_input_state()

    # Call agent
    output: dict = await graph.ainvoke(inputs)
    output: AgentGraphState = graph.builder.state_schema.model_validate(output)

    update = {}
    # Update state
    update |= output.cl_update()

    # Update task
    # Current task
    if output.end_result.result == "success":
        curr_task.status = TaskStatus.COMPLETED
    else:
        curr_task.status = TaskStatus.FAILED
    tasks[curr_idx] = curr_task

    # Next task
    if (
        next_task is not None
        and next_task.task.value.startswith("hil_")
        and output.skip_hil()
    ):
        next_task.status = TaskStatus.SKIPPED
        tasks[curr_idx + 1] = next_task

    # Skip further formalization tasks if formalization is successful
    if (
        curr_task.task == CLTask.FORMALIZATION
        and not output.formalizations[-1].eval_res.errors
    ):
        for i, task in enumerate(tasks):
            if i <= curr_idx:
                continue
            if (
                task.task == CLTask.FORMALIZATION
                or task.task == CLTask.HIL_FORMALIZATION
            ):
                task.status = TaskStatus.SKIPPED
                tasks[i] = task

    # Skip further decomposition task if last formalization failed
    curr_f_failed = (
        curr_task.task == CLTask.FORMALIZATION
        and output.formalizations[-1].eval_res.errors
    )
    next_task_is_decomp = (
        next_task is not None and next_task.task == CLTask.DECOMPOSITION
    )
    if curr_f_failed and next_task_is_decomp:
        next_task.status = TaskStatus.SKIPPED
        tasks[curr_idx + 1] = next_task

    print(f"\tTask status: {tasks[curr_idx].status}")
    update["tasks"] = tasks

    return Command(goto="cl_manager", update=update)


def cl_hil(state: InputState, config) -> Command[Literal["cl_manager"]]:
    tasks = state.tasks
    curr_idx, curr_task = state.curr_task()
    if curr_task is None or not curr_task.task.value.startswith("hil_"):
        raise ValueError("No pending HIL task found")
    print(f"--- Node: CL_HIL ({curr_task.task.value}) ---")

    interrupt_msg = state.get_interrupt_message()
    human_feedback = interrupt(interrupt_msg)

    update = {}
    # Process human input
    if curr_task.task == CLTask.HIL_ANALYSIS:
        if human_feedback.strip():
            update["src_code"] = human_feedback
    elif curr_task.task == CLTask.HIL_REFACTORING:
        if human_feedback.strip() != "y":
            # cancel all tasks after the current task
            for task in tasks[curr_idx + 1 :]:
                task.status = TaskStatus.CANCELLED
    elif curr_task.task == CLTask.HIL_FORMALIZATION:
        formalizations = state.formalizations
        formalizations[-1].human_error_hint = human_feedback or ""
        update["formalizations"] = formalizations
    else:
        raise ValueError(f"Invalid HIL task: {curr_task.task}")

    # Update task
    hil_msgs = [*interrupt_msg.to_messages(), HumanMessage(content=human_feedback)]
    curr_task.status = TaskStatus.COMPLETED
    tasks[curr_idx] = curr_task
    update |= {"tasks": tasks, "hil_messages": hil_msgs}

    return Command(goto="cl_manager", update=update)
