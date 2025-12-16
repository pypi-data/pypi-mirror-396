import uuid
from enum import Enum
from typing import Literal, Self

import pandas as pd
from devtools import pformat
from pydantic import BaseModel, Field, field_validator, model_validator
from tabulate import tabulate

from agents.code_logician.formalizer.analyzer.base import InputState as AInputState
from agents.code_logician.formalizer.converter.base import (
    Formalization,
    FormalizationContext,
    InputState as CInputState,
)
from agents.code_logician.formalizer.decomposer.base import InputState as DInputState
from agents.code_logician.formalizer.refactorer.base import InputState as RInputState
from utils.agent.base import AgentDisclosure, InputBase, InterruptMessage
from utils.imandra.imandrax.proto_models.simple_api import DecomposeRes
from utils.llm import MODEL_NAME


class CLTask(Enum):
    ANALYSIS = "analysis"
    REFACTORING = "refactoring"
    FORMALIZATION = "formalization"
    DECOMPOSITION = "decomposition"
    HIL_ANALYSIS = "hil_analysis"
    HIL_REFACTORING = "hil_refactoring"
    HIL_FORMALIZATION = "hil_formalization"

    def get_agent_name(self) -> str:
        match self:
            case CLTask.ANALYSIS:
                return "analyzer"
            case CLTask.REFACTORING:
                return "refactorer"
            case CLTask.FORMALIZATION:
                return "converter"
            case CLTask.DECOMPOSITION:
                return "decomposer"
            case _:
                raise ValueError(f"Invalid task: {self}")


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class Task(BaseModel):
    task: CLTask
    status: TaskStatus


class CLCogitoInputState(InputBase):
    src_code: str = Field(description="The source code to be converted")
    src_lang: str = Field(description="The source language of the code")


class InputState(CLCogitoInputState):
    inappropriateness: list[str] = Field(
        [], description="List of inappropriateness found"
    )
    refactored_code: list[tuple[str, str]] = Field(
        [], description="The refactored code"
    )
    context: FormalizationContext = Field(
        description="retrieved context", default_factory=FormalizationContext
    )
    formalizations: list[Formalization] = Field(
        description="The previous attempts of formalization",
        default_factory=list,
    )
    iml_func_name: str | None = Field(
        default=None, description="The name of the IML function decomposed"
    )
    decomp_res: DecomposeRes | None = Field(
        default=None, description="The result of the decomposition"
    )
    tasks: list[Task] = Field(
        description="The workflow to run. Also the communicating channel of agents.",
        default_factory=list,
    )

    @field_validator("tasks", mode="after")
    @classmethod
    def check_task_order(cls, v: list[Task]) -> list[Task]:
        # Check that all pending tasks are at the end of the list
        for i, task in enumerate(v[:-1]):
            if (
                task.status == TaskStatus.PENDING
                and v[i + 1].status != TaskStatus.PENDING
            ):
                raise ValueError("Pending tasks must be at the end of the list")

        # Check no consecutive HIL tasks
        for i, task in enumerate(v[:-1]):
            if task.task.value.startswith("hil_") and v[i + 1].task.value.startswith(
                "hil_"
            ):
                raise ValueError("Cannot have two consecutive human-in-the-loop tasks")

        # HIL cannot be the first task
        if v and v[0].task.value.startswith("hil_"):
            raise ValueError("HIL cannot be the first task")

        return v

    def curr_task(self) -> tuple[int, Task] | tuple[None, None]:
        """Get the current task and its index."""
        curr_idx = None
        curr_task = None
        for i, task in enumerate(self.tasks):
            if task.status == TaskStatus.PENDING:
                curr_idx = i
                curr_task = task
                break
        return curr_idx, curr_task

    def get_input_state(self) -> AInputState | RInputState | CInputState:
        """Get the input for the current task."""
        _curr_idx, curr_task = self.curr_task()
        match curr_task.task:
            case CLTask.ANALYSIS:
                return AInputState(
                    src_code=self.src_code,
                )
            case CLTask.REFACTORING:
                return RInputState(src_code=self.src_code)
            case CLTask.FORMALIZATION:
                src_code = (
                    self.src_code
                    if not self.refactored_code
                    else self.refactored_code[-1][1]
                )
                return CInputState(
                    src_code=src_code,
                    src_lang=self.src_lang,
                    context=self.context,
                    formalizations=self.formalizations,
                )
            case CLTask.DECOMPOSITION:
                src_code = (
                    self.src_code
                    if not self.refactored_code
                    else self.refactored_code[-1][1]
                )
                return DInputState(
                    src_code=src_code,
                    iml_code=self.formalizations[-1].iml_code,
                )
            case _:
                raise ValueError(f"Invalid task: {curr_task.task}")

    def get_interrupt_message(self) -> InterruptMessage:
        _curr_idx, curr_task = self.curr_task()
        if curr_task.task == CLTask.HIL_ANALYSIS:
            info = (
                "Your Python code contains operations that IML does not directly "
                "support:\n\n"
            )
            info += ", ".join([f"`{fn}`" for fn in self.inappropriateness])
            prompt = (
                "While IML can handle these as opaque functions, it may limit "
                "reasoning capabilities later. Consider rewriting your Python code, "
                "or return empty string to continue with the current version."
            )
        elif curr_task.task == CLTask.HIL_REFACTORING:
            info = (
                f"Refactored code:\n\n"
                f"```{self.src_lang}\n"
                f"{self.refactored_code[-1][1]}\n"
                f"```"
            )
            prompt = (
                "The code has been refactored to improve IML conversion. Please verify "
                "that the refactored code is correct by responding with 'y' or 'n'"
            )
        elif curr_task.task == CLTask.HIL_FORMALIZATION:
            f = self.formalizations[-1]
            info = (
                f"IML failed to be admitted.\n\n"
                f"IML code:\n\n"
                f"```{self.src_lang}\n"
                f"{f.iml_code}\n"
                f"```\n\n"
                f"IML errors:\n\n"
                f"```\n"
                f"{pformat(f.eval_res.errors)}\n"
                f"```"
            )

            prompt = "Please provide hints to fix the IML errors."

        return InterruptMessage(
            agent="code_logician",
            output=info,
            prompt=prompt,
        )


def decomp_res_region_df(decomp_res: DecomposeRes) -> pd.DataFrame:
    if not decomp_res.regions_str:
        return pd.DataFrame()
    return pd.DataFrame(list(map(lambda r: r.model_dump(), decomp_res.regions_str)))


def decomp_res_format_regions(
    decomp_res: DecomposeRes,
    format: Literal["markdown", "ascii", "records"] = "markdown",
) -> str:
    """Format the regions"""
    if not decomp_res.regions_str:
        return "No regions found."

    df = decomp_res_region_df(decomp_res)
    df = df[["constraints_str", "invariant_str", "model_eval_str", "model_str"]]
    df.rename(
        columns={
            "constraints_str": "Constraints",
            "invariant_str": "Invariant",
            "model_eval_str": "Model Evaluation",
            "model_str": "Model",
        },
        inplace=True,
    )
    df.rename_axis("Region", inplace=True)
    if format == "markdown":
        return df.to_markdown(index=True, tablefmt="github")
    elif format == "ascii":
        return df.to_markdown(index=True, tablefmt="grid")
    else:
        return pformat(df.to_dict(orient="records"))


class GraphState(InputState, AgentDisclosure):
    pass

    def render(self) -> str:
        s = ""
        if self.refactored_code:
            s += (
                f"- Refactored code:\n\n"
                f"```{self.src_lang}\n"
                f"{self.refactored_code[-1][1]}\n"
                f"```\n\n"
            )
        if self.inappropriateness:
            s += f"- Inappropriateness:\n\n{self.inappropriateness}\n\n"
        if self.formalizations:
            f = self.formalizations[-1]
            s = f"- IML code:\n\n```iml\n{f.iml_code}\n```\n\n"
            if f.eval_res.errors:
                s += f"IML failed to be admitted.\n\n{pformat(f.eval_res.errors)}\n\n"
        if decomp_res := self.decomp_res:
            s += f"- Decomposition:\n\n{decomp_res_format_regions(decomp_res)}\n\n"
        return s


class RoutingConfig(BaseModel):
    """Determines which steps to run in CodeLogician Formalizer."""

    analysis: bool = Field(default=True, description="Whether to run analysis")
    hil_analysis: bool = Field(
        default=True, description="Whether to ask human feedback on analysis"
    )
    refactoring: bool = Field(default=True, description="Whether to run refactoring")
    hil_refactoring: bool = Field(
        default=True, description="Whether to ask human feedback on refactoring"
    )
    formalization_limits: tuple[int, int] = Field(
        (1, 2),
        description="The limits for the number of formalizations, without HIL and "
        "total attempts",
    )
    decomp: bool = Field(default=True, description="Whether to run decomposition")

    def to_tasks(self) -> list[Task]:
        cl_tasks = []
        if self.analysis:
            cl_tasks.append(CLTask.ANALYSIS)
        if self.hil_analysis:
            cl_tasks.append(CLTask.HIL_ANALYSIS)
        if self.refactoring:
            cl_tasks.append(CLTask.REFACTORING)
        if self.hil_refactoring:
            cl_tasks.append(CLTask.HIL_REFACTORING)
        f_wo_hil, f_total = self.formalization_limits
        f_w_hil = f_total - f_wo_hil
        cl_tasks.extend([CLTask.FORMALIZATION] * f_wo_hil)
        cl_tasks.extend([CLTask.HIL_FORMALIZATION, CLTask.FORMALIZATION] * f_w_hil)
        if self.decomp:
            cl_tasks.append(CLTask.DECOMPOSITION)
        return [Task(task=t, status=TaskStatus.PENDING) for t in cl_tasks]

    @property
    def formalization(self) -> bool:
        return self.formalization_limits[1] > 0

    @field_validator("formalization_limits", mode="after")
    @classmethod
    def valid_formalization_limits(cls, v: tuple[int, int]) -> tuple[int, int]:
        f_wo_hil, f_total = v
        if (f_wo_hil < 0) or (f_total < 0):
            raise ValueError("The number of formalizations must be non-negative")
        if f_wo_hil > f_total:
            raise ValueError(
                "The number of formalizations without HIL must be less than "
                "the total number of formalizations"
            )
        return v

    @model_validator(mode="after")
    def valid_config(self) -> Self:
        analysis = self.analysis
        hil_analysis = self.hil_analysis
        refactoring = self.refactoring
        hil_refactoring = self.hil_refactoring
        formalization = self.formalization
        _f_wo_hil, _f_total = self.formalization_limits
        decomp = self.decomp

        steps = [
            analysis,
            hil_analysis,
            refactoring,
            hil_refactoring,
            formalization,
            decomp,
        ]
        n_step = sum(steps)
        if n_step == 0:
            raise ValueError("At least one step must be enabled")
        if hil_analysis and not analysis:
            raise ValueError("hil_analysis cannot be True if analysis is False")
        if hil_refactoring and not refactoring:
            raise ValueError("hil_refactoring cannot be True if refactoring is False")
        if decomp and not formalization:
            raise ValueError("decomp cannot be True if formalization is False")
        if n_step == 2 and analysis and hil_analysis:
            raise ValueError("Meaningless HIL for analysis only run.")
        if n_step == 2 and refactoring and hil_refactoring:
            raise ValueError("Meaningless HIL for refactor only run.")
        return self

    @classmethod
    def basic_conversion(cls) -> Self:
        """Convert and decomp main function."""
        return cls(
            analysis=False,
            hil_analysis=False,
            refactoring=False,
            hil_refactoring=False,
            formalization_limits=(2, 2),
            decomp=True,
        )

    @classmethod
    def full_steps(cls) -> Self:
        return cls(
            analysis=True,
            hil_analysis=True,
            refactoring=True,
            hil_refactoring=True,
            formalization_limits=(2, 2),
            decomp=True,
        )

    @classmethod
    def conversion_only(cls) -> Self:
        return cls(
            analysis=False,
            hil_analysis=False,
            refactoring=False,
            hil_refactoring=False,
            formalization_limits=(2, 2),
            decomp=False,
        )

    @classmethod
    def no_analysis(cls) -> Self:
        return cls(
            analysis=False,
            hil_analysis=False,
            refactoring=True,
            hil_refactoring=True,
            formalization_limits=(2, 2),
            decomp=True,
        )

    def __repr__(self) -> str:
        """Tasks to run."""
        tasks = self.to_tasks()
        table = [
            [str(i), task.task.value.capitalize()] for i, task in enumerate(tasks, 1)
        ]
        return "Tasks to run:\n" + tabulate(
            table, headers=["Step", "Task"], tablefmt="pipe"
        )


class GraphConfig(BaseModel):
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cache_prompt: bool = False
    llm_model_name: MODEL_NAME | None = None
    routing_config: RoutingConfig = Field(
        default_factory=RoutingConfig.full_steps,
        description="The configuration for the steps to run",
    )


class NonPyGraphConfig(GraphConfig):
    routing_config: RoutingConfig = Field(
        default_factory=RoutingConfig.no_analysis,
        description="The configuration for the steps to run",
    )
