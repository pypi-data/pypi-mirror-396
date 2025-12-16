import pathlib
from typing import AsyncGenerator
from pydantic_ai import ModelMessage
from pydantic_ai.messages import (
    AgentStreamEvent,
    SystemPromptPart,
    UserPromptPart,
    ThinkingPart,
    ToolCallPart,
    ToolReturnPart,
    RetryPromptPart,
    TextPart,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    PartStartEvent,
    FinalResultEvent,
    TextPartDelta,
    ThinkingPartDelta,
    PartEndEvent,
)

import rich.syntax
import rich.text

from pi._internal.ui.models import chattables, panelables
from pi._internal.ui.widgets import chat


class UIAdapter:
    async def make_ui_stream_event(
        self, loop_event: AgentStreamEvent
    ) -> chat.ChatStreamEvent | None:
        ui_event: chat.ChatStreamEvent | None = None

        match loop_event:
            case PartStartEvent(part=part):
                # Handle thinking parts
                if isinstance(part, ThinkingPart):
                    ui_event = chat.ChatStreamEvent(
                        action="start_stream",
                        chattable=chattables.ThinkingMessage(
                            content=part.content,
                        ),
                    )
                # Handle text parts (regular assistant messages)
                elif isinstance(part, TextPart):
                    ui_event = chat.ChatStreamEvent(
                        action="start_stream",
                        chattable=chattables.TextMessage(
                            content=part.content,
                        ),
                    )
            case PartDeltaEvent(delta=delta):
                # Handle thinking deltas
                if isinstance(delta, ThinkingPartDelta):
                    ui_event = chat.ChatStreamEvent(
                        action="apply_delta",
                        delta=delta.content_delta,
                    )
                # Handle text deltas (regular assistant messages)
                elif isinstance(delta, TextPartDelta):
                    ui_event = chat.ChatStreamEvent(
                        action="apply_delta",
                        delta=delta.content_delta,
                    )
            case FunctionToolCallEvent(part=part):
                ui_event = chat.ChatStreamEvent(
                    action="push",
                    chattable=chattables.ToolMessage(
                        tool_name=part.tool_name,
                        tool_args=part.args_as_dict() or {},
                        tool_call_id=part.tool_call_id,
                    ),
                )
            case FunctionToolResultEvent(result=result):
                assert isinstance(result.content, str), (
                    "tool must have ToolReturn as return type and string "
                    "as return_value"
                )
                if isinstance(result, ToolReturnPart):
                    assert isinstance(result.metadata, dict), (
                        "tool must have ToolReturn as return type and dict "
                        "as metadata"
                    )
                    is_failure = result.metadata.get("is_failure", False)
                elif isinstance(result, RetryPromptPart):
                    is_failure = True
                else:
                    raise ValueError(
                        f"Unexpected tool result type: {type(result)}"
                    )

                ui_event = chat.ChatStreamEvent(
                    action="update",
                    chattable=chattables.ToolMessage(
                        tool_call_id=result.tool_call_id,
                        result_status="failure" if is_failure else "success",
                    ),
                )
            case PartEndEvent(part=part):
                # this is a newly introduced event, we're ignoring it because
                # our current setup works without it, but in the future we
                # should consider refactoring.
                pass
            case FinalResultEvent():
                pass  # ignore final result
            case _:
                raise ValueError(
                    f"Unknown event type: {loop_event.event_kind}"
                )

        return ui_event  # None if we ignore the loop event

    async def make_chattables(
        self, messages: list[ModelMessage]
    ) -> AsyncGenerator[chattables.Chattable, None]:
        for message_idx, message in enumerate(messages):
            for part in message.parts:
                chattable: chattables.Chattable | None = None

                match part:
                    case ThinkingPart():
                        chattable = chattables.ThinkingMessage(
                            content=part.content,
                        )
                    case TextPart():
                        chattable = chattables.TextMessage(
                            content=part.content,
                        )
                    case ToolCallPart():
                        chattable = chattables.ToolMessage(
                            tool_call_id=part.tool_call_id,
                            tool_name=part.tool_name,
                            tool_args=part.args_as_dict() or {},
                        )

                        # unless the history is corrupted, tool return
                        # must be in the next message
                        try:
                            next_message = messages[message_idx + 1]
                            [tool_return] = [
                                p
                                for p in next_message.parts
                                if isinstance(
                                    p, ToolReturnPart | RetryPromptPart
                                )
                                and p.tool_call_id == part.tool_call_id
                            ]

                            if isinstance(
                                tool_return, RetryPromptPart
                            ) or tool_return.metadata.get("is_failure", False):
                                chattable.result_status = "failure"
                            else:
                                chattable.result_status = "success"

                        except (IndexError, ValueError):
                            # the return part isn't there or is duplicated,
                            # so we won't be rendering a tick mark
                            pass

                    case ToolReturnPart():
                        # already handled in ToolCallPart
                        pass
                    case UserPromptPart():
                        assert isinstance(part.content, str), (
                            "We don't support non-text media in "
                            "user prompts yet"
                        )
                        chattable = chattables.UserMessage(
                            content=str(part.content),
                        )
                    case RetryPromptPart():
                        continue  # ignore retry prompts
                    case SystemPromptPart():
                        continue  # ignore system prompts
                    case _:
                        raise ValueError(f"Unknown part type: {type(part)}")

                if chattable is not None:
                    yield chattable

    async def make_panelable_tool_return(
        self, tool_return: ToolReturnPart
    ) -> panelables.ToolResultDetails | None:
        panelable: panelables.ToolResultDetails | None = None

        match tool_return.tool_name:
            case "rewrite" | "search_replace":
                # file path and diff
                path = tool_return.metadata.get("path", "Unknown path")
                header = f"[dim]({path})[/dim]"
                diff = tool_return.metadata.get("diff", "Diff unavailable")
                panelable = panelables.ToolResultDetails(
                    [
                        header,
                        rich.syntax.Syntax(
                            diff, "diff", background_color="default"
                        ),
                    ],
                    title=tool_return.tool_name,
                )

            case "list_files":
                # llm return and path
                path = tool_return.metadata.get("path", "Unknown path")
                header = f"[dim]({path})[/dim]"
                content = rich.text.Text(tool_return.content)
                panelable = panelables.ToolResultDetails(
                    [header, content],
                    title=tool_return.tool_name,
                )

            case "read_file":
                # llm return and path
                path = tool_return.metadata.get("path", "Unknown path")
                header = f"[dim]({path})[/dim]"
                extension = pathlib.Path(path).suffix[1:]  # remove leading dot
                content_text = tool_return.content
                syntax = rich.syntax.Syntax(
                    content_text,
                    extension,
                    line_numbers=True,
                    background_color="default",
                )
                panelable = panelables.ToolResultDetails(
                    [header, syntax],
                    title=tool_return.tool_name,
                )

            case "read_chunk":
                # llm return and path, bound_from_line, bound_to_line
                path = tool_return.metadata.get("path", "Unknown path")
                extension = pathlib.Path(path).suffix[1:]
                bound_from = tool_return.metadata.get("bound_from_line", 0)
                bound_to = tool_return.metadata.get("bound_to_line", 0)
                chunk = tool_return.metadata.get("chunk", "")
                header = f"[dim]({path})[/dim] (lines {bound_from}-{bound_to})"
                syntax = rich.syntax.Syntax(
                    chunk,
                    extension,
                    line_numbers=True,
                    start_line=bound_from + 1,
                    background_color="default",
                )
                panelable = panelables.ToolResultDetails(
                    [header, syntax],
                    title=tool_return.tool_name,
                )

            case "exec":
                cmd = tool_return.metadata.get("command")
                header = f"[dim]({cmd})[/dim]"
                if tool_return.content.strip():
                    panelable = panelables.ToolResultDetails(
                        [header, rich.text.Text(tool_return.content)],
                        title=tool_return.tool_name,
                    )

            case (
                "read_log"
                | "list_processes"
                | "process_info"
                | "command_history"
                | "command_output"
            ):
                # llm return
                panelable = panelables.ToolResultDetails(
                    [rich.text.Text(tool_return.content)],
                    title=tool_return.tool_name,
                )

            case _:
                pass

        return panelable
