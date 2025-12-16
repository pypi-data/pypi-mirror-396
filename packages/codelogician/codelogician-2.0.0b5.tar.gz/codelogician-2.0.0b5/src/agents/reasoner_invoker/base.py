import uuid

from devtools import pformat
from pydantic import BaseModel, Field

from utils.agent.base import AgentDisclosure, InputBase, create_partial_graph_state
from utils.llm import MODEL_NAME


# TODO: https://github.com/imandra-ai/imandra-universe/blob/main/api/common.py
# import this
class ReasonerResult(BaseModel):
    results: list[str]
    errors: list[str]
    artifacts: list[str] = Field([])
    stats: dict

    def __repr__(self):
        return pformat(self)


class ReasonerCall(BaseModel):
    input: str
    result: ReasonerResult | None = Field(None)


class InputState(InputBase):
    reasoner: str = Field(
        ...,
        description=("The Reasoner to invoke."),
    )
    src_input: str = Field(
        ...,
        description=("The raw input to pass to the Reasoner."),
    )


class GraphState(InputState, AgentDisclosure):
    reasoner_calls: list[ReasonerCall] = Field(
        [],
        description="The reasoner calls made to the reasoner.",
    )
    retrieved_context: dict = Field(
        {},
        description="The context retrieved for fixing the input.",
    )
    should_attempt_change: bool | None = Field(
        None,
        description="Whether the user chose to fix the input.",
    )

    def render(self) -> str:
        assert self.reasoner_calls, "No reasoner calls found"
        last_call: ReasonerCall = self.reasoner_calls[-1]
        last_res: ReasonerResult = last_call.result
        errors = [err for err in last_res.errors if err != ""]
        error_msg = """
Initial input:
```
{initial_input}
```
Attempted input:
```
{last_input}
```
Error:
```
{errors}
```
""".strip("\n")
        success_msg = """
Input:
```
{input}
```
Result:
```
{results}
```
""".strip("\n")

        if self.end_result.result == "success":
            s = f"Evaluation with Reasoner `{self.reasoner}` succeeded.\n\n"
            s += success_msg.format(
                input=last_call.input,
                results="\n".join(last_res.results),
            )
        else:
            s = f"Evaluation with Reasoner `{self.reasoner}` failed.\n\n"
            s += error_msg.format(
                initial_input=self.src_input,
                last_input=last_call.input,
                errors=errors,
            )
        return s


PartialOutput = create_partial_graph_state(InputState, GraphState)


class GraphConfig(BaseModel):
    llm_model_name: MODEL_NAME | None = None
    max_retries: int = 1
    thread_id: str = Field(default_factory=lambda _: str(uuid.uuid4()))
