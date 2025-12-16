"""Constrained MDP implementation for rule-driven agent workflows.

Core classes:
- Agent: Executes actions (LLM tool selection, transitions, model generation)
- ConstrainedMDP: Orchestrates agent with rule engine, manages state/history
- MDPCheckpoint: Serializable checkpoint for HITL interrupt/resume
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from enum import Enum
from inspect import iscoroutinefunction
from typing import Any, Protocol, assert_never, cast

import langsmith as ls
import structlog
from langchain.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.messages.human import HumanMessage
from pydantic import BaseModel

from utils.llm import support_anthropic_prompt_caching

from ...base import FormalizationState, FormalizationStatus
from ...fstate_transition import (
    AsyncFormalizationStateTransition,
    FormalizationStateTransition,
    handle_check_formalization_hitl_response,
    handle_formalization_action_hitl_response,
    set_model,
)
from ...task import Formalization
from ...tools.formalize_to_iml import format_formalization_msgs
from .agent_param import F_TRANSITION_MAP, TOOL_MAP, run_tool
from .base import (
    AgentParam,
    FStateTransitionResult,
    FTransParam,
    GenModelParam,
    GenModelResult,
    HITLParam,
    HITLResult,
    LLMAgentParam,
    LLMInvokeResult,
    MDPConfig,
    MessageParam,
    StepParam,
    StepRecord,
    StepType,
    ToolName,
    ai_message_to_tool_calls,
    repr_step_param,
)
from .rule import RuleEngine, count_gen_model_in_records, get_step_names_from_record

logger = structlog.get_logger(__name__)


class Agent:
    def __init__(self, model: BaseChatModel):
        self.model = model

    async def action(
        self,
        agent_param: AgentParam,
        state: FormalizationState,
        langgraph_runtime: dict[Any, Any],
        config: MDPConfig,
    ) -> tuple[FormalizationState, StepRecord]:
        match agent_param:
            case FTransParam(name=ftrans_name):
                ftrans = F_TRANSITION_MAP[ftrans_name]

                # direct transition
                if iscoroutinefunction(ftrans):
                    ftrans = cast(AsyncFormalizationStateTransition, ftrans)
                    fupdate = await ftrans(state, langgraph_runtime)
                else:
                    ftrans = cast(FormalizationStateTransition, ftrans)
                    fupdate = ftrans(state, langgraph_runtime)
                next_state = FormalizationState.model_validate(
                    state.model_dump() | fupdate
                )
                record = StepRecord(
                    step_type=StepType.FSTATE_TRANSITION,
                    step_param=agent_param,
                    result=FStateTransitionResult(),
                )
            case GenModelParam():
                msgs = self.construct_messages(
                    state,
                    None,
                    with_output_format_instruction=True,
                    langgraph_runtime=langgraph_runtime,
                    config=config,
                )
                res_msg = self.model.invoke(msgs)
                iml_model = cast(str, res_msg.content)

                # gen model transition
                fupdate = await set_model(state, langgraph_runtime, iml_model)
                next_state = FormalizationState.model_validate(
                    state.model_dump() | fupdate
                )
                record = StepRecord(
                    step_type=StepType.GEN_MODEL,
                    step_param=agent_param,
                    result=GenModelResult(),
                )
            case LLMAgentParam(
                tool_names=tool_names,
                message_param=_message_param,
                model_spec=_model_spec,
            ):
                langchain_tools = [
                    TOOL_MAP[tool_name].to_langchain_tool() for tool_name in tool_names
                ]
                msgs = self.construct_messages(
                    state,
                    None,
                    with_output_format_instruction=False,
                    langgraph_runtime=langgraph_runtime,
                    config=config,
                )
                last_msg = HumanMessage(
                    'Use tools to search for context or call "gen_model" to have one '
                    "more try"
                )
                msgs = [*msgs, last_msg]
                response = self.model.bind_tools(
                    tools=langchain_tools,
                    tool_choice="any",  # Force at least one tool call
                ).invoke(msgs)
                response = cast(AIMessage, response)

                # Execute tools
                tool_call_summary: list[tuple[ToolName, bool]] = []
                tool_calls = ai_message_to_tool_calls(response)

                curr_state = state
                for tool_call in tool_calls:
                    tool_res = await run_tool(
                        tool_call, fstate=curr_state, config=langgraph_runtime
                    )
                    if tool_res.success:
                        assert tool_res.fupdate is not None
                        curr_state = FormalizationState.model_validate(
                            curr_state.model_dump() | tool_res.fupdate
                        )
                        tool_call_summary.append((tool_call.tool_name, True))
                    else:
                        tool_call_summary.append((tool_call.tool_name, False))

                next_state = curr_state
                record = StepRecord(
                    step_type=StepType.LLM_INVOKE,
                    step_param=agent_param,
                    result=LLMInvokeResult(tool_call_summary=tool_call_summary),
                )
            case _ as unreachable:
                assert_never(unreachable)  # ty: ignore[type-assertion-failure]

        return next_state, record

    def construct_messages(
        self,
        state: FormalizationState,
        message_param: MessageParam,
        with_output_format_instruction: bool,
        config: MDPConfig,
        langgraph_runtime: dict[Any, Any],
    ) -> list[BaseMessage]:
        messages = format_formalization_msgs(
            src_lang=state.src_lang,
            src_code=state.src_code,
            src_info=state.conversion_source_info,
            dependency=state.dependency,
            failures_info=state.conversion_failures_info,
            with_output_format_instruction=with_output_format_instruction,
            cache_prompt=(
                langgraph_runtime.get("cache_prompt", True)
                and support_anthropic_prompt_caching(self.model)
            ),
        )
        return messages


# ============================================================================
# MDP System
# ============================================================================


class MDPStatus(Enum):
    INITIALIZED = "initialized"
    RUNNING = "running"
    TERMINATED_OF_SUCCESS = "terminated_of_success"
    TERMINATED_OF_FAILURE = "terminated_of_failure"
    INTERRUPTED = "interrupted"


class MDPData(Protocol):
    status: MDPStatus
    initial_state: FormalizationState
    history_states: list[FormalizationState]
    history_steps: list[StepRecord]
    config: MDPConfig
    start_time: str | None


def resume_mdp(mdp: MDPData, hitl_response: Any):
    """
    Resume MDP from HITL_INTERRUPTED state with HITL response.

    This modifies the last step record (HITL_INTERRUPTED) with the response data

    The validation of HITL response should happen before calling this method.
    """
    last_step = mdp.history_steps[-1]
    if (
        mdp.status != MDPStatus.INTERRUPTED
        or last_step.step_type != StepType.HITL_INTERRUPTED
    ):
        raise ValueError(
            f"resume called on non-interrupted MDP "
            f"(status={mdp.status.value}, step_type={last_step.step_type.value})"
        )

    # Update last state with HITL response
    last_state = mdp.history_states[-1]
    last_step_param = last_step.step_param
    last_step_param = cast(HITLParam, last_step_param)
    match last_step_param.get_name():
        case "check_formalization_hitl":
            fupdate = handle_check_formalization_hitl_response(
                fstate=last_state,
                config={},
                hitl_response=hitl_response,
            )
        case "formalization_action_hitl":
            fupdate = handle_formalization_action_hitl_response(
                fstate=last_state,
                config={},
                hitl_response=hitl_response,
            )
        case _ as unreachable:
            assert_never(unreachable)  # ty: ignore[type-assertion-failure]

    updated_state = FormalizationState.model_validate(last_state.model_dump() | fupdate)
    mdp.history_states[-1] = updated_state

    # Replace the HITL_INTERRUPTED step with completed HITL step
    completed_hitl_step = StepRecord(
        step_type=StepType.HITL,
        step_param=last_step.step_param,
        result=HITLResult(data=hitl_response),
        timestamp=last_step.timestamp,
    )
    mdp.history_steps[-1] = completed_hitl_step
    logger.info("MDP resumed from HITL")

    mdp.status = MDPStatus.RUNNING


class MDPCheckpoint(BaseModel):
    status: MDPStatus
    initial_state: FormalizationState
    history_states: list[FormalizationState]
    history_steps: list[StepRecord]
    config: MDPConfig
    start_time: str | None

    def resume(self, hitl_response: Any):
        resume_mdp(self, hitl_response)


class ConstrainedMDP(MDPData):
    """
    MDP where a language agent selects tool calls, constrained by rules.
    Rules can:
    - Force specific tool calls with priority
    - Restrict which tools are available
    """

    def __init__(
        self,
        agent: Agent,
        rule_engine: RuleEngine,
        initial_state: FormalizationState,
        langgraph_runtime: dict[Any, Any],
        config: MDPConfig,
    ):
        self.status = MDPStatus.INITIALIZED
        self.agent = agent
        self.rule_engine = rule_engine
        self.initial_state = initial_state
        self.history_states: list[FormalizationState] = []
        self.history_steps: list[StepRecord] = []
        self.langgraph_runtime = langgraph_runtime
        self.config = config

        self.start_time: str | None = None

    @property
    def current_state(self) -> FormalizationState:
        if not self.history_states:
            return self.initial_state
        return self.history_states[-1]

    @property
    def current_step(self) -> StepRecord:
        if not self.history_steps:
            raise AssertionError("No history")
        return self.history_steps[-1]

    def to_checkpoint(self) -> MDPCheckpoint:
        return MDPCheckpoint(
            status=self.status,
            initial_state=self.initial_state,
            history_states=self.history_states,
            history_steps=self.history_steps,
            config=self.config,
            start_time=self.start_time,
        )

    @classmethod
    def from_checkpoint(
        cls,
        checkpoint: MDPCheckpoint,
        agent: Agent,
        rule_engine: RuleEngine,
        langgraph_runtime: dict[Any, Any],
    ) -> ConstrainedMDP:
        """Restore MDP from checkpoint with provided agent and rule_engine"""
        mdp = cls(
            agent=agent,
            rule_engine=rule_engine,
            initial_state=checkpoint.initial_state,
            langgraph_runtime=langgraph_runtime,
            config=checkpoint.config,
        )
        mdp.status = checkpoint.status
        mdp.history_states = checkpoint.history_states.copy()
        mdp.history_steps = checkpoint.history_steps.copy()
        mdp.start_time = checkpoint.start_time
        return mdp

    def resume(self, hitl_response: Any):
        resume_mdp(self, hitl_response)

    def set_start_time(self):
        self.start_time = datetime.now(UTC).isoformat()
        logger.info("MDP started", start_time=self.start_time)

    async def step(self) -> None:
        """
        Execute one step of the MDP:
        1. Evaluate rules to get constraints
        2. Either execute forced action OR let agent choose
        3. Execute tool and update state
        4. Record action and return
        """
        # Evaluate rules
        step_param: StepParam = self.rule_engine.evaluate(
            self.current_state, self.history_states, self.history_steps, self.config
        )

        step_param_s = repr_step_param(step_param)
        logger.info("MDP step", step=step_param_s)

        def step_param_to_str(step_param: StepParam) -> str:
            return type(step_param).__name__.removesuffix("Param")

        with ls.trace(
            name=f"MDP step ({step_param_to_str(step_param)})",
            inputs={
                "step_param": step_param_s,
                "mdp_config": self.config,
                "mdp_status": self.status,
            },
        ) as rt:
            match step_param:
                case (
                    LLMAgentParam()
                    | FTransParam()
                    | GenModelParam() as actionable_agent_param
                ):
                    next_state, step_record = await self.agent.action(
                        actionable_agent_param,
                        self.current_state,
                        self.langgraph_runtime,
                        self.config,
                    )
                case HITLParam() as hitl_param:
                    next_state = self.current_state
                    step_record = StepRecord(
                        step_type=StepType.HITL_INTERRUPTED,
                        step_param=hitl_param,
                        result=HITLResult(data={}),
                    )
                    self.status = MDPStatus.INTERRUPTED
                case _ as unreachable:
                    assert_never(unreachable)  # ty: ignore[type-assertion-failure]

            rt.end(outputs={"next_state": next_state, "step_record": step_record})

        # Update history
        self.history_states.append(next_state)
        self.history_steps.append(step_record)

    def reset(self, initial_state: FormalizationState) -> None:
        """Reset the MDP to initial state"""
        self.history_states = []
        self.history_steps = []

    async def run(self) -> AsyncIterator[StepRecord]:
        """
        Run the MDP as an async generator.

        Yields StepRecord after each step. If a HITL_INTERRUPTED step is yielded,
        the caller should checkpoint, handle HITL, then call resume().
        """
        if self.status not in [MDPStatus.INITIALIZED, MDPStatus.RUNNING]:
            raise ValueError(
                f"run called on non-initialized MDP (status={self.status.value})"
            )
        if self.status == MDPStatus.INITIALIZED:
            self.set_start_time()
        self.status = MDPStatus.RUNNING

        safe_guard = 100
        i = 0
        while True:
            logger.info("MDP run iter", step_idx=i)

            # Check termination conditions
            if self.current_state.status not in [
                FormalizationStatus.UNKNOWN,
                FormalizationStatus.INADMISSIBLE,
            ]:
                self.status = MDPStatus.TERMINATED_OF_SUCCESS
                logger.info("MDP terminated of success")
                return

            if len(self.history_steps) >= self.config["max_step"]:
                self.status = MDPStatus.TERMINATED_OF_FAILURE
                logger.info("MDP terminated of action limit")
                return

            if (
                count_gen_model_in_records(self.history_steps)
                >= self.config["max_gen_model"]
            ):
                self.status = MDPStatus.TERMINATED_OF_FAILURE
                logger.info("MDP terminated of gen_model limit")
                return

            await self.step()
            yield self.current_step

            i += 1
            if i > safe_guard:
                self.status = MDPStatus.TERMINATED_OF_FAILURE
                return

    def get_formalization_trajectory(self) -> list[Formalization]:
        if self.start_time is None:
            return []

        formalizations = []
        formalizations += [
            Formalization(
                action="input",
                fstate=self.initial_state,
                timestamp=self.start_time,
            )
        ]

        for state, action_record in zip(
            self.history_states, self.history_steps, strict=True
        ):
            action_names = get_step_names_from_record(action_record)
            match action_record.step_type:
                case StepType.LLM_INVOKE:
                    action_names = ["tool_call", *action_names]
                case StepType.FSTATE_TRANSITION:
                    pass
                case StepType.GEN_MODEL:
                    pass
                case StepType.HITL_INTERRUPTED:
                    action_names = ["hitl_interrupted", *action_names]
                case StepType.HITL:
                    action_names = ["hitl", *action_names]

            formalizations += [
                Formalization(
                    action="_".join(action_names),
                    fstate=state,
                    timestamp=action_record.timestamp,
                )
            ]
        return formalizations
