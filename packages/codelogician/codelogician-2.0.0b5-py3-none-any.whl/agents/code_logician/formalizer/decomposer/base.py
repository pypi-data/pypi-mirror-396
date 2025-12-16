from utils.agent.base import AgentDisclosure, InputBase
from utils.imandra.imandrax.proto_models.simple_api import DecomposeRes


class InputState(InputBase):
    src_code: str
    iml_code: str


class GraphState(InputState, AgentDisclosure):
    iml_func_name: str
    decomp_res: DecomposeRes

    def render(self) -> str:
        raise NotImplementedError("Decomposer does not render")

    def cl_update(self) -> dict:
        update = {
            "iml_func_name": self.iml_func_name,
            "decomp_res": self.decomp_res,
        }
        return update
