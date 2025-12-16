from langchain.chat_models.base import BaseChatModel
from langchain.prompts import HumanMessagePromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field


class IsAbort(BaseModel):
    """
    Whether the agent should abort the current task.
    """

    is_abort: bool = Field(
        description=(
            "Boolean flag indicating if the agent should abort (True) or continue "
            "(False) the current task"
        )
    )


detect_abort_msg_template = HumanMessagePromptTemplate.from_template(
    """\
<context>
An AI agent is performing a task. and has paused at a breakpoint to request human \
feedback to continue the task.
</context>

<task>
Your need is to analyze whether the human's response is answering the agent's request, \
or the human is asking to abort the current task and possibly start a new task.
</task>

<agent_request>
{agent_request}
</agent_request>

<human_feedback>
{human_feedback}
</human_feedback>
"""
)


async def detect_abort(
    llm: BaseChatModel,
    agent_requests: list[AIMessage],
    human_feedback: HumanMessage,
) -> bool:
    request_str = ""
    for request in agent_requests:
        request_str += f"<message>\n\n{request.content}\n</message>\n"
    request_str += f"{human_feedback.content}"

    detect_abort_msg = detect_abort_msg_template.format(
        agent_request=request_str,
        human_feedback=human_feedback.content,
    )

    return (
        await llm.with_structured_output(schema=IsAbort).ainvoke([detect_abort_msg])
    ).is_abort
