from langchain_core.prompts import HumanMessagePromptTemplate

translate_prompt = HumanMessagePromptTemplate.from_template(
    """Write formalized (code) input for Reasoner `{reasoner}`, using the \
following prose (raw) input:

```
{raw_input}
```

Format your response as a JSON object with the `code` property as per the expected \
schema.
"""
)
