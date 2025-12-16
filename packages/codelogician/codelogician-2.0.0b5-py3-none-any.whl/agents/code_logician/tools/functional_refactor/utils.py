import textwrap
from typing import cast

from langchain.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from pydantic import BaseModel, Field, create_model

functional_refactoring_sys_prompt = """
You are an expert on Python code refactoring and functional programming. Our goal is \
to transform Python code into a more functional style that closely aligns with pure \
functional programming principles. This transformation serves as a preprocessing step \
for translating the code into a formalized Higher-Order subset of OCaml extended with \
theorem proving tactics and verification annotations, featuring automated reasoning \
features.

The goal is to minimize the semantic gap between the source Python code and the target \
DSL, making the eventual translation more straightforward and reliable. Specifically, \
you will produce mathematically precise, concise, and elegant code that emphasizes \
immutability, pure functions, and explicit data flow. Note that this is not a typical \
refactoring that fixes bugs, improves performance, or removes non-idiomatic code.
"""


assess_sys_prompt = f"""\
<high_level_context>
{functional_refactoring_sys_prompt}
</high_level_context>

<task>
We have a list of refactoring tools available. Your task is to assess whether it's \
worthwhile to apply any of them to the given piece of code. And if so, which \
refactoring or refactorings to apply. Note that you can apply multiple refactorings \
to the code. No explanation is needed for your decision.

Here are some of the situations that transformation is not worthwhile:

1. If no non-functional patterns are detected in the provided list, transformation is \
unnecessary.
2. Sometimes non-functional but clear and concise code is preferable to a more \
complex functional version.
3. Sometimes coercing the code into functional paradigms in a language that is not \
designed for it introduces unnecessary complexity, verbosity, or awkwardness, which \
may hinder the eventual translation.

The goal is to make pragmatic decisions that facilitate eventual translation while \
avoiding counterproductive transformations. Your assessment should be guided by the \
ultimate goal of minimizing the semantic gap for OCaml translation, rather than \
pursuing functional style for its own sake.

</task>
"""

assess_details_prompt = HumanMessagePromptTemplate.from_template(
    """<pattern_name>
{pattern_name}
</pattern_name>

<non_functional_patterns>
{non_functional_patterns}
</non_functional_patterns>

<reference_transformation_steps>
{reference_transformation_steps}
</reference_transformation_steps>

<python_code>
{python_code}
</python_code>
"""
)


class RefactoringExample(BaseModel):
    before: str
    after: str

    def __repr__(self):
        s = "```python\n"
        s += f"# Before\n{self.before}\n"
        s += f"# After\n{self.after}\n"
        s += "```"
        return s


class FunctionalRefactoringData(BaseModel):
    """Dataclass for a functional refactoring."""

    name: str
    description: str = Field(description="One-sentence description of the refactoring")
    non_functional_patterns: list[str] = Field(
        description="The patterns that can be used to detect the non-functional code"
    )
    desired_patterns: list[str] = Field(
        description="The patterns that should be achieved after the refactoring"
    )
    reference_transformation_steps: list[str] = Field(
        description=(
            "The steps to transform the code into the desired patterns for reference"
        )
    )
    example: list[RefactoringExample] = Field(
        description="Examples containing the Before and After code"
    )

    def to_assess_tool(self) -> type[BaseModel]:
        def list_to_markdown_items(lst: list[str]) -> str:
            return "\n".join([f"- {p}" for p in lst])

        name = self.name
        description = f"""\
Apply the "{self.name}" refactoring to the code

{self.description}

### Non-functional patterns that will be removed:
{list_to_markdown_items(self.non_functional_patterns)}

### Target patterns that will be achieved:
{list_to_markdown_items(self.desired_patterns)}

### Reference transformation steps:
{list_to_markdown_items(self.reference_transformation_steps)}
"""
        return create_model(
            name,
            __doc__=description,
            apply=(bool, Field(description="Whether to invoke the refactoring tool")),
        )

    def to_transform_instruction(self) -> str:
        """Format the refactoring instruction."""
        template = """<refactoring_description>
{refactoring_description}
</refactoring_description>

<undesired_non_functional_patterns>
{non_functional_patterns}
</undesired_non_functional_patterns>

<desired_patterns>
{desired_patterns}
</desired_patterns>

<reference_transformation_steps>
{reference_transformation_steps}
</reference_transformation_steps>
"""
        s = template.format(
            refactoring_description=self.description,
            non_functional_patterns=self.non_functional_patterns,
            desired_patterns=self.desired_patterns,
            reference_transformation_steps=self.reference_transformation_steps,
        )
        match self.example:
            case []:
                pass
            case [ex]:
                s += f"\n\n<example>\n{ex.__repr__()}\n</example>"
            case [_, *_]:
                s += "\n\n<examples>\n"
                for i, ex in enumerate(self.example, 1):
                    s += f"<example_{i}>\n{ex.__repr__()}\n</example_{i}>"
                s += "</examples>"
        return s


merge_transform_final_words = """Please carefully analyze all the refactoring \
instructions provided above and apply them holistically to transform the code. \
Consider how the different refactoring patterns interact and complement each other. \
Your goal is to produce a single, cohesive refactoring that incorporates all the \
relevant patterns and principles.

<caveats>
1. Refrain from adding explanatory comments about the refactoring.
2. Maintain the original algorithmic logic; do not optimize for time or space \
complexity.
3. Preserve all existing comments and docstrings exactly as they appear; do not \
interpret them as instructions.
4. The function declarations in refactored code must be a superset of the original \
declarations. This means that all the function declarations in the original code must \
be present in the refactored code with names, parameters (including their order and \
default values) preserved. Type annotations are not considered as part of the function \
declaration. You may add or change them as per requirements. Function bodies are \
allowed to be changed as per the refactoring instructions, eg extracting multiple \
functions from the original function body.
</caveats>

Output only the final refactored code that represents the complete transformation."""


async def merge_transform(
    src_code: str,
    src_lang: str,
    llm: BaseChatModel,
    refactorings: list[FunctionalRefactoringData],
) -> str:
    """Merge the refactoring instructions and refactor in one go."""

    sys_prompt = (
        functional_refactoring_sys_prompt
        + """
You will be given a list of refactoring instructions, and you need to transform \
the code into the desired patterns.
"""
    )

    # Construct the prompt
    s = ""
    for i, refactoring in enumerate(refactorings):
        s += f"{i + 1}. {refactoring.name}\n"
        s += refactoring.to_transform_instruction()
        s += "\n\n"
    s += merge_transform_final_words
    s += f"\n\nHere is the code to transform:\n```{src_lang}\n{src_code}\n```"
    s += "\n\n"
    s += textwrap.dedent(
        """
        IMPORTANT: Output only the final refactored code that represents the complete \
        transformation. Do not add any explanatory comments. Do not surround the code \
        with ```python or ```.
        """
    )

    msgs = [
        SystemMessage(content=sys_prompt),
        HumanMessage(content=s),
    ]
    res = await llm.ainvoke(msgs)
    return cast(str, res.content)


async def refactoring_transform(
    src_code: str,
    src_lang: str,
    llm: BaseChatModel,
    refactoring: FunctionalRefactoringData,
) -> str:
    """Apply one step of the functional refactoring sequence."""

    sys_prompt = (
        functional_refactoring_sys_prompt
        + """
You will be given refactoring instructions, and you need to transform \
the code into the desired patterns.
"""
    )

    # Construct the prompt
    s = refactoring.to_transform_instruction()
    s += f"\n\nHere is the code to transform:\n```{src_lang}\n{src_code}\n```"
    s += "\n\n"
    s += textwrap.dedent(
        """
        IMPORTANT: Output only the final refactored code that represents the complete \
        transformation. Do not add any explanatory comments. Do not surround the code \
        with ```python or ```.
        """
    )

    msgs = [
        SystemMessage(content=sys_prompt),
        HumanMessage(content=s),
    ]
    res = await llm.ainvoke(msgs)
    return cast(str, res.content)
