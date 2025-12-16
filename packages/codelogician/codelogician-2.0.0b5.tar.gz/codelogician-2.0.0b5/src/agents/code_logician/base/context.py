from typing import Self

from pydantic import BaseModel, Field, model_validator

from utils.fdb.fdb import FDB
from utils.imandra.imandrax.proto_models.simple_api import EvalRes

from .iml import LintingError


class ConversionSourceInfo(BaseModel):
    """
    Context retrieved based on the source code.

    For languages other than Python, only `iml_api_refs` are populated
    """

    meta_eg: list[FDB.ConversionPair] = Field(
        default_factory=list, description="Language-specific meta examples"
    )
    relevant_eg: list[FDB.ConversionPair] = Field(
        default_factory=list, description="Relevant examples"
    )
    iml_api_refs: list[FDB.IMLAPIReference] = Field(
        default_factory=list,
        description="IML API references relevant to the source code",
    )
    missing_func: list[FDB.MissingFunc] | None = Field(
        default=None, description="Missing functions in the source code"
    )
    user_inject: str | None = Field(default=None, description="User-injected context")


class ConversionFailureInfo(BaseModel):
    """Context based on conversion failure. Used for re-try conversion.

    Note that `iml_api_refs` and `missing_func` are re-retrived based on the error,
    different from the ones in `SourceCodeInfo`.
    """

    iml_code: str = Field(description="IML code")
    eval_res: EvalRes
    linting_errors: list[LintingError] = Field(
        default_factory=list,
        description="Linting errors",
    )

    sim_errs: list[FDB.Error] = Field(
        default_factory=list,
        description="Similar errors",
    )
    human_hint: str | None = Field(
        default=None,
        description="Human hint",
    )
    iml_api_refs: list[FDB.IMLAPIReference] = Field(
        default_factory=list,
        description="Relevant IML API references",
    )
    missing_func: list[FDB.MissingFunc] = Field(
        default_factory=list,
        description="Missing functions in the code",
    )

    tool_calls: list[str] = Field(
        default_factory=list,
        description="Tool calls reflecting on the failure",
    )

    @model_validator(mode="after")
    def validate_error_exist(self) -> Self:
        if not self.eval_res.has_errors:
            raise ValueError("No errors found in eval_res")
        return self
