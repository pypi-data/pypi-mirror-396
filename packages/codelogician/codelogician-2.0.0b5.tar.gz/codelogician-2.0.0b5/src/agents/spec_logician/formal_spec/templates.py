intermediate_result_ok = """
Here's a Formal Spec translation of the scenarios you provided.
```
{output}
```
""".strip("\n")

intermediate_result_with_issues = """
Here's a partial attempt at a Formal Spec translation of the scenarios you provided.
```
{output}
```
""".strip("\n")

hil_prompt_with_issues = """
The generated Formal Spec feature contains some problems
that could not be resolved automatically:

{problems}

Please provide instructions on how to address these issues.
"""

final_result_ok = """
Formal Spec translation:
```
{output}
```
Equivalent IPL code:
```
{ipl_code}
```
""".strip("\n")
