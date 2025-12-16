from pydantic import BaseModel, Field

from .formal_spec.dsl.syntax import Feature


class Formalization(BaseModel):
    formal_spec: Feature = Field(description="Current version of the formal spec")
    last_synced_nl_spec: str = Field(
        description="Last known version of the natural language spec that is "
        "semantically in sync with the formal spec"
    )
    last_synced_formal_spec: Feature = Field(
        description="Last known version of the formal spec that is "
        "semantically in sync with the natural language spec"
    )
    validation_result: list[str] | None = Field(
        description="Results of validating the generated formal spec"
    )
    decomp_result: str | None = Field(
        None, description="JSON of the decomposition results"
    )
    reachability_result: str | None = Field(
        None, description="Reachability analysis results"
    )


class FormalizationState(BaseModel):
    src_spec: str = Field(description="Current version of the natural language spec")
    formalization: Formalization | None = Field(
        description="Last known versions of the natural language spec and formal spec "
        "that are guaranteed to be semantically in synch with each other"
    )
    user_feedback: list[str] = Field(
        description="General feedback provided by the user"
    )


def mk_init_state(src_spec: str) -> FormalizationState:
    return FormalizationState(
        src_spec=src_spec,
        formalization=None,
        user_feedback=[],
    )
