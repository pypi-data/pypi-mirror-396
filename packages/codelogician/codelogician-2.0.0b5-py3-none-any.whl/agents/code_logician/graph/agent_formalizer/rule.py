"""Rule engine for constraining MDP actions based on state and history.

Provides:
- Rule: Abstract base for defining constraint logic
- RuleEngine: Evaluates rules and resolves priority conflicts
- NaiveRuleEngine: Default rule implementation for formalization workflow
- AgentParamItem: Constraint specification for enabling/disabling/forcing actions
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal, cast, override

import structlog

from ...base import FormalizationState
from ...imandrax_model_utils import eval_res_errors_to_llm_context
from .base import (
    FTransName,
    FTransParam,
    GenModelParam,
    HITLName,
    HITLParam,
    LLMAgentParam,
    LLMInvokeResult,
    MDPConfig,
    MessageParam,
    ModelSpec,
    StepParam,
    StepRecord,
    ToolName,
)

logger = structlog.get_logger(__name__)

# All possible action names (tools + transitions)
type StepName = ToolName | FTransName | HITLName | Literal["gen_model"]


def get_step_names_from_record(record: StepRecord) -> list[StepName]:
    """Extract action names from step record.

    Returns list of action names based on step type:
    - FTransParam: transition name
    - GenModelParam: "gen_model"
    - LLMAgentParam: tool names from tool_call_summary
    - HITLParam: HITL interaction name
    """
    match record.step_param, record.result:
        case FTransParam(name=name), _:
            return [name]
        case GenModelParam(), _:
            return ["gen_model"]
        case (
            LLMAgentParam(tool_names=_tool_names),
            LLMInvokeResult(tool_call_summary=tool_call_summary),
        ):
            # invariant type
            return cast(
                list[StepName],
                [tool_name for (tool_name, _is_success) in tool_call_summary],
            )
        case HITLParam() as hitl_param, _:
            return [hitl_param.get_name()]
        case _ as invalid:
            raise ValueError(f"Invalid record: {invalid}")


def count_step_in_records(records: list[StepRecord], step_name: StepName) -> int:
    """Count occurrences of specific step name in record history."""
    count = 0
    for r in records:
        if step_name in get_step_names_from_record(r):
            count += 1
    return count


def count_gen_model_in_records(
    records: list[StepRecord],
) -> int:
    """Count total gen_model steps in record history."""
    return count_step_in_records(records, "gen_model")


def steps_after_last_gen_model(
    records: list[StepRecord],
) -> list[StepRecord]:
    """Return steps that occurred after the most recent gen_model step.

    Returns empty list if no gen_model found or it's the last step.
    """
    last_gen_model_idx = -1
    for i in range(len(records) - 1, -1, -1):
        if "gen_model" in get_step_names_from_record(records[i]):
            last_gen_model_idx = i
            break

    if last_gen_model_idx == -1 or last_gen_model_idx == len(records) - 1:
        return []
    return records[last_gen_model_idx + 1 :]


@dataclass
class AgentParamItem:
    """Constraint specification for an action with priority-based resolution.

    Specifies whether an action should be enabled, disabled, or forced, along
    with priority for conflict resolution. Higher priority numbers win.
    """

    tool_name: StepName
    case_enabled: int | None = None
    case_disabled: int | None = None
    case_forced: int | None = None
    forced_arguments: dict[str, Any] | None = None  # Only used when case_forced is set

    message_param: MessageParam = None
    model_spec: ModelSpec = None

    def validate(self) -> list[str]:
        errors = []
        if (
            self.case_enabled is None
            and self.case_disabled is None
            and self.case_forced is None
        ):
            errors.append("Must have at least one case enabled")
        if self.case_forced is not None and self.forced_arguments is None:
            errors.append("case_forced requires forced_arguments")
        if self.case_forced is None and self.forced_arguments is not None:
            errors.append("forced_arguments requires case_forced")
        return errors

    def compare(self, other: AgentParamItem) -> Literal[-1] | Literal[1]:
        """Compare priority of two tool constraints to determine winner.

        This method implements the priority resolution logic for constraints:
        1. Forced constraints always beat enabled/disabled constraints
        2. Among same type (forced vs forced, enabled vs enabled, etc.), higher
           priority number wins
        3. Enabled vs disabled: higher priority number wins
        4. If priorities are equal, other wins (tie-breaking rule)

        Special case: Can compare constraints for different tools only when both
        are forced (used to find highest priority forced action across all tools).

        Args:
            other: Another ToolConstraint to compare against

        Returns:
            -1 if self wins (higher priority or better type)
            1 if other wins (higher priority or better type, or tie)

        Raises:
            ValueError: If comparing different tools when not both forced
        """
        if self.tool_name != other.tool_name:
            if self.case_forced and other.case_forced:
                if self.case_forced > other.case_forced:
                    return -1
                else:
                    return 1
            else:
                raise ValueError(
                    "Can only compare different tool constraints in case of forced"
                )
        if self.case_forced:
            if other.case_forced:
                if self.case_forced > other.case_forced:
                    return -1
                else:
                    return 1
            else:
                return -1
        elif self.case_enabled:
            if other.case_forced:
                return 1
            elif other.case_disabled:
                if self.case_enabled > other.case_disabled:
                    return -1
                else:
                    return 1
            else:
                # Both enabled
                assert other.case_enabled is not None
                if self.case_enabled > other.case_enabled:
                    return -1
                else:
                    return 1
        else:
            assert self.case_disabled is not None
            if other.case_forced:
                return 1
            elif other.case_enabled:
                if self.case_disabled > other.case_enabled:
                    return -1
                else:
                    return 1
            else:
                # Both disabled
                assert other.case_disabled is not None
                if self.case_disabled > other.case_disabled:
                    return -1
                else:
                    return 1


class Rule(ABC):
    """Base class for all rules"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def eval(
        self,
        state: FormalizationState,
        history_states: list[FormalizationState],
        history_actions: list[StepRecord],
        config: MDPConfig,
    ) -> list[AgentParamItem]:
        """Evaluate this rule and return tool constraints.

        This method examines the current state and history to determine what
        constraints should be applied to tool availability. A rule can return
        multiple constraints affecting different tools.

        Args:
            state: Current formalization state
            history_states: List of previous states (chronological order)
            history_actions: List of previous actions taken (chronological order)

        Returns:
            List of ToolConstraint objects. Each constraint specifies:
            - Which tool it affects (tool_name)
            - Whether to enable (case_enabled with priority)
            - Whether to disable (case_disabled with priority)
            - Whether to force execution (case_forced with priority + arguments)

            Return empty list if this rule doesn't apply to current state.
        """
        pass


class CheckFormalizationRule(Rule):
    """Force check_formalization transition on first step if not already done."""

    def __init__(self):
        super().__init__("check_formalization")

    @override
    def eval(
        self,
        state: FormalizationState,
        history_states: list[FormalizationState],
        history_actions: list[StepRecord],
        config: MDPConfig,
    ) -> list[AgentParamItem]:
        if count_step_in_records(history_actions, "check_formalization"):
            return []
        else:
            return [
                AgentParamItem(
                    tool_name="check_formalization",
                    case_forced=100,
                    forced_arguments={},
                )
            ]


class GenProgramRefactorRule(Rule):
    """Force program refactoring if not done and refactoring is enabled in config."""

    def __init__(self):
        super().__init__("gen_program_refactor")

    @override
    def eval(
        self,
        state: FormalizationState,
        history_states: list[FormalizationState],
        history_actions: list[StepRecord],
        config: MDPConfig,
    ) -> list[AgentParamItem]:
        if config["no_refactor"]:
            return []
        if count_step_in_records(history_actions, "gen_program_refactor"):
            return []
        else:
            return [
                AgentParamItem(
                    tool_name="gen_program_refactor",
                    case_forced=90,
                    forced_arguments={},
                )
            ]


class GenFormalizationDataRule(Rule):
    """Force gathering formalization data from database if not already done."""

    def __init__(self):
        super().__init__("gen_formalization_data")

    @override
    def eval(
        self,
        state: FormalizationState,
        history_states: list[FormalizationState],
        history_actions: list[StepRecord],
        config: MDPConfig,
    ) -> list[AgentParamItem]:
        if count_step_in_records(history_actions, "gen_formalization_data"):
            return []
        else:
            return [
                AgentParamItem(
                    tool_name="gen_formalization_data",
                    case_forced=80,
                    forced_arguments={},
                )
            ]


# ============================================================================
# Rule Engine
# ============================================================================


class RuleEngine:
    """Evaluates rules and produces constraints on available actions"""

    def __init__(self, rules: list[Rule]):
        self.rules = rules

    def evaluate(
        self,
        state: FormalizationState,
        history_states: list[FormalizationState],
        history_actions: list[StepRecord],
        config: MDPConfig,
    ) -> StepParam:
        """Evaluate all rules and return the final constraint for the MDP step.

        This method orchestrates the rule evaluation process:
        1. Calls eval() on each rule to collect tool constraints
        2. Groups constraints by tool name
        3. For each tool, compares constraints to find the winner (highest priority)
        4. Determines if any tool is forced (bypasses agent decision)
        5. Returns available tools for agent selection (if no forced action)

        Args:
            state: Current formalization state
            history_states: List of previous states (chronological order)
            history_actions: List of previous actions taken (chronological order)

        Returns:
            Constraint object containing:
            - forced_action: ToolCall to execute immediately (bypasses agent), or None
            - available_tools: List of tool names agent can choose from (if no forced
                action)
            - active_rules: Names of rules that produced the winning constraints
        """
        # Collect all constraints from all rules with provenance
        # List of (action_name, rule_name, constraint)
        all_items: list[tuple[StepName, str, AgentParamItem]] = []

        for rule in self.rules:
            items = rule.eval(state, history_states, history_actions, config)
            if items:
                for item in items:
                    all_items.append((item.tool_name, rule.name, item))

        # Group by action name and find winner for each action
        action_groups: dict[StepName, list[tuple[str, AgentParamItem]]] = {}
        for action_name, rule_name, constraint in all_items:
            if action_name not in action_groups:
                action_groups[action_name] = []
            action_groups[action_name].append((rule_name, constraint))

        # For each action, find the highest priority constraint
        winning_items: list[tuple[StepName, str, AgentParamItem]] = []
        for action_name, rules_and_constraints in action_groups.items():
            if len(rules_and_constraints) == 1:
                rule_name, constraint = rules_and_constraints[0]
                winning_items.append((action_name, rule_name, constraint))
            else:
                # Find winner by comparing all constraints
                winner_rule, winner_constraint = rules_and_constraints[0]
                for rule_name, constraint in rules_and_constraints[1:]:
                    if winner_constraint.compare(constraint) == 1:
                        # constraint wins
                        winner_rule = rule_name
                        winner_constraint = constraint
                winning_items.append((action_name, winner_rule, winner_constraint))

        # Separate forced and available tools
        forced_items = [
            item for item in winning_items if item[2].case_forced is not None
        ]

        if forced_items:
            # Find highest priority forced action
            winner = forced_items[0]
            for item in forced_items[1:]:
                if winner[2].compare(item[2]) == 1:
                    winner = item

            # Return appropriate AgentParam type based on action name
            action_name = winner[0]
            if action_name == "gen_model":
                return GenModelParam()
            else:
                # Action name must be an FTransName
                return FTransParam(name=cast(FTransName, action_name))

        # No forced actions - return all enabled tools
        enabled_items = [
            item for item in winning_items if item[2].case_enabled is not None
        ]

        # Filter to only ToolNames (LLM-invocable tools)
        tool_names: list[ToolName] = []
        for item in enabled_items:
            action_name = item[0]
            if action_name in ("gen_model", "search_iml_api"):
                tool_names.append(cast(ToolName, action_name))

        return LLMAgentParam(tool_names=tool_names)


class NaiveRuleEngine(RuleEngine):
    """Default rule engine with hardcoded priority-ordered rules.

    Rule Evaluation Order (highest to lowest priority):
    1. check_formalization - if not done
    2. check_formalization_hitl - if missing functions and HITL enabled
    3. gen_program_refactor - if not done and refactoring enabled
    4. gen_formalization_data - if not done
    5. gen_model (first attempt) - if zero gen_model steps
    6. gather_formalization_failure_info - after gen_model if not gathered
    7. formalization_action_hitl - if gen attempts exceed limit and HITL enabled
    8. gen_model (retry) - if 10+ steps since last gen_model
    9. LLM agent - choose from [search_iml_api, gen_model]

    Exit conditions handled by ConstrainedMDP:
    - Success: ~ by FormalizationStatus
    - Failure: max_step or max_gen_model limit reached
    """

    @override
    def __init__(self):
        pass

    @override
    def evaluate(
        self,
        state: FormalizationState,
        history_states: list[FormalizationState],
        history_steps: list[StepRecord],
        config: MDPConfig,
    ) -> StepParam:
        # Forced actions in priority order
        if count_step_in_records(history_steps, "check_formalization") == 0:
            logger.debug(
                "naive_rule_engine",
                step_type="ftrans",
                step_param="check_formalization",
            )
            return FTransParam(name="check_formalization")

        missing_func = state.conversion_source_info.missing_func
        if (
            # Missing function exists
            missing_func is not None
            and len(missing_func) > 0
            # Config allow check formalization hitl
            and not config["no_check_formalization_hitl"]
            # No check formalization action before
            and count_step_in_records(history_steps, "check_formalization_hitl") == 0
        ):
            logger.debug(
                "naive_rule_engine",
                step_type="hitl",
                step_param="check_formalization_hitl",
            )
            return HITLParam(
                data={"missing_func": missing_func, "src_code": state.src_code}
            )

        if (
            count_step_in_records(history_steps, "gen_program_refactor") == 0
            and not config["no_refactor"]
        ):
            logger.debug(
                "naive_rule_engine",
                step_type="ftrans",
                step_param="gen_program_refactor",
            )
            return FTransParam(name="gen_program_refactor")

        if count_step_in_records(history_steps, "gen_formalization_data") == 0:
            logger.debug(
                "naive_rule_engine",
                step_type="ftrans",
                step_param="gen_formalization_data",
            )
            return FTransParam(name="gen_formalization_data")

        if count_step_in_records(history_steps, "gen_model") == 0:
            logger.debug("naive_rule_engine", step_type="gen_model")
            return GenModelParam()

        if (
            count_step_in_records(
                steps_after_last_gen_model(history_steps),
                "gather_formalization_failure_info",
            )
            == 0
        ):
            logger.debug(
                "naive_rule_engine",
                step_type="ftrans",
                step_param="gather_formalization_failure_info",
            )
            return FTransParam(name="gather_formalization_failure_info")

        if (
            # Exceed max gen model without hitl
            (
                count_gen_model_in_records(history_steps)
                >= config["max_gen_model_without_hitl"]
            )
            # Config allow gen model hitl
            and not config["no_gen_model_hitl"]
            # No hitl after gen model
            and (
                count_step_in_records(
                    steps_after_last_gen_model(history_steps),
                    "formalization_action_hitl",
                )
                == 0
            )
        ):
            eval_res = state.eval_res
            assert eval_res is not None
            err_str = eval_res_errors_to_llm_context(eval_res)
            assert err_str is not None
            logger.debug(
                "naive_rule_engine",
                step_type="hitl",
                step_param="formalization_action_hitl",
            )
            return HITLParam(data={"iml_code": state.iml_code, "err_str": err_str})

        if len(steps_after_last_gen_model(history_steps)) >= 10:
            logger.debug("naive_rule_engine", step_type="gen_model")
            return GenModelParam()

        # Default: let LLM choose between available tools
        tool_names: list[ToolName] = ["search_iml_api", "gen_model"]
        logger.debug("naive_rule_engine", step_type="llm_agent", step_param=tool_names)
        return LLMAgentParam(tool_names=tool_names)
