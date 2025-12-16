"""Constrained MDP for agent-driven formalization workflows.

This package implements a Markov Decision Process where an LLM agent selects
actions (tools and state transitions) under dynamic constraints specified by rules.

Core Components:
- mdp: ConstrainedMDP class orchestrating agent execution with checkpointing
- rule: Rule engine for constraint evaluation and action forcing
- base: Data types for tools, steps, and configuration
- agent_param: Tool implementations and transition mappings
- node: LangGraph integration for workflow orchestration

Typical Usage:
    from .mdp import ConstrainedMDP, Agent
    from .rule import NaiveRuleEngine

    agent = Agent(model=llm)
    mdp = ConstrainedMDP(
        agent=agent,
        initial_state=fstate,
        rule_engine=NaiveRuleEngine(),
        langgraph_runtime=config,
        config=mdp_config,
    )

    async for step in mdp.run():
        if step.step_type == StepType.HITL_INTERRUPTED:
            # Handle human-in-the-loop interaction
            checkpoint = mdp.to_checkpoint()
            ...
"""

from .base import (
    FTransParam,
    GenModelParam,
    HITLParam,
    LLMAgentParam,
    MDPConfig,
    StepRecord,
    StepType,
    ToolDefinition,
    mk_default_mdp_config,
    mk_mdp_config,
)
from .mdp import Agent, ConstrainedMDP, MDPCheckpoint, MDPStatus
from .rule import NaiveRuleEngine, Rule, RuleEngine

__all__ = [
    "Agent",
    "ConstrainedMDP",
    "FTransParam",
    "GenModelParam",
    "HITLParam",
    "LLMAgentParam",
    "MDPCheckpoint",
    "MDPConfig",
    "MDPStatus",
    "NaiveRuleEngine",
    "Rule",
    "RuleEngine",
    "StepRecord",
    "StepType",
    "ToolDefinition",
    "mk_default_mdp_config",
    "mk_mdp_config",
]
