import copy
from enum import Enum
from typing import Any, TypedDict

from pydantic import BaseModel, Field, field_validator
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from utils.imandra.imandrax.proto_models import EvalRes

from .context import ConversionFailureInfo, ConversionSourceInfo
from .dependency import FormalizationDependency
from .iml import LintingError, TopLevelDefinition
from .region_decomp import RegionDecomp
from .vg import VG


class FormalizationStatus(str, Enum):
    UNKNOWN = "unknown"
    INADMISSIBLE = "inadmissible"
    ADMITTED_WITH_OPAQUENESS = "admitted_with_opaqueness"
    EXECUTABLE_WITH_APPROXIMATION = "executable_with_approximation"
    TRANSPARENT = "transparent"

    def __rich__(self) -> Text:
        status_colors = {
            FormalizationStatus.UNKNOWN: "dim",
            FormalizationStatus.INADMISSIBLE: "bright_red",
            FormalizationStatus.ADMITTED_WITH_OPAQUENESS: "bright_cyan",
            FormalizationStatus.EXECUTABLE_WITH_APPROXIMATION: "bright_yellow",
            FormalizationStatus.TRANSPARENT: "light_green",
        }
        status_color = status_colors[self]
        return Text(self.name, style=status_color)

    def __repr__(self) -> str:
        return self.value.capitalize()


class FormalizationState(BaseModel):
    status: FormalizationStatus = Field(
        description="The status of the formalization",
        default=FormalizationStatus.UNKNOWN,
    )
    src_code: str = Field(description="Source program")
    src_lang: str = Field(description="Source language")
    dependency: list[FormalizationDependency] = Field(
        default_factory=list,
        description=(
            "The dependency of the formalization. "
            "A list of FormalizationDependency objects, each containing the source "
            "module and the IML module"
            "The dependencies is sorted by topological order from leaves to root"
        ),
    )
    refactored_code: list[tuple[str, str]] = Field(
        default_factory=list,
        description="Refactored code. A list of (step_name, refactored_code) pairs",
    )

    conversion_source_info: ConversionSourceInfo = Field(
        default_factory=ConversionSourceInfo,
        description=(
            "Context retrieved based on the source code. "
            "Includes conversion examples for the source language, "
            "relevant examples, IML API references, and missing functions."
        ),
    )
    conversion_failures_info: list[ConversionFailureInfo] = Field(
        default_factory=list,
        description=(
            "Context retrieved based on conversion failures. "
            "Used for re-try conversion. Includes evaluation errors, "
            "similar error-suggestions pairs, and additional context."
        ),
    )

    iml_code: str | None = Field(default=None, description="IML code")
    iml_model: str | None = Field(
        default=None, description="IML model without requests"
    )
    top_definitions: list[TopLevelDefinition] = Field(
        default_factory=list,
        description="Top-level definitions in the IML code",
    )
    linting_errors: list[LintingError] = Field(
        default_factory=list,
        description="Linting errors in the IML code",
    )
    eval_res: EvalRes | None = Field(default=None, description="Evaluation result")

    vgs: list[VG] = Field(
        default_factory=list,
        description="Verification goals",
    )
    region_decomps: list[RegionDecomp] = Field(
        default_factory=list,
        description="Region decompositions",
    )

    @field_validator("src_lang", mode="after")
    @classmethod
    def lower_src_lang(cls, value: str) -> str:
        return value.lower()

    @property
    def opaque_funcs(self) -> list[TopLevelDefinition]:
        return [td for td in self.top_definitions if td.opaque]

    @property
    def test_cases(self) -> dict[str, dict[str, list[dict[Any, Any]]]]:
        """
        {func_name: [{test_case_i: {args: ..., expected_output: ...}}, ...]}
        """
        region_decomps = self.region_decomps
        res = {}
        for i, decomp in enumerate(region_decomps, 1):
            if decomp.data is None or decomp.test_cases is None:
                continue
            func_name = decomp.data.name
            test_cases: dict[str, list[dict[Any, Any]]] = decomp.test_cases
            if "src" in test_cases:
                test_cases_: list[dict] = copy.deepcopy(test_cases["src"])
            else:
                test_cases_: list[dict] = copy.deepcopy(test_cases["iml"])
            for i, test_case in enumerate(test_cases_, 1):
                test_case["name"] = f"test_case_{i}"
                test_case.pop("docstr", None)  # TODO: give access to docstr elsewhere
            res[func_name] = test_cases_
        return res

    def __rich__(self) -> Panel:
        def _truncate_code(
            code: str | None, max_lines: int = 8, max_chars: int = 200
        ) -> str:
            """Smart truncation for code that preserves readability"""
            if code is None:
                return "None"

            lines = code.split("\n")
            if len(lines) <= max_lines and len(code) <= max_chars:
                return code

            if len(lines) > max_lines:
                truncated_lines = lines[:max_lines]
                remaining_lines = len(lines) - max_lines
                return (
                    "\n".join(truncated_lines) + f"\n... ({remaining_lines} more lines)"
                )
            else:
                return code[:max_chars] + f"... ({len(code) - max_chars} more chars)"

        # Main panel content
        content_parts = []

        # Status with color coding
        status_text = Text("Status: ", style="bold") + self.status.__rich__()
        content_parts.append(status_text)

        # Source code section
        if self.src_code:
            src_truncated = _truncate_code(self.src_code)
            content_parts.append(
                Text(f"\nSource Code ({self.src_lang}):", style="bold")
            )
            content_parts.append(Text(src_truncated, style="dim"))

        # Refactored section
        if self.refactored_code:
            content_parts.append(
                Text(
                    f"\nRefactored: {len(self.refactored_code)} step(s)",
                    style="bright_cyan",
                )
            )

        # IML code section
        content_parts.append(Text("\nIML Code:", style="bold"))
        if self.iml_code:
            iml_truncated = _truncate_code(self.iml_code)
            content_parts.append(Text(iml_truncated, style="dim"))
        else:
            content_parts.append(Text("None", style="dim"))

        # Eval result section
        eval_part = Text("\nEval: ", style="bold")
        if self.eval_res:
            if self.eval_res.errors is None or len(self.eval_res.errors) == 0:
                eval_part += Text("Success", style="light_green")
            else:
                eval_part += Text("Failed", style="red")
                eval_part += Text(f" ({len(self.eval_res.errors)})", style="red")
        else:
            eval_part += Text("None", style="dim")
        content_parts.append(eval_part)

        # IML symbols table
        if self.top_definitions:
            header, table = TopLevelDefinition.render_list(self.top_definitions)
            content_parts.extend([header, table])

        # Opaques table
        if self.opaque_funcs:
            header, table = TopLevelDefinition.render_opaque_list(self.opaque_funcs)
            content_parts.extend([header, table])

        # Analysis results
        analysis_parts = []
        if self.vgs:
            analysis_parts.append(f"VGs: {len(self.vgs)}")
        if self.region_decomps:
            analysis_parts.append(f"Region Decomps: {len(self.region_decomps)}")

        if analysis_parts:
            content_parts.append(Text(f"\nAnalysis: {' | '.join(analysis_parts)}"))

        # Context data summary
        context_parts = []
        context_parts.append(Text("\nContext Data: ", style="bold"))
        source_info_size = (
            len(self.conversion_source_info.model_dump_json())
            if self.conversion_source_info is not None
            else 0
        )
        failures_info_size = sum(
            len(f.model_dump_json()) for f in self.conversion_failures_info
        )
        context_parts.append(Text(f"  source  : {source_info_size:>8,} bytes"))
        context_parts.append(Text(f"  failures: {failures_info_size:>8,} bytes"))
        content_parts.append(Group(*context_parts))

        # Create the main panel
        content_group = Group(*content_parts)
        panel = Panel(
            content_group,
            title="Formalization State",
            # border_style="bright_white",
        )
        return panel


class FormalizationStateUpdate(TypedDict, total=False):
    status: FormalizationStatus
    src_code: str
    src_lang: str
    refactored_code: list[tuple[str, str]]

    conversion_source_info: ConversionSourceInfo
    conversion_failures_info: list[ConversionFailureInfo]

    iml_code: str | None
    iml_model: str | None
    top_definitions: list[TopLevelDefinition]
    linting_errors: list[LintingError]
    eval_res: EvalRes | None

    vgs: list[VG]
    region_decomps: list[RegionDecomp]
