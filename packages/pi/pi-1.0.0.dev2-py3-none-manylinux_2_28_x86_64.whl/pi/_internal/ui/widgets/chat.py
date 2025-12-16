from __future__ import annotations

import dataclasses
from typing import Any, Literal

from textual.containers import (
    VerticalScroll,
)
from textual.app import ComposeResult
from textual.widgets._markdown import MarkdownStream
from textual.message import Message
from textual.events import MouseUp, Click
from textual.containers import Container
from textual.widgets import Markdown, Static

from pi._internal.ui.models import chattables
from pi._internal.ui.widgets import graphics


class ChatHeader(Static):
    ALLOW_SELECT = False


class ChatMessage(Container, can_focus=True):
    """Renders a single Chattable into the chat view"""

    BINDINGS = [
        ("escape", "yield_focus", "Go back to sidebar input"),
        ("enter", "request_result", "Expand tool call"),
        ("up", "yield_focus('up')", "Previous tool call"),
        ("down", "yield_focus('down')", "Next tool call"),
        ("ctrl+p", "yield_focus('up')", "Previous tool call"),
        ("ctrl+n", "yield_focus('down')", "Next tool call"),
    ]

    DEFAULT_CSS = """
    ChatMessage {
        height: auto;
        width: 100%;
        background: transparent;
        margin-bottom: 1;
    }

    ChatMessage:focus {
        border-left: thick $primary;
        padding-left: 1;
    }

    ChatMessage Markdown {
        padding: 0;
    }

    ChatMessage Markdown > *:last-child {
        margin-bottom: 0;
    }

    ChatMessage.user-message {
    }

    ChatMessage.user-message > SlimBox {
        background: $surface;
    }

    ChatMessage.user-message > SlimBox > Markdown {
        padding: 0 2;
    }

    ChatMessage.thinking-message {
        color: $text-muted;
        text-style: italic;
    }

    ChatMessage.text-message {
    }

    ChatMessage.tool-message {
        margin-left: 2;
        margin-bottom: 1;  # re-specify because it gets reset otherwise
    }

    ChatMessage.error-message {
        margin-left: 2;
        margin-bottom: 1;  # re-specify because it gets reset otherwise
    }

    ChatMessage.error-message Markdown {
        padding-top: 1;
        color: $text-muted;
    }

    ChatMessage.hint {
        color: $text-muted;
    }
    """

    _markdown: Markdown | None = None
    _stream: MarkdownStream | None = None

    class FocusYielded(Message):
        def __init__(
            self,
            widget: ChatMessage,
            direction: Literal["up", "down"] | None = None,
        ) -> None:
            self.widget = widget
            self.direction = direction
            super().__init__()

        @property
        def control(self) -> ChatMessage:
            return self.widget

    class DetailsRequested(Message):
        def __init__(self, widget: ChatMessage, unhide: bool = True) -> None:
            self.widget = widget
            self.unhide = unhide  # unhide the panel if it's hidden
            super().__init__()

        @property
        def control(self) -> ChatMessage:
            return self.widget

    def __init__(self, chattable: chattables.Chattable, **kwargs: Any) -> None:
        super().__init__(classes=chattable.css_class, **kwargs)
        self.chattable = chattable
        self.can_focus = chattable.can_focus

    def compose(self) -> ComposeResult:
        header = self.chattable.get_chat_header()

        if header:
            yield ChatHeader(header, classes="chat-message-header")

        self._markdown = Markdown(self.chattable.get_chat_markdown_content())

        if self.chattable.has_slimbox:
            yield graphics.SlimBox(self._markdown)
        else:
            yield self._markdown

    def start_stream(self) -> MarkdownStream:
        if self._stream is None:
            assert self._markdown is not None
            self._stream = Markdown.get_stream(self._markdown)
        return self._stream

    async def write_to_stream(self, text: str) -> None:
        if self._stream is not None:
            await self._stream.write(text)

    async def stop_stream(self) -> None:
        if self._stream is not None:
            await self._stream.stop()

    async def refresh_header(self) -> None:
        # this could be a reactive attribute, but it would require
        # more complex setup for no good reason
        header_content = self.chattable.get_chat_header()
        if header_content:
            header = self.query_one(".chat-message-header", Static)
            header.update(header_content)

    async def action_yield_focus(
        self, direction: Literal["up", "down"] | None = None
    ) -> None:
        self.post_message(self.FocusYielded(self, direction))

    async def action_request_result(self) -> None:
        self.post_message(self.DetailsRequested(self))

    async def on_click(self, event: Click) -> None:
        # imitate the double click binding
        # textual doesn't seem to support using mouse in bindings
        if event.chain == 2 and self.chattable.can_focus:
            await self.action_request_result()
            event.stop()


@dataclasses.dataclass
class ChatStreamEvent:
    """
    Instructions for the Chat widget for handling a stream event.

    1. start_stream: push a new ChatMessage and get ready to stream to it
    2. apply_delta: write a delta to the current ChatMessage stream
    3. push: cut the stream and push a non-streaming message (e.g. a tool call)
    4. update: find and update a non-streaming message (e.g. add tool result)

    chattable is not None for start_stream and push
    (it's the chattable that needs to be rendered)

    delta is not None for apply_delta
    """

    action: Literal["start_stream", "apply_delta", "push", "update"]
    chattable: chattables.Chattable | None = None
    delta: str | None = None


class Chat(VerticalScroll, can_focus=False, can_focus_children=True):
    DEFAULT_CSS = """
    Chat {
        height: 1fr;
        width: 100%;
        margin: 0;
        padding: 0 1;
        scrollbar-size: 1 1;
        scrollbar-color: $primary;
        scrollbar-background: transparent;
        background: transparent;
        border: round $surface-lighten-3;
    }

    Chat:focus-within {
        border: round $primary;
    }
    """

    _streaming_message: ChatMessage | None = None

    class TextSelected(Message):
        def __init__(self, text: str) -> None:
            self.text = text
            super().__init__()

    class ToolResultRequested(Message):
        def __init__(self, tool_call_id: str, unhide: bool = True) -> None:
            self.tool_call_id = tool_call_id
            self.unhide = unhide  # unhide the panel if it's hidden
            super().__init__()

    class ErrorRequested(Message):
        pass

    class FocusYielded(Message):
        pass

    async def push_message(
        self, chattable: chattables.Chattable
    ) -> ChatMessage:
        message = ChatMessage(chattable)

        # always insert before the streaming indicator
        spinner = self.query_one("#streaming-indicator")
        await self.mount(message, before=spinner)

        self.scroll_end()
        return message

    async def bulk_render(
        self, chattables: list[chattables.Chattable]
    ) -> None:
        messages = [ChatMessage(chattable) for chattable in chattables]

        # always insert before the streaming indicator
        spinner = self.query_one("#streaming-indicator")
        await self.mount_all(messages, before=spinner)

        self.scroll_end()

    async def handle_stream_event(self, event: ChatStreamEvent) -> None:
        match event.action:
            case "start_stream":
                assert event.chattable is not None
                if self._streaming_message is not None:
                    await self._streaming_message.stop_stream()
                message = await self.push_message(event.chattable)
                message.start_stream()
                self._streaming_message = message
            case "apply_delta":
                assert event.delta is not None
                if self._streaming_message is not None:
                    await self._streaming_message.write_to_stream(event.delta)
            case "push":
                if self._streaming_message is not None:
                    await self._streaming_message.stop_stream()
                assert event.chattable is not None
                message = await self.push_message(event.chattable)
            case "update":
                # find and update the message with new content from chattable
                assert event.chattable is not None
                assert isinstance(event.chattable, chattables.ToolMessage)

                messages = self.query(ChatMessage)
                tool_calls = [
                    message
                    for message in messages
                    if isinstance(message.chattable, chattables.ToolMessage)
                    and message.chattable.tool_call_id
                    == event.chattable.tool_call_id
                ]

                # in case for whatever reason there's 0 or >1 of a tool call
                # marked with the same id already rendered in the UI
                if tool_calls:
                    tool_call = tool_calls[0]
                    assert isinstance(
                        tool_call.chattable, chattables.ToolMessage
                    )

                    tool_call.chattable.result_status = (
                        event.chattable.result_status
                    )
                    await tool_call.refresh_header()

        self.scroll_end()

    async def start_streaming(self) -> None:
        # only need to show the streaming indicator
        self.query_one("#streaming-indicator").display = True
        self.scroll_end()

    async def stop_streaming(self) -> None:
        if self._streaming_message is not None:
            await self._streaming_message.stop_stream()
        self._streaming_message = None

        # hide the streaming indicator
        self.query_one("#streaming-indicator").display = False

    async def pop_message(self) -> None:
        messages = self.query(ChatMessage)
        if messages and len(messages) > 0:
            await messages[-1].remove()
        self.scroll_end()

    @property
    def is_focusable(self) -> bool:
        messages = self.query(ChatMessage)
        focusable = [message for message in messages if message.can_focus]
        return len(focusable) > 0

    def focus_first_child(self) -> None:
        messages = self.query(ChatMessage)
        focusable = [message for message in messages if message.can_focus]
        if focusable:
            focusable[0].focus()
            focusable[0].scroll_visible()

    def focus_last_child(self) -> None:
        messages = self.query(ChatMessage)
        focusable = [message for message in messages if message.can_focus]
        if focusable:
            focusable[-1].focus()

    def on_mouse_up(self, event: MouseUp) -> None:
        # this is a special handler to enable copy-paste from the chat view
        # normal cmd+c / cmd+v won't work due to terminal-related limitations

        # text may be spread across multiple widgets, so we need to collect it
        # by walking Chat's descendants
        result: list[str] = []
        for widget, selection in self.screen.selections.items():
            if self in widget.ancestors:
                selected = widget.get_selection(selection)
                if not selected:
                    continue
                text, ending = selected
                if not text:
                    continue
                result.append(text)
                result.append(ending)

        ret = "".join(result).rstrip("\n")
        if ret:
            self.post_message(self.TextSelected(ret))

    async def on_chat_message_focus_yielded(
        self, event: ChatMessage.FocusYielded
    ) -> None:
        # yield focus if no direction is provided
        # otherwise find next / previous tool call
        # that can be focused and focus it
        if event.direction is None:
            self.post_message(self.FocusYielded())
            event.stop()
        else:
            messages = list(self.query(ChatMessage))
            focusable = [message for message in messages if message.can_focus]
            # there has to be at least one by definition of the event

            current_index = focusable.index(event.control)
            match event.direction:
                case "up":
                    if current_index == 0:
                        # if currently at the top message, cycle focus
                        # to chat input
                        self.post_message(self.FocusYielded())
                        event.stop()
                    else:
                        # move focus upwards
                        previous_index = (current_index - 1) % len(focusable)
                        widget = focusable[previous_index]
                        widget.focus()
                        widget.post_message(
                            ChatMessage.DetailsRequested(widget, unhide=False)
                        )
                case "down":
                    if current_index == len(focusable) - 1:
                        # if currently at the bottom message, cycle focus
                        # to chat input
                        self.post_message(self.FocusYielded())
                        event.stop()
                    else:
                        # move focus to the next focusable tool call
                        next_index = (current_index + 1) % len(focusable)
                        widget = focusable[next_index]
                        widget.focus()
                        widget.post_message(
                            ChatMessage.DetailsRequested(widget, unhide=False)
                        )
            event.stop()

    async def on_chat_message_details_requested(
        self, event: ChatMessage.DetailsRequested
    ) -> None:
        # show details for the chattable
        match event.widget.chattable:
            case chattables.ToolMessage():
                self.post_message(
                    self.ToolResultRequested(
                        event.widget.chattable.tool_call_id,
                        unhide=event.unhide,
                    )
                )
            case chattables.ErrorMessage():
                self.post_message(self.ErrorRequested())
            case _:
                raise ValueError(
                    f"Can't request details for {type(event.widget.chattable)}"
                )

    async def on_mount(self) -> None:
        # mount the streaming indicator
        spinner = graphics.StreamingIndicator(id="streaming-indicator")
        spinner.display = False
        await self.mount(spinner)
