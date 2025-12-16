"""LangGraph node implementations for agent_formalizer workflow.

Provides nodes for:
- Prechecking formalization state
- Running constrained MDP with agent execution
- Handling HITL interrupts and resumption
- Routing back to supervisor
"""

from typing import Literal, assert_never, cast

import structlog
from langchain_core.messages import HumanMessage
from langgraph.types import Command as LGCommand, interrupt
from pydantic import Field

from agents.code_logician.command import AgentFormalizerCommand
from utils.agent.base import InterruptMessage
from utils.fdb.fdb import FDB
from utils.llm import get_llm

from ...base import FormalizationState
from ...graph.graph_state import GraphState
from ...graph.utils import (
    check_field_exists,
    mk_precheck_failure_response,
    unpack_step_data,
)
from ...task import FormalizationTask
from .base import HITLParam, MDPConfig, StepType, mk_mdp_config
from .mdp import Agent, ConstrainedMDP, MDPCheckpoint
from .rule import NaiveRuleEngine

logger = structlog.get_logger(__name__)

LGCommand[Literal["code_logician_supervisor"]]


class GraphStateWithMDPCheckPoint(GraphState):
    mdp_checkpoint: MDPCheckpoint | None = Field(default=None)
    mdp_config: MDPConfig


async def agent_formalizer_node(
    state: GraphState, config
) -> LGCommand[Literal["agent_formalizer_core_node", "code_logician_supervisor"]]:
    """Precheck formalization state and setup MDP config before execution."""
    # Unpack
    step_i, steps, step = unpack_step_data(state)
    ftask = step.task
    if ftask is None:
        raise ValueError("Missing task in AgentFormalizerNodeHandler")
    fstate = ftask.last_fstate
    command = cast(AgentFormalizerCommand, step.command.root)
    mdp_config = mk_mdp_config(command)

    logger.info("agent_formalizer_precheck (start)")

    # Precheck fstate
    precheck_failures = check_field_exists(fstate)
    if precheck_failures:
        logger.warning(
            "agent_formalizer_precheck_failed",
            handler="agent_formalizer_node",
            step_id=step_i,
            failures=[f.field for f in precheck_failures],
        )
        command = mk_precheck_failure_response(precheck_failures, steps, step_i)
        # LGCommand type is invariant
        command = cast(
            LGCommand[
                Literal["agent_formalizer_core_node", "code_logician_supervisor"]
            ],
            command,
        )
        return command

    return LGCommand(
        update={"mdp_config": mdp_config}, goto="agent_formalizer_core_node"
    )


async def agent_formalizer_core_node(
    state: GraphStateWithMDPCheckPoint, config
) -> LGCommand[Literal["agent_formalizer_hitl_node", "agent_formalizer_end_node"]]:
    """Execute constrained MDP loop, yielding HITL interrupts or completing workflow."""
    logger.info("agent_formalizer_core_node", handler="agent_formalizer_core_node")
    step_i, steps, step = unpack_step_data(state)
    ftask = cast(FormalizationTask, step.task)
    fstate = cast(FormalizationState, ftask.last_fstate)

    # Agent MDP
    if config.get("configurable", {}).get("use_small_llm", False):
        llm = get_llm(use_case="json")
    else:
        llm = get_llm(use_case="code")
    agent = Agent(model=llm)
    rule_engine = NaiveRuleEngine()
    mdp_config = state.mdp_config

    if state.mdp_checkpoint is None:
        mdp = ConstrainedMDP(
            agent=agent,
            initial_state=fstate,
            rule_engine=rule_engine,
            langgraph_runtime=config,
            config=mdp_config,
        )
    else:
        mdp = ConstrainedMDP.from_checkpoint(
            agent=agent,
            rule_engine=rule_engine,
            checkpoint=state.mdp_checkpoint,
            langgraph_runtime=config,
        )

    async for mdp_step in mdp.run():
        if mdp_step.step_type == StepType.HITL_INTERRUPTED:
            mdp_cp = mdp.to_checkpoint()
            update = {"mdp_checkpoint": mdp_cp}
            return LGCommand(update=update, goto="agent_formalizer_hitl_node")

    traj = mdp.get_formalization_trajectory()

    # New step
    ftask = FormalizationTask(
        formalizations=traj,
        status="done",
    )
    step.task = ftask
    steps[step_i] = step

    logger.info(
        "agent_formalizer_core_node_completed",
        handler="agent_formalizer_core_node",
        step_id=step_i,
        n_formalizations=len(traj),
    )

    return LGCommand(update={"steps": steps}, goto="agent_formalizer_end_node")


def agent_formalizer_hitl_node(
    state: GraphStateWithMDPCheckPoint, config
) -> LGCommand[Literal["agent_formalizer_core_node"]]:
    """Handle HITL interrupts, prompt user, and resume MDP with response."""
    logger.info("agent_formalizer_hitl_node")
    mdp_checkpoint = state.mdp_checkpoint
    assert mdp_checkpoint is not None
    step_i, steps, step = unpack_step_data(state)
    ftask = step.task
    assert ftask is not None

    last_step = mdp_checkpoint.history_steps[-1]
    assert last_step.step_type == StepType.HITL_INTERRUPTED
    last_step_param = last_step.step_param
    last_step_param = cast(HITLParam, last_step_param)
    match last_step_param.data:
        case {"missing_func": missing_func, "src_code": src_code}:
            logger.info("check_formalization_hitl")

            # Deserialize missing_func if they are dicts (from langgraph between-node
            # serialization)
            if missing_func and isinstance(missing_func[0], dict):
                missing_func = [FDB.MissingFunc.from_dict(mf) for mf in missing_func]

            # Interrupt and ask
            interrupt_msg = format_check_formalization_hitl(missing_func, src_code)
            human_feedback = interrupt(interrupt_msg)

            # Log hitl_qas
            ftask.hitl_qas = [
                *ftask.hitl_qas,
                [interrupt_msg, HumanMessage(content=human_feedback)],
            ]

            mdp_checkpoint.resume(human_feedback)
            logger.info("check_formalization_hitl_resumed")

        case {"iml_code": iml_code, "err_str": err_str}:
            logger.info("formalization_action_hitl")

            # Interrupt and ask
            interrupt_msg = format_formalization_action_hitl(iml_code, err_str)
            human_feedback = interrupt(interrupt_msg)

            # Log hitl_qas
            ftask.hitl_qas = [
                *ftask.hitl_qas,
                [interrupt_msg, HumanMessage(content=human_feedback)],
            ]

            mdp_checkpoint.resume(human_feedback)
            logger.info("formalization_action_hitl_resumed")
        case _ as unreachable:
            assert_never(unreachable)  # ty: ignore[type-assertion-failure]

    step.task = ftask
    steps[step_i] = step
    return LGCommand(
        update={"steps": steps, "mdp_checkpoint": mdp_checkpoint},
        goto="agent_formalizer_core_node",
    )


def format_check_formalization_hitl(
    missing_func: list[FDB.MissingFunc],
    src_code: str,
) -> InterruptMessage:
    """Format HITL interrupt message for unsupported functions in source code."""
    info = (
        "Your source program contains functions that IML does not directly support:\n\n"
    )
    for mf in missing_func:
        info += f"- `{mf.src_code}`\n"
    prompt = (
        "While IML can handle these as opaque functions, it may limit "
        "reasoning capabilities later. Consider rewriting your source code, "
        "or **return empty string** to continue with the current version."
    )
    return InterruptMessage(
        agent="agent_formalizer/ask_check_formalization",
        output=info,
        prompt=prompt,
    )


def format_formalization_action_hitl(
    iml_code: str,
    err_str: str,
) -> InterruptMessage:
    """Format HITL interrupt message for IML admission errors."""
    info = (
        f"IML failed to be admitted.\n\n"
        f"IML code:\n\n"
        f"```iml\n"
        f"{iml_code}\n"
        f"```\n\n"
        f"IML errors:\n\n"
        f"```\n"
        f"{err_str}\n"
        f"```"
    )
    prompt = "Please provide hints to fix the IML errors."
    return InterruptMessage(
        agent="agent_formalizer/ask_formalization_action",
        output=info,
        prompt=prompt,
    )


def agent_formalizer_end_node(
    state: GraphState, config
) -> LGCommand[Literal["code_logician_supervisor"]]:
    """Clean up MDP-specific state and route back to supervisor."""
    return LGCommand(update=None, goto="code_logician_supervisor")
