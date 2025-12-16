from typing import Self

from pydantic import BaseModel, Field, model_validator

from utils.agent.base import AgentDisclosure, InputBase
from utils.fdb.fdb import FDBFormatter
from utils.imandra.imandrax.proto_models.simple_api import EvalRes


class Formalization(BaseModel):
    iml_code: str
    eval_res: EvalRes
    similar_error_hint: list[str] = Field([], description="Hints from similar errors")
    human_error_hint: str = Field("", description=("Hints from human, if any."))

    @model_validator(mode="after")
    def check_error_hint(self) -> Self:
        if (
            self.similar_error_hint
            and self.human_error_hint
            and not self.eval_res.errors
        ):
            raise ValueError("No error hint is needed if there are no errors")
        return self


class FormalizationContext(BaseModel):
    """For non-Python languages, only iml_func is populated"""

    meta_eg: list[dict] = Field([], description="Language-specific meta examples")
    relevant_eg: list[dict] = Field([], description="Relevant examples")
    iml_func: list[dict] = Field([], description="IML functions relevant to the code")
    missing_func: list[dict] = Field([], description="Missing functions in the code")

    def to_llm_context(self) -> str:
        s = ""
        for i, eg in enumerate([*self.meta_eg, *self.relevant_eg], 1):
            s += f"Example {i}:\n"
            s += FDBFormatter.format_src_code(eg["src_code"], eg["src_lang"])
            s += "\n\n"
            s += FDBFormatter.format_src_code(eg["iml_code"], "iml")
            s += "\n\n"

        s += "Relevant IML API References:\n\n"
        s += FDBFormatter.format_iml_api_reference(self.iml_func)

        missing_func_s = FDBFormatter.format_missing_func(self.missing_func)
        if missing_func_s:
            s += (
                "\n\nMissing functions in the source code and their IML counterparts:\n"
            )
            s += missing_func_s
        return s


class InputState(InputBase):
    src_code: str = Field(..., description="The source code to be formalized")
    src_lang: str = Field(..., description="The language of the source code")
    context: FormalizationContext = Field(
        description="retrieved context", default_factory=FormalizationContext
    )
    formalizations: list[Formalization] = Field(
        description="The previous attempts of formalization",
        default_factory=list,
    )

    @model_validator(mode="after")
    def check_error_hint(self) -> Self:
        # NOTE: it's possible that we may retry formalization even if the IML code
        # admitted successfully.
        for f in self.formalizations[:-1]:
            if f.eval_res.errors and not f.similar_error_hint:
                raise ValueError(
                    "Error hint is required for previous failed formalizations"
                )
        return self


class GraphState(InputState, AgentDisclosure):
    pass

    def render(self) -> str:
        raise NotImplementedError("Formalizer does not render")

    def skip_hil(self) -> bool:
        """
        Determine if HIL is needed.
        """
        return not bool(self.formalizations[-1].eval_res.errors)

    def cl_update(self) -> dict:
        return {
            "context": self.context,
            "formalizations": self.formalizations,
        }
