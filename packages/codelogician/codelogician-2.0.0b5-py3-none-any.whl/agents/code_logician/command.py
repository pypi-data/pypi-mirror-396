import textwrap
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel
from rich.console import ConsoleRenderable, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# ----------------------
# Command
# ----------------------


class ToolAnnotations(BaseModel):
    """
    Additional properties describing a Tool to clients.

    NOTE: all properties in ToolAnnotations are **hints**.
    They are not guaranteed to provide a faithful description of
    tool behavior (including descriptive properties like `title`).

    Clients should never make tool use decisions based on ToolAnnotations
    received from untrusted servers.
    """

    title: str | None = None
    """A human-readable title for the tool."""

    readOnlyHint: bool | None = None  # noqa: N815
    """
    If true, the tool does not modify its environment.
    Default: false
    """

    destructiveHint: bool | None = None  # noqa: N815
    """
    If true, the tool may perform destructive updates to its environment.
    If false, the tool performs only additive updates.
    (This property is meaningful only when `readOnlyHint == false`)
    Default: true
    """

    idempotentHint: bool | None = None  # noqa: N815
    """
    If true, calling the tool repeatedly with the same arguments
    will have no additional effect on the its environment.
    (This property is meaningful only when `readOnlyHint == false`)
    Default: false
    """

    openWorldHint: bool | None = None  # noqa: N815
    """
    If true, this tool may interact with an "open world" of external
    entities. If false, the tool's domain of interaction is closed.
    For example, the world of a web search tool is open, whereas that
    of a memory tool is not.
    Default: true
    """
    model_config = ConfigDict(extra="allow")


class BaseCommand(BaseModel):
    """Base class for all individual commands with custom __repr__"""

    def __rich__(self) -> ConsoleRenderable:
        max_width = 40

        # Get command type and args
        cmd_name = getattr(self, "type", None)
        if cmd_name is None:
            raise ValueError("Command type not found")
        args = self.model_dump(exclude={"type"})

        # Create main content
        content_parts = []

        # Command header
        content_parts.append(Text(f"Command: {cmd_name}", style="bold"))

        # Arguments table (if any)
        if args:
            content_parts.append(Text("Parameters:", style="bold"))
            args_table = Table(show_header=False, box=None, padding=(0, 1))

            for key, value in args.items():
                # Smart value formatting
                if isinstance(value, str) and len(value) > max_width - 3:
                    # Truncate long strings
                    display_value = (
                        value[: max_width - 3] + "..."
                        if len(value) > max_width - 3
                        else value
                    )
                elif isinstance(value, list | dict):
                    # Show collection size
                    if isinstance(value, list):
                        display_value = f"[{len(value)} items]" if value else "[]"
                    else:
                        display_value = f"{{{len(value)} keys}}" if value else "{}"
                elif isinstance(value, bool):
                    # Boolean with color
                    display_value = (
                        f"[bright_green]{value}[/bright_green]"
                        if value
                        else f"[bright_red]{value}[/bright_red]"
                    )
                else:
                    display_value = str(value)

                args_table.add_row(f"[dim]{key}:[/dim]", display_value)
            content_parts.append(args_table)
        else:
            content_parts.append(Text("\nNo parameters", "dim"))

        # Create panel
        content_group = Group(*content_parts)
        panel = Panel(
            content_group,
            title="Command",
        )
        return panel


class InitStateCommand(BaseCommand, extra="forbid"):
    """
    Initialize the formalization state. Formalization status will be initialized to
    `UNKNOWN`.

    Updates `src_code`, `src_lang` in the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Initialize the formalization state",
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["init_state"] = "init_state"
    src_code: str = Field(description="Source program to formalize")
    src_lang: str = Field(description="Source language")


class GetStateElementCommand(BaseCommand, extra="forbid"):
    """
    Get a state element from the formalization state.

    The following elements are supported:
    - `status`
    - `src_code`
    - `src_lang`
    - `refactored_code`
    - `conversion_source_info`
    - `conversion_failures_info`
    - `iml_code`
    - `iml_symbols`
    - `opaques`
    - `vgs`
    - `region_decomps`
    - `test_cases`
    Will not change the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Get state elements",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["get_state_element"] = "get_state_element"
    element_names: list[str] = Field(
        description="Name(s) of the state element(s) to get"
    )


class EditStateElementCommand(BaseCommand, extra="forbid"):
    """
    Edit a state element in the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Edit state elements",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["edit_state_element"] = "edit_state_element"
    # TODO: this can be a RootModel, making it more intuitive
    update: dict[str, Any] = Field(
        description=(
            "Updating dictionary to the formalization state, "
            "key-value pairs of field names and values"
        )
    )


class SearchFDBCommand(BaseCommand, extra="forbid"):
    """
    Search the FDB for a table and query.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Search formalization database",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["search_fdb"] = "search_fdb"
    name: Literal[
        "missing_functions",
        "iml_code_by_iml_code",
        "formalization_examples_by_src_lang",
        "formalization_examples_by_src_code",
        "iml_api_reference_by_pattern",
        "iml_api_reference_by_src_code",
        "error_suggestion_by_error_msg",
    ] = Field(description="Name of the table to search")
    query: str | tuple[str, str] | None = Field(
        description=(
            textwrap.dedent(
                """
                Query to search the table.
                - Not required for `missing_functions`
                - For `formalization_examples_by_src_code`, the query is a tuple of
                (source language, source code)
                - For `iml_api_reference_by_src_code`, the query is a tuple of
                (source language, source code)
                - Otherwise, the query is a string
                """
            )
        )
    )
    top_k: int = Field(default=5, description="Number of results to return")


class EmbedCommand(BaseCommand, extra="forbid"):
    """
    Embed query into vector representation if it is provided.
    Other chunk source code and IML code (if any) into pieces and embed them.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Embed source code and IML code (if any)",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["embed"] = "embed"
    query: str | None = Field(
        default=None,
        description="Query to embed. If not provided, source code and IML code will be"
        "embeded",
    )


class CheckFormalizationCommand(BaseCommand, extra="forbid"):
    """
    Check if the source code contains any functions that are hard to formalize in IML.
    If so, relevant context will be retrieved from the FDB to help the later
    formalization.

    Updates `conversion_source_info.missing_funcs` in the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Check formalization feasibility",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["check_formalization"] = "check_formalization"


class GenProgramRefactorCommand(BaseCommand, extra="forbid"):
    """
    Refactor the source code to make it easier to formalize in IML.

    Updates `refactored_code` in the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Generate program refactoring",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["gen_program_refactor"] = "gen_program_refactor"


class GenFormalizationDataCommand(BaseCommand, extra="forbid"):
    """
    Based on the source code, retrieve relevant information from the FDB as context
    for formalization. Must be called before `gen_model`.

    Updates `conversion_source_info` in the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Generate formalization data",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["gen_formalization_data"] = "gen_formalization_data"


class InjectFormalizationContextCommand(BaseCommand, extra="forbid"):
    """
    Inject additional context that is relevant to the formalization.

    Updates `conversion_source_info.user_inject` in the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Inject formalization context",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["inject_formalization_context"] = "inject_formalization_context"
    context: str = Field(description="Additional context for formalization")


class InjectCustomExamplesCommand(BaseCommand, extra="forbid"):
    """
    Inject custom examples for formalization.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["inject_custom_examples"] = "inject_custom_examples"
    examples: list[tuple[str, str]] = Field(
        description=(
            "Examples of source code and corresponding IML code in the form of tuples"
        )
    )


class GenFormalizationFailureDataCommand(BaseCommand, extra="forbid"):
    """
    Based on the formalization failure, retrieve relevant information from the FDB as
    context for re-try formalization.

    Retrieved information will be appended to `conversion_failures_info` in the
    formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Generate formalization failure data",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["gen_formalization_failure_data"] = "gen_formalization_failure_data"


class AdmitModelCommand(BaseCommand, extra="forbid"):
    """
    Admit the current IML model and see if there's any error.

    Updates `eval_res` in the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Admit IML model",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["admit_model"] = "admit_model"


class GenModelCommand(BaseCommand, extra="forbid"):
    """
    Generate IML code based on source program and retrieved context.

    Updates `iml_code`, `iml_symbols`, `opaques`, `eval_res`, `status` in the
    formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Generate IML model",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["gen_model"] = "gen_model"


class SetModelCommand(BaseCommand, extra="forbid"):
    """
    Set the IML model and admit it to see if there's any error.

    Updates `iml_code`, `iml_symbols`, `opaques`, `eval_res`, `status` in the
    formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Set IML model",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["set_model"] = "set_model"
    model: str = Field(description="new IML model to use")


class GenVgsCommand(BaseCommand, extra="forbid"):
    """
    Generate verification goals on the source code and its corresponding IML model. Then
    use ImandraX to verify the VGs.

    Cannot be called when the formalization status is `UNKNOWN` or `INADMISSIBLE`.

    Updates `vgs` in the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Generate verification goals",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["gen_vgs"] = "gen_vgs"
    description: str | None = Field(
        default=None,
        description=(
            "Description of the VGs to generate. If not provided, CodeLogician will "
            "seek verification goal requests from the comments in the source code."
        ),
    )


class GenRegionDecompsCommand(BaseCommand, extra="forbid"):
    """
    Generate region decompositions.

    If `function_name` is provided, the region decompositions will be generated for the
    specific function. Otherwise, CodeLogician will seek region decomposition requests
    from the comments in the source code.

    Cannot be called when the formalization status is `UNKNOWN` or `INADMISSIBLE`.

    Updates `region_decomps` in the formalization state.

    After successful execution, you can either:
    - See the region decomposition results using `get_state_element` with
        `region_decomps`
    - Generate test cases for this specific region decomposition using `gen_test_cases`
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Generate region decompositions",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["gen_region_decomps"] = "gen_region_decomps"
    function_name: str | None = Field(
        default=None,
        description="Name of the function to decompose",
    )


class GenTestCasesCommand(BaseCommand, extra="forbid"):
    """
    Use a specific region decomposition to generate test cases for a specific function
    in the source code.

    Updates `region_decomps[decomp_idx].test_cases` in the formalization state.

    After successful execution, you can:
    - See the test cases using `get_state_element` with `["test_cases"]`
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Generate test cases",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["gen_test_cases"] = "gen_test_cases"
    decomp_idx: int = Field(
        description="Index of the region decomposition to generate test cases for"
    )


class SyncSourceCommand(BaseCommand, extra="forbid"):
    """
    Use the most recent IML model and last pair of source code and IML code to
    update the source code.

    Updates `src_code` in the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Synchronize source code",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["sync_source"] = "sync_source"


class SyncModelCommand(BaseCommand, extra="forbid"):
    """
    Use the most recent IML model and last pair of source code and IML code to
    update the IML code.

    Updates `iml_code` in the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Synchronize IML model",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["sync_model"] = "sync_model"


class AgentFormalizerCommand(BaseCommand, extra="forbid"):
    """
    Use the agentic workflow to formalize the source code. This is roughly equivalent to
    the following steps:
    1. check if the source code is within the scope of Imandra's capability
    (CheckFormalizationCommand)
    2. refactor the source code to make it easier to formalize in IML
    (GenProgramRefactorCommand)
    3. retrieve relevant information from the FDB based on the source code
    (GenFormalizationDataCommand)
    4. generate IML code based on the source code and retrieved context
    (GenModelCommand)
    5. admit the IML code and see if there's any error (AdmitModelCommand)
    6. If the IML code is not admissible, retrieve relevant information from the FDB
    based on the error message (GenFormalizationFailureDataCommand)
    7. repeat 4-6 until the IML code is admissible or the number of tries is exhausted

    Some steps can be skipped by setting the corresponding flags.

    Relevant fields in the formalization state:
    - `refactored_code`, `conversion_source_info`, `conversion_failures_info`?,
    `iml_code`, `eval_res`, `iml_symbols`, `opaques`, `status`
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Agent formalizer workflow",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["agent_formalizer"] = "agent_formalizer"
    no_check_formalization_hitl: bool = Field(
        default=False,
        description="Whether to skip HITL in check_formalization",
    )
    no_refactor: bool = Field(
        default=False,
        description="Whether to skip refactoring",
    )
    no_gen_model_hitl: bool = Field(
        default=False,
        description="Whether to skip HITL in gen_model",
    )
    max_tries_wo_hitl: int = Field(
        default=2,
        description=(
            "Maximum number of tries for the formalizer agent without human-in-the-loop"
        ),
    )
    max_tries: int = Field(
        default=3,
        description="Maximum number of tries for the formalizer agent",
    )


class SuggestFormalizationActionCommand(BaseCommand, extra="forbid"):
    """
    Upon a formalization failure, provide information by populating the `human_hint`
    field of the latest `conversion_failures_info` in the formalization state, which
    will be taken into account by the next formalization attempt (either GenModelCommand
    or AgentFormalizerCommand).
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Suggest formalization action",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["suggest_formalization_action"] = "suggest_formalization_action"
    feedback: str = Field(
        description="Feedback on the formalization failure",
    )


class SuggestAssumptionsCommand(BaseCommand, extra="forbid"):
    """
    Suggest assumptions for a specific opaque function.

    Updates `opaques[i].assumptions` in the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Suggest assumptions",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["suggest_assumptions"] = "suggest_assumptions"
    feedback: str = Field()


class SuggestApproximationCommand(BaseCommand, extra="forbid"):
    """
    Suggest an approximation for a specific opaque function.

    Updates `opaques[i].approximation` in the formalization state.
    """

    tool_annotations: ClassVar[ToolAnnotations] = ToolAnnotations(
        title="Suggest approximations",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    type: Literal["suggest_approximation"] = "suggest_approximation"
    feedback: str = Field()


IndividualCommand = (
    InitStateCommand
    | GetStateElementCommand
    | EditStateElementCommand
    | SearchFDBCommand
    | EmbedCommand
    | CheckFormalizationCommand
    | GenProgramRefactorCommand
    | GenFormalizationDataCommand
    | InjectFormalizationContextCommand
    | InjectCustomExamplesCommand
    | GenFormalizationFailureDataCommand
    | AdmitModelCommand
    | GenModelCommand
    | SetModelCommand
    | GenVgsCommand
    | GenRegionDecompsCommand
    | GenTestCasesCommand
    | SyncSourceCommand
    | SyncModelCommand
    | AgentFormalizerCommand
    | SuggestFormalizationActionCommand
    | SuggestAssumptionsCommand
    | SuggestApproximationCommand
    # | GenAssumptionCandidatesCommand
    # | GenApproximationCandidatesCommand
)


class RootCommand(RootModel):
    root: IndividualCommand = Field(discriminator="type")

    def __rich__(self) -> ConsoleRenderable:
        return self.root.__rich__()


Command = IndividualCommand | RootCommand
