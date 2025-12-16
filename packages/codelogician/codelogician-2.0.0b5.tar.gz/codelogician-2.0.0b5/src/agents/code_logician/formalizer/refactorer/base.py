from pydantic import Field

from utils.agent.base import AgentDisclosure, InputBase


class InputState(InputBase):
    src_code: str = Field(..., description="The source code to be refactored")


class GraphState(InputState, AgentDisclosure):
    refactored_code: list[tuple[str, str]] = Field(
        [], description="The refactored code"
    )

    def render(self) -> str:
        raise NotImplementedError("Refactorer does not render")

    def skip_hil(self) -> bool:
        """
        Determine if HIL is needed.
        """
        return not bool(self.refactored_code)

    def cl_update(self) -> dict:
        return {
            "refactored_code": self.refactored_code,
        }
