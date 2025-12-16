import textwrap
from typing import cast

from pydantic import BaseModel, Field

from agents.code_logician.base.formalization_state import (
    FormalizationState,
    FormalizationStateUpdate,
)
from agents.code_logician.base.iml import OpaqueData, TopLevelDefinition
from utils.llm import get_llm


async def choose_assumptions(
    state: FormalizationState, config, feedback: str | None = None
) -> FormalizationStateUpdate:
    """Given a list of assumption candidates, make LLM choose assumptions."""
    opaque_funcs: list[TopLevelDefinition] = [
        top_def for top_def in state.top_definitions if top_def.opaque
    ]

    # Make opaque function choices
    opaques_str = ""
    for i, opaque_func in enumerate(opaque_funcs, 1):
        opaques_str += f"{i}. {opaque_func.name}\n"
        opaque_data = opaque_func.opaque_data
        if opaque_data is None:
            continue
        opaques_str += (
            f"    - Assumption candidates: {opaque_data.assumption_candidates}\n"
        )

    choose_assumptions_prompt = textwrap.dedent(
        """
        We have a list of opaque functions.

        For each opaque function, we have a list of assumption candidates.
        Given human feedback, you are tasked to identify the opaque function it is \
        talking about, and give a list of assumption candidates that are chosen \
        from the list of assumption candidates.

        <opaques>
        {opaques_str}
        </opaques>

        <human_feedback>
        {feedback}
        </human_feedback>

        The output should be the name of the opaque function and the list of \
        assumption candidates that are chosen from the list of assumption candidates.
        """
    )

    class ChooseAssumptionsOutput(BaseModel):
        opaque_func: str = Field(description="The name of the opaque function")
        chosen_assumption_candidates: list[str] = Field(
            description=(
                "The chosen list of assumptions from the list of assumption candidates"
            )
        )

    llm = get_llm(use_case="json").with_structured_output(
        ChooseAssumptionsOutput
    )  # TODO: use better one?
    response = await llm.ainvoke(choose_assumptions_prompt)
    chosen_assumption_candidates = cast(ChooseAssumptionsOutput, response)

    # Update the opaque function's assumptions
    updated_top_definitions = state.top_definitions.copy()
    for top_def in updated_top_definitions:
        if top_def.opaque and top_def.name == chosen_assumption_candidates.opaque_func:
            if top_def.opaque_data is None:
                top_def.opaque_data = OpaqueData()
            top_def.opaque_data.assumptions.extend(
                chosen_assumption_candidates.chosen_assumption_candidates
            )
            break

    return FormalizationStateUpdate(top_definitions=updated_top_definitions)


async def choose_approximation(
    state: FormalizationState, config, feedback: str | None = None
) -> FormalizationStateUpdate:
    """Given a list of approximation candidates, make LLM choose one approximation."""
    opaque_funcs: list[TopLevelDefinition] = [
        top_def for top_def in state.top_definitions if top_def.opaque
    ]

    # Make opaque function approximation choices
    opaques_str = ""
    for i, opaque_func in enumerate(opaque_funcs, 1):
        opaques_str += f"{i}. {opaque_func.name}\n"
        opaque_data = opaque_func.opaque_data
        if opaque_data is not None:
            opaques_str += (
                f"    - Approximation candidates: "
                f"{opaque_data.approximation_candidates}\n"
            )

    choose_approximation_prompt = textwrap.dedent(
        """
        We have a list of opaque functions.

        For each opaque function, we have a list of approximation candidates.
        Given human feedback, you are tasked to identify the opaque function it is \
        talking about, and choose one approximation candidate from the list of \
        approximation candidates.

        <opaques>
        {opaques_str}
        </opaques>

        <human_feedback>
        {feedback}
        </human_feedback>

        The output should be the name of the opaque function and the list of \
        approximation candidates that are chosen from the list of approximation \
        candidates.
        """
    )

    class ChooseApproximationOutput(BaseModel):
        opaque_func: str = Field(description="The name of the opaque function")
        chosen_approximation_candidate: str = Field(
            description=(
                "The chosen approximation candidate from the list of "
                "approximation candidates"
            )
        )

    llm = get_llm(use_case="json").with_structured_output(
        ChooseApproximationOutput
    )  # TODO: use better one?
    response = await llm.ainvoke(choose_approximation_prompt)
    chosen_approximation_candidate = cast(ChooseApproximationOutput, response)

    # Update the opaque function's approximation
    updated_top_definitions = state.top_definitions.copy()
    for top_def in updated_top_definitions:
        if (
            top_def.opaque
            and top_def.name == chosen_approximation_candidate.opaque_func
        ):
            if top_def.opaque_data is None:
                top_def.opaque_data = OpaqueData()
            chosen_approx = (
                chosen_approximation_candidate.chosen_approximation_candidate
            )
            top_def.opaque_data.approximation = chosen_approx
            break

    return FormalizationStateUpdate(top_definitions=updated_top_definitions)
