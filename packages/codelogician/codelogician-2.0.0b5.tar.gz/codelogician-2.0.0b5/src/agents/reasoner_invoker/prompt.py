from langchain_core.prompts import HumanMessagePromptTemplate

fix_prompt = HumanMessagePromptTemplate.from_template(
    """When evaluating the following code with Reasoner `{reasoner}`, with the 
following inputs:

```
{input}
```

The reasoner returned the following errors:

{error}

Here are some relevant information that may help you fix the input:

- Similar valid inputs:
{similar_valid_inputs}

- Similar error and corrections:
{similar_error_corrections}

Please try to fix the input. Format your response as a JSON object as per the expected \
schema.
"""
)
