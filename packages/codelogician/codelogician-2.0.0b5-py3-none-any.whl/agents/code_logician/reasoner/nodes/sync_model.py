from difflib import unified_diff

from langchain.chat_models.base import BaseChatModel
from langchain_core.prompts import HumanMessagePromptTemplate
from pydantic import BaseModel, Field

from agents.code_logician.reasoner.nodes.utils import context_on_src_iml_correspondence


def diff_code(old: str, new: str) -> str:
    """Compare two code strings and return their diff.

    Args:
        old_code (str): The original code string
        new_code (str): The updated code string

    Returns:
        str: A unified diff string showing the differences between old and new code

    Example:
        >>> old = "def hello():\\n    print('hi')"
        >>> new = "def hello():\\n    print('hello')"
        >>> print(diff_code(old, new))
        '  def hello():\\n-     print(\\'hi\\')\\n+     print(\\'hello\\')'
    """
    diff = unified_diff(old.splitlines(), new.splitlines())
    return "\n".join(diff)


# TODO: we probably need few-shot examples (even RAG) for the following two

update_src_code_prompt = HumanMessagePromptTemplate.from_template(
    """<context_on_the_correspondence_between_source_code_and_iml_code>
{context_on_src_iml_correspondence}
</context_on_the_correspondence_between_source_code_and_iml_code>

<task>
We have a pair of source code and IML code. The original pair of source code and \
IML code are already correct respectively. Also, they are correctly corresponding to \
each other. Now, we have some changes in the IML code and you are tasked to update the \
source code to reflect the changes in IML code. The changes in IML code is given in \
the unified diff style.

<caveat>
- Note that it is possible that the changes in IML code won't require any changes in \
the source code. In that case, you can just return the original source code.
- Only update the source code to reflect the **changes** in IML code. Take other parts \
of the source code as they are and do not change them.
</caveat>
</task>

<source code>
{src_code}
</source code>

<original IML code>
{orig_iml_code}
</original IML code>

<IML code unified diff>
{iml_code_diff}
</IML code unified diff>
"""
)

update_iml_code_prompt = HumanMessagePromptTemplate.from_template(
    """<context_on_the_correspondence_between_source_code_and_iml_code>
{context_on_src_iml_correspondence}
</context_on_the_correspondence_between_source_code_and_iml_code>

<task>
We have a pair of source code and IML code. The original pair of source code and \
IML code are already correct respectively. Also, they are correctly corresponding to \
each other. Now, we have some changes in the source code and you are tasked to update \
the IML code to reflect the changes in source code. The changes in source code is \
given in the unified diff style.

<caveat>
- Note that it is possible that the changes in source code won't require any changes \
in the IML code. In that case, you can just return the original IML code.
- Only update the IML code to reflect the **changes** in source code. Take other parts \
of the IML code as they are and do not change them.
</caveat>
</task>

<IML code>
{iml_code}
</IML code>

<original source code>
{orig_src_code}
</original source code>

<source code unified diff>
{src_code_diff}
</source code unified diff>
"""
)

retry_update_iml_code_prompt = HumanMessagePromptTemplate.from_template(
    """<IML error>
{iml_error}
</IML error>

Your previous attempt to update the IML code failed. Please try again."""
)


class UpdatedSrcCode(BaseModel):
    src_code: str = Field(
        description="The updated source code reflecting the changes in IML code."
    )


class UpdatedIMLCode(BaseModel):
    iml_code: str = Field(
        description="The updated IML code reflecting the changes in source code."
    )


async def update_src_code(
    llm: BaseChatModel, src_code: str, orig_iml_code: str, iml_code_diff: str
) -> str:
    return (
        await llm.with_structured_output(UpdatedSrcCode).ainvoke(
            [
                update_src_code_prompt.format(
                    context_on_src_iml_correspondence=context_on_src_iml_correspondence,
                    src_code=src_code,
                    orig_iml_code=orig_iml_code,
                    iml_code_diff=iml_code_diff,
                )
            ]
        )
    ).src_code


async def update_iml_code(
    llm: BaseChatModel, iml_code: str, orig_src_code: str, src_code_diff: str
) -> str:
    return (
        await llm.with_structured_output(UpdatedIMLCode).ainvoke(
            [
                update_iml_code_prompt.format(
                    context_on_src_iml_correspondence=context_on_src_iml_correspondence,
                    iml_code=iml_code,
                    orig_src_code=orig_src_code,
                    src_code_w_diff=src_code_diff,
                )
            ]
        )
    ).iml_code
