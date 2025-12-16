import uuid

from pydantic import BaseModel, Field

from agents.code_logician.imandrax_model_utils import eval_res_errors_to_llm_context
from utils.agent.base import (
    AgentDisclosure,
    InputBase,
    create_partial_graph_state,
)
from utils.imandra.imandrax.proto_models.simple_api import EvalRes


class InputState(InputBase):
    iml_code: str = Field(..., description="The IML code to be checked")


class GraphState(InputState, AgentDisclosure):
    iml_check_res: EvalRes
    similar_err_hints: list[dict] | None = None

    def render(self, as_sub_agent: bool = False) -> str:
        fail_msg = """
- IML code
```iml
{iml_code}
```

- IML errors
```
{iml_err_str}
```
""".strip("\n")

        success_msg = """
- IML code
```iml
{iml_code}
```
""".strip("\n")

        if self.end_result.result == "success":
            s = "IML check succeeded.\n\n" if not as_sub_agent else ""
            s += success_msg.format(iml_code=self.iml_code)
            return s
        else:
            s = "IML check failed.\n\n" if not as_sub_agent else ""
            err_str = eval_res_errors_to_llm_context(self.iml_check_res)
            s += fail_msg.format(iml_code=self.iml_code, iml_err_str=err_str)
            return s


PartialOutput = create_partial_graph_state(InputState, GraphState)


class GraphConfig(BaseModel):
    thread_id: str = Field(default_factory=lambda _: str(uuid.uuid4()))
