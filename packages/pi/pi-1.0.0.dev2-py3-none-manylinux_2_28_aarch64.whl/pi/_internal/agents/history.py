from pydantic_ai.messages import ModelMessage, ModelRequest, UserPromptPart
from pydantic_ai import RunContext
from pi._internal.agents.deps import PiDeps
from pi._internal.agents.storage import fix_stray_tool_calls


async def save_new_messages(
    ctx: RunContext[PiDeps], messages: list[ModelMessage]
) -> list[ModelMessage]:
    """
    Save user and system messages that aren't being streamed by the loop
    """

    NEW_CHAT_OFFSET = 1

    if len(messages) == NEW_CHAT_OFFSET:
        # this is a brand new chat
        ctx.deps.session.add_message(messages[-1])

    elif len(messages) > NEW_CHAT_OFFSET:
        # this isn't a new chat, so it's either a user message or a tool call
        # only save the last user message, because the tool call
        # was saved when it got emitted by the agent loop
        last_message = messages[-1]
        assert isinstance(last_message, ModelRequest), (
            f"This is supposed to be a ModelRequest, "
            f"not {type(last_message).__name__}"
        )

        if len(last_message.parts) >= 1 and isinstance(
            last_message.parts[-1], UserPromptPart
        ):
            ctx.deps.session.add_message(last_message)

    else:
        raise ValueError(f"Unexpected number of messages: {len(messages)}")

    return messages


async def repair_tool_calls(
    ctx: RunContext[PiDeps], messages: list[ModelMessage]
) -> list[ModelMessage]:
    """
    Repair corrupted chat history by appending tool returns for stray
    tool calls. This is necessary to avoid API-side errors.
    """

    messages = fix_stray_tool_calls(messages)
    return messages
