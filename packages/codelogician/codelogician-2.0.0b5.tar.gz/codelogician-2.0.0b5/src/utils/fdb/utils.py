from typing import cast

from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field


class Pattern(BaseModel):
    patterns: list[str] = Field(
        description=(
            "A list of strings describing the computational pattern of the program. "
            "Expected format: '<Name>: <Verb-only description>'"
        )
    )


async def extract_src_code_pattern(
    llm: BaseChatModel,
    src_code: str,
    src_lang: str | None = None,
) -> list[str]:
    src_lang = src_lang if src_lang is not None else ""
    prompt = f"""\
Analyze the following program and describe the computational patterns it **contains**
in **language-agnostic natural English prose**. The analysis should be at the function \
level (in the range of 3-5 lines of code at a time), not the overall program level.
Focus on:
- The abstract operation it performs
- Data transformation patterns
- Common functional programming idioms
- Algorithm patterns if any

The output should be a enumerated list.

<code_to_analyze>
```{src_lang}
{src_code}
```"""
    res = await llm.with_structured_output(schema=Pattern).ainvoke(prompt)
    res = cast(Pattern, res)
    return res.patterns
