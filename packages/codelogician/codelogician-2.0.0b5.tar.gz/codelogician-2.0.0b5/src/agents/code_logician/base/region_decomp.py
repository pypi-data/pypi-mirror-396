import copy
from collections.abc import Iterable
from typing import Any, Self

from pydantic import BaseModel, Field, model_validator
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from utils.imandra.imandrax.proto_models import DecomposeRes, RegionStr

from .. import rich_utils
from .vg import render_error_table


class RawDecomposeReq(BaseModel):
    """
    A function to decompose in source code and its corresponding function in IML.
    """

    description: str = Field(
        description="Human-readable description of the function to decompose"
    )
    src_func_name: str = Field(
        description="name of function to decompose in source code"
    )
    iml_func_name: str = Field(description="name of function to decompose in IML")

    def render_content(self) -> list[Text]:
        return [
            Text(f"Src func name: {self.src_func_name}"),
            Text(f"IML func name: {self.iml_func_name}"),
            Text(f"Description: {self.description}"),
        ]

    def __rich__(self):
        title = Text("Raw Decompose Request")
        contents = self.render_content()
        contents = [rich_utils.left_pad(item, 2) for item in contents]

        return rich_utils.join_texts([title, *contents])

    def __repr__(self):
        return rich_utils.get_str(self.__rich__())


class DecomposeReqData(BaseModel):
    name: str
    assuming: str | None = Field(default=None)
    basis: list[str] = Field(default_factory=list)
    rule_specs: list[str] = Field(default_factory=list)
    prune: bool = Field(default=True)
    ctx_simp: bool | None = Field(default=None)
    lift_bool: Any | None = Field(default=None)
    timeout: float | None = Field(default=None)
    str_: bool | None = Field(
        default=True, validation_alias="str", serialization_alias="str"
    )

    def render_content(self) -> Text:
        data = self.model_dump()
        data = {k: v for k, v in data.items() if v is not None}
        skip_keys = ["str_", "name"]
        data = {k: v for k, v in data.items() if k not in skip_keys}

        content_t = rich_utils.devtools_pformat(data, indent=0)
        content_ts = content_t.split("\n")[1:-1]

        t = rich_utils.join_texts(content_ts)
        return t

    def __rich__(self) -> Text:
        t = Text()
        t.append(Text("DecomposeReqData:", style="bold"))
        t.append("\n")
        t.append(rich_utils.left_pad(self.render_content(), 2))
        return t


def render_region_table(regions: list[RegionStr], limit: int = 20) -> Table:
    table = Table(title="Regions")
    for col_name in ["#", "Constraints", "Invariant"]:
        table.add_column(col_name)

    def f_constraints(strs: list[str] | None) -> str:
        strs = strs or []
        return "\n".join(strs)

    for i, region in enumerate(regions):
        table.add_row(
            str(i),
            f_constraints(region.constraints_str),
            region.invariant_str,
        )
        if i >= limit:
            remaining = len(regions) - limit
            table.add_row(
                f"{limit}+",
                f"{remaining} more",
                f"{remaining} more",
            )
            break
    return table


def render_decomp_res_content(res: DecomposeRes, limit: int = 10) -> list[Text | Table]:
    parts: list[Text | Table] = []
    if len(res.errors) > 0:
        parts.append(Text("Errors:", style="red"))
        error_table = render_error_table(res.errors, "Decompose Errors")
        parts.append(error_table)
        return parts
    regions = res.regions_str
    if regions is None:
        return parts

    if len(regions) == 0:
        parts.append(Text("0 regions", style="yellow"))
        return parts

    region_table = render_region_table(regions, limit)
    parts.append(region_table)

    return parts


class RegionDecomp(BaseModel):
    """
    A region decomposition
    """

    # Pure IML
    data: DecomposeReqData | None = Field(default=None)
    res: DecomposeRes | None = Field(default=None)

    # Source correspondence
    raw: RawDecomposeReq | None = Field(default=None)
    # TODO: define a test case schema?
    test_cases: dict[str, list[dict[Any, Any]]] | None = Field(
        default=None,
        examples=[
            {
                "iml": [
                    {"args": {"x": "1"}, "expected_output": "(-2)"},
                    {"args": {"x": "2"}, "expected_output": "4"},
                ],
                "src": [
                    {
                        "args": {"x": "1"},
                        "expected_output": "-2",
                        "docstr": (
                            "Constraints:\n    - `x <= 1`\nInvariant:\n    - `x - 3`\n"
                        ),
                    },
                    {
                        "args": {"x": "2"},
                        "expected_output": "4",
                        "docstr": (
                            "Constraints:\n    - `x >= 2`\nInvariant:\n    - `x + 2`\n"
                        ),
                    },
                ],
            }
        ],
    )

    @model_validator(mode="after")
    def at_least_one_of_req(self) -> Self:
        if self.raw is None and self.data is None:
            raise ValueError("At least one of raw or data must be provided")
        return self

    @staticmethod
    def render_test_cases(
        test_cases: dict[str, list[dict[Any, Any]]],
        limit: int = 20,
    ) -> Table:
        test_cases = copy.deepcopy(test_cases)
        if "src" in test_cases:
            data = test_cases["src"]
        else:
            data = test_cases["iml"]

        if "docstr" in data[0]:
            for item in data:
                item.pop("docstr")

        def format_args(args_dict: dict[str, str]) -> str:
            """Format args dictionary nicely: {'x': '1', 'y': '2'} -> 'x: 1, y: 2'"""
            if not args_dict:
                return ""

            formatted_pairs: list[str] = []
            for key, value in args_dict.items():
                formatted_pairs.append(f"{key}: {value}")

            return ", ".join(formatted_pairs)

        table = Table(title="Test Cases")
        col_names = list(data[0].keys())

        def title_case(s: str) -> str:
            s = s.replace("_", " ")
            return s.title()

        col_names = [title_case(name) for name in col_names]
        col_names = ["", *col_names]
        for col_name in col_names:
            table.add_column(col_name)

        for i, item in enumerate(data, 1):
            row_values: list[str] = []
            for key, value in item.items():
                if key == "args":
                    row_values.append(format_args(value))
                else:
                    row_values.append(str(value))
            table.add_row(str(i), *row_values)
            if i >= limit:
                remaining = len(data) - limit
                table.add_row(
                    f"{limit}+",
                    f"{remaining} more",
                    f"{remaining} more",
                )
                break

        return table

    def __rich__(self) -> Panel:
        """Rich display for the entire RegionDecomp."""
        parts: Iterable[RenderableType] = []

        if self.raw:
            raw_req_group = Group(
                Text(f"Src func name: {self.raw.src_func_name}"),
                Text(f"IML func name: {self.raw.iml_func_name}"),
                Text(f"Description: {self.raw.description}"),
            )
            parts.append(Panel(raw_req_group, title="Raw Request"))

        if self.data:
            parts.append(Panel(self.data.__rich__(), title="Request Data"))

        if self.res:
            res_contents = render_decomp_res_content(self.res)
            parts.append(Panel(Group(*res_contents), title="Result"))

        if self.test_cases:
            test_cases_table = self.render_test_cases(self.test_cases)
            parts.append(Panel(test_cases_table, title="Test Cases"))

        return Panel(Group(*parts), title="Region Decomposition")

    def __repr__(self):
        return rich_utils.get_str(self.__rich__())
