from pydantic import Field

from utils.agent.base import AgentDisclosure, InputBase


class InputState(InputBase):
    src_code: str = Field(..., description="The code to be converted")


class GraphState(InputState, AgentDisclosure):
    inappropriateness: list[str] = Field(
        [], description="List of inappropriateness found"
    )

    def render(self) -> str:
        raise NotImplementedError("Analyzer does not render")

    def skip_hil(self) -> bool:
        """
        Determine if HIL is needed.
        """
        return not bool(self.inappropriateness)

    def cl_update(self) -> dict:
        return {
            "inappropriateness": self.inappropriateness,
        }
