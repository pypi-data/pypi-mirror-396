from __future__ import annotations

from abc import abstractmethod
from typing import Annotated, Literal

from pydantic import BaseModel, Field, computed_field
from rich.table import Table
from rich.text import Text


class OpaqueData(BaseModel):
    assumptions: list[str] = Field(
        default_factory=list,
        description=(
            "Assumptions about the opaque function. Each assumption is an axiom. "
            "For example, `axiom boo x = f x > 0`"
        ),
    )
    approximation: str | None = Field(
        default=None,
        description="An approximation of the opaque function",
    )
    assumption_candidates: list[str] = Field(
        default_factory=list,
        description="Assumption candidates",
    )
    approximation_candidates: list[str] = Field(
        default_factory=list,
        description="Approximation candidates",
    )


class TopLevelDefinition(BaseModel):
    name: str

    start_byte: int
    end_byte: int
    start_point: tuple[int, int]
    end_point: tuple[int, int]

    measure: str | None
    opaque: bool
    opaque_data: OpaqueData | None = Field(default=None)

    @staticmethod
    def render_list(
        top_defs: list[TopLevelDefinition],
        limit: int = 10,
    ) -> tuple[Text, Table]:
        header = Text(f"\nIML Symbols ({len(top_defs)}):", style="bold")
        table = Table(show_header=False, box=None, padding=(0, 1))
        for i, sym in enumerate(top_defs[:limit], 1):  # Limit to first 10
            opaque_marker = (
                "[bright_red]●[/bright_red]"
                if sym.opaque
                else "[bright_green]●[/bright_green]"
            )
            table.add_row(f"{i}.", f"{opaque_marker} {sym.name}")
        if len(top_defs) > limit:
            table.add_row("...", f"[dim]({len(top_defs) - limit} more)[/dim]")
        return header, table

    @staticmethod
    def render_opaque_list(
        top_defs: list[TopLevelDefinition],
        limit: int = 10,
    ) -> tuple[Text, Table]:
        opaque_funcs = [td for td in top_defs if td.opaque]
        header = Text(f"Opaque Functions ({len(opaque_funcs)}):", style="bold")
        table = Table(show_header=False, box=None, padding=(0, 1))
        for i, opaque_func in enumerate(opaque_funcs[:limit], 1):
            opaque_data = opaque_func.opaque_data
            if opaque_data is None:
                opaque_data = OpaqueData()
            num_assumptions = len(opaque_data.assumptions)
            has_approx = opaque_data.approximation is not None
            status_icon = (
                "[bright_green]✓[/bright_green]"
                if has_approx
                else "[bright_yellow]○[/bright_yellow]"
            )
            table.add_row(
                f"{i}.",
                f"{status_icon} {opaque_func.name}",
                f"({num_assumptions} assumptions)",
            )
        if limit is not None and len(opaque_funcs) > limit:
            table.add_row("...", f"[dim]({len(opaque_funcs) - limit} more)[/dim]", "")

        return header, table


class BaseLintingError(BaseModel):
    name: str
    start_byte: int
    end_byte: int
    start_point: tuple[int, int]
    end_point: tuple[int, int]

    @computed_field
    @property
    @abstractmethod
    def message(self) -> str:
        pass

    def format_error_message(self) -> str:
        s = ""
        s += f"{self.name}: {self.message}\n"
        s += f"location: {self.start_point[0]}:{self.start_point[1]}\n"
        return s


class NestedMeasureError(BaseLintingError):
    name: Literal["nested-measure-attribute"] = Field(
        default="nested-measure-attribute"
    )

    function_name: str
    measure: str = Field(description="Measure attribute text")
    top_function_name: str = Field(
        description="Name of the top-level function containing the error"
    )
    nesting_level: int

    @computed_field
    @property
    def message(self) -> str:
        s = ""
        s += f"Measure attribute `{self.measure}` should be attached to a "
        f"top-level function instead of a nested function `{self.function_name}`.\n"
        return s


class NestedRecursiveFunctionError(BaseLintingError):
    name: Literal["nested-recursive-function"] = Field(
        default="nested-recursive-function"
    )

    function_name: str
    top_function_name: str = Field(
        description="Name of the top-level function containing the error"
    )
    nesting_level: int

    @computed_field
    @property
    def message(self) -> str:
        s = ""
        s += f"Recursive function `{self.function_name}` nested in "
        f"{self.top_function_name} might cause proof-obligation difficulty and is"
        "generally discouraged.\n"
        return s


LintingError = Annotated[
    (NestedMeasureError | NestedRecursiveFunctionError), Field(discriminator="name")
]
