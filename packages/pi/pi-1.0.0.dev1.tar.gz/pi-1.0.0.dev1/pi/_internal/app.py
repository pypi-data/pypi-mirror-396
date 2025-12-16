from __future__ import annotations

import asyncio
import typing
from typing import Any

import pyperclip
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.css.query import NoMatches
from textual.containers import (
    Horizontal,
    Vertical,
)

from pi._internal import bus
from pi._internal import rpc
from pi._internal import protocols
from pi._internal import agents
from pi._internal.agents import storage
from pi._internal import ai_conn as _ai_conn
from pi._internal.ui.widgets import layout, control, chat, panel
from pi._internal.ui.models import pickables, chattables, panelables


if typing.TYPE_CHECKING:
    from pydantic_ai.models import Model


BUS_NAME = "python-sidebar"


class PiApp(App[None]):
    BINDINGS = [
        ("ctrl+q", "noop", "Do Nothing"),
        ("escape", "close_sidebar", "Close the sidebar"),
        Binding(
            "tab", "cycle_focus_forward", "Cycle focus forward", priority=True
        ),
        Binding(
            "shift+tab",
            "cycle_focus_backward",
            "Cycle focus backward",
            priority=True,
        ),
    ]

    # disable textual's own command palette
    ENABLE_COMMAND_PALETTE = False

    bus: bus.Bus

    # renderable state
    history_storage: storage.HistoryStorage
    _current_session: storage.Session | None = None
    _last_error: Exception | None = None

    # track running agent task for cancellation
    _current_agent_task: asyncio.Task[None] | None = None

    CSS = """
    Screen {
        background: transparent;
    }

    #panel {
        width: 1fr;
        height: 100%;
        padding: 0;
        margin: 0;
        border: none;
        background: transparent;
    }

    #resize-handle {
        width: 1;
        height: 100%;
        background: transparent;
    }

    #resize-handle:hover {
        background: $primary;
    }

    #sidebar-content {
        width: 30%;
        min-width: 30;
        height: 100%;
    }

    #sidebar-input {
        dock: bottom;
    }
    """
    _cached_ai_conn: _ai_conn.Connector | None = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._message_timer = None
        self.history_storage = storage.HistoryStorage()

    def compose(self) -> ComposeResult:
        # Horizontal layout: left side shows shell, right side shows sidebar
        # content
        with Horizontal(id="horizontal-container"):
            # Left side: background fill (shell shows through)
            yield panel.Panel(id="panel")
            # Resize handle
            yield layout.ResizeHandle(id="resize-handle")
            # Right side: sidebar content (30% width, min 30 chars)
            with Vertical(id="sidebar-content"):
                yield chat.Chat(id="chat")
                yield control.SidebarInput(id="sidebar-input")

    # ShellEvents message subscriber
    async def terminal_event(
        self, *, event: protocols.shell.TerminalEvent
    ) -> None:
        if event.kind is protocols.shell.TerminalEventKind.SidebarActivated:
            # await self.on_pi_sidebar_activated()
            pass

    async def on_resize_handle_dragged(
        self, message: layout.ResizeHandle.Dragged
    ) -> None:
        # TODO add debouncing
        sidebar = self.query_one("#sidebar-content")
        sidebar.styles.width = f"{message.new_width_percent}%"

    async def on_sidebar_input_submit(
        self, message: control.SidebarInput.Submit
    ) -> None:
        self._current_agent_task = asyncio.create_task(
            self._handle_llm_stream(message.content)
        )
        message.stop()

    async def on_chat_text_selected(
        self, event: chat.Chat.TextSelected
    ) -> None:
        # put selected text on the clipboard
        # we have a special way of handling copy because cmd+c / cmd+v
        # cannot be used due to terminal-related limitations
        pyperclip.copy(event.text)
        sidebar_input = self.query_one("#sidebar-input", control.SidebarInput)
        await sidebar_input.show_hint("Selected text copied")

    async def on_sidebar_input_cancel(
        self, message: control.SidebarInput.Cancel
    ) -> None:
        if self._current_agent_task is not None:
            # the user wants to cancel the current agent run
            self._current_agent_task.cancel()
            self._current_agent_task = None
        else:
            # maybe the user is trying to quit using ctrl-c
            # so we should notify them that they're doing it wrong
            sidebar_input = self.query_one(
                "#sidebar-input", control.SidebarInput
            )
            sidebar_input.post_message(
                control.SidebarInput.WrongExit(message.key_combo)
            )

    async def on_sidebar_input_new_session_requested(
        self, message: control.SidebarInput.NewSessionRequested
    ) -> None:
        # the user has requested a new session
        # clear current chat history
        # remove only messages, but keep the streaming spinner
        chat_view = self.query_one("#chat", chat.Chat)
        messages = chat_view.query(chat.ChatMessage)
        await chat_view.remove_children(messages)

        shell = protocols.shell.interface(self.bus)
        self._current_session = self.history_storage.create_session(
            await shell.process_info()
        )

        # hide panel when starting a new session
        panel_view = self.query_one("#panel", panel.Panel)
        panel_view.hide()

    async def on_sidebar_input_session_requested(
        self, message: control.SidebarInput.SessionRequested
    ) -> None:
        # the user has requested an old session from the list
        # 1. clear current chat history
        chat_view = self.query_one("#chat", chat.Chat)
        # remove only messages, but keep the streaming spinner
        messages = chat_view.query(chat.ChatMessage)
        await chat_view.remove_children(messages)

        # hide the panel if it's up
        panel_view = self.query_one("#panel", panel.Panel)
        panel_view.hide()

        # 2. retrieve the session wrapped in the event, convert all messages
        # to Chattables via the UI adapter and pass them into the chat view
        self._current_session = message.pickable_session.session

        pydantic_messages = self._current_session.get_pydantic_ai_history()
        ui_adapter = agents.ui_adapter.UIAdapter()

        ui_messages: list[chattables.Chattable] = []
        async for ui_message in ui_adapter.make_chattables(pydantic_messages):
            ui_messages.append(ui_message)

        await chat_view.bulk_render(ui_messages)

    async def on_sidebar_input_session_list_requested(
        self, message: control.SidebarInput.SessionListRequested
    ) -> None:
        # prepare the list of sessions and push them into the SidebarInput's
        # navigation stack, because the SidebarInput is responsible for
        # rendering Pickers
        pickable_sessions = [
            pickables.PickableNewSession(),
            *[
                pickables.PickableSession.from_session(session)
                for session in self.history_storage.sessions.values()
            ],
        ]

        await message.control.push_session_picker(pickable_sessions)

    async def on_sidebar_input_chat_focus_requested(
        self, message: control.SidebarInput.ChatFocusRequested
    ) -> None:
        chat_view = self.query_one("#chat", chat.Chat)

        if chat_view.is_focusable:
            if message.direction == "up":
                # move focus straight up from the sidebar input
                # so it lands on the last tool call
                chat_view.focus_last_child()
            elif message.direction == "down":
                # move focus down from the sidebar input, so it
                # wraps around and lands on the first tool call
                chat_view.focus_first_child()

    async def on_sidebar_input_error_requested(
        self, message: control.SidebarInput.ErrorRequested
    ) -> None:
        # show the error details
        panel_view = self.query_one("#panel", panel.Panel)

        if self._last_error is not None:
            panelable = panelables.TracebackDetails(self._last_error)
            await panel_view.update_content(panelable)
            panel_view.show()
            panel_view.focus()
        else:
            sidebar_input = self.query_one(
                "#sidebar-input", control.SidebarInput
            )
            await sidebar_input.show_hint("No error to show")

    async def on_panel_focus_yielded(
        self, message: panel.Panel.FocusYielded
    ) -> None:
        # the panel has yielded focus to the app
        # so we can focus the sidebar input
        sidebar_input = self.query_one("#sidebar-input", control.SidebarInput)
        sidebar_input.focus()

    async def on_chat_focus_yielded(
        self, event: chat.Chat.FocusYielded
    ) -> None:
        # the chat has yielded focus to the app
        # so we can focus the sidebar input
        sidebar_input = self.query_one("#sidebar-input", control.SidebarInput)
        sidebar_input.focus()

        panel_view = self.query_one("#panel", panel.Panel)
        panel_view.hide()

    async def on_chat_tool_result_requested(
        self, event: chat.Chat.ToolResultRequested
    ) -> None:
        # the user has requested the result of a tool call
        # we need to fetch the tools result and put it on the panel
        assert self._current_session is not None, (
            "Current session should not be None by now"
        )

        tool_result = self._current_session.get_tool_result(event.tool_call_id)

        if tool_result is not None:
            ui_adapter = agents.ui_adapter.UIAdapter()
            panelable = await ui_adapter.make_panelable_tool_return(
                tool_result
            )
            if panelable is not None:
                panel_view = self.query_one("#panel", panel.Panel)
                await panel_view.update_content(panelable)
                panel_view.show()

    async def on_mount(self) -> None:
        self.bus = await bus.connect(name=BUS_NAME)
        rpc.listen(protocols.shell.ShellEvents, self.bus, self)

        # create a new chat session
        shell = protocols.shell.interface(self.bus)
        self._current_session = self.history_storage.create_session(
            await shell.process_info()
        )

        text_area = self.query_one("#input-text-area", control.SidebarTextArea)
        text_area.focus()

    async def on_unmount(self) -> None:
        try:
            bus = self.bus
        except AttributeError:
            pass
        else:
            await bus.close()

    async def action_close_sidebar(self) -> None:
        shell = protocols.shell.interface(self.bus)
        asyncio.create_task(shell.close_sidebar())

    async def action_cycle_focus_forward(self) -> None:
        current_widget = self.app.focused

        chat_view = self.query_one("#chat", chat.Chat)
        sidebar_input = self.query_one("#sidebar-input", control.SidebarInput)
        panel_view = self.query_one("#panel", panel.Panel)

        if current_widget is None:
            sidebar_input.focus()
        else:
            # sidebar input -> panel (if up) -> chat (if has tool calls)
            # -> sidebar input
            match current_widget:
                case control.SidebarTextArea():
                    if not panel_view.is_hidden:
                        panel_view.focus()
                    elif chat_view.is_focusable:
                        chat_view.focus_last_child()
                case chat.ChatMessage():
                    sidebar_input.focus()
                case panel.PanelContainer():
                    if chat_view.is_focusable:
                        chat_view.focus_last_child()
                    else:
                        sidebar_input.focus()
                case _:
                    # do not transfer focus
                    pass

    async def action_cycle_focus_backward(self) -> None:
        current_widget = self.app.focused

        chat_view = self.query_one("#chat", chat.Chat)
        sidebar_input = self.query_one("#sidebar-input", control.SidebarInput)
        panel_view = self.query_one("#panel", panel.Panel)

        if current_widget is None:
            sidebar_input.focus()
        else:
            # sidebar input -> chat (if has tool calls) -> panel (if up)
            # -> sidebar input
            match current_widget:
                case control.SidebarTextArea():
                    if chat_view.is_focusable:
                        chat_view.focus_last_child()
                    elif not panel_view.is_hidden:
                        panel_view.focus()
                case chat.ChatMessage():
                    if not panel_view.is_hidden:
                        panel_view.focus()
                    else:
                        sidebar_input.focus()
                case panel.PanelContainer():
                    sidebar_input.focus()
                case _:
                    # do not transfer focus
                    pass

    async def _get_ai_connector(self) -> _ai_conn.Connector:
        if self._cached_ai_conn is None:
            self._cached_ai_conn = _ai_conn.Connector.from_environment()
            await self._cached_ai_conn.validate_key()

        return self._cached_ai_conn

    async def _get_ai_model(self) -> Model:
        conn = await self._get_ai_connector()
        return conn.make_model()

    async def _handle_llm_stream(self, prompt: str) -> None:
        chat_view = self.query_one("#chat", chat.Chat)

        await chat_view.push_message(chattables.UserMessage(prompt))

        assert self._current_session is not None, (
            "Current session should not be None by now"
        )

        # update the display name for the list of sessions
        if self._current_session.display_name == "New robot":
            # XXX use a small model to generate the display name instead
            self._current_session.display_name = prompt.strip()[:100]

        # stream events from the agent loop as the LLM produces them
        # convert events to Chattables (a UI model) using the UI adapter
        # and feed those chattables into the chat view
        ui_adapter = agents.ui_adapter.UIAdapter()

        # we're keeping a single agent for now
        agent = agents.pi_agent
        deps = agents.deps.PiDeps(
            bus=self.bus,
            session=self._current_session,
        )

        try:
            # show the streaming indicator at the start
            await chat_view.start_streaming()

            agent.model = await self._get_ai_model()

            async for loop_event in agents.loop.run_agent(
                agent,
                user_prompt=prompt,
                deps=deps,
            ):
                ui_event = await ui_adapter.make_ui_stream_event(loop_event)
                # some events from the loop are ignored because they are not
                # relevant to the UI, so the adapter yields None for those
                if ui_event is not None:
                    await chat_view.handle_stream_event(ui_event)

        except asyncio.CancelledError:
            try:
                # agent was cancelled by user (ctrl+c) - stop gracefully
                sidebar_input = self.query_one(
                    "#sidebar-input", control.SidebarInput
                )
                await sidebar_input.show_hint("Run cancelled (ctrl-c)")
            except NoMatches:
                # the app is trying to shut down due to an error
                pass

        except Exception as e:
            # render the error into the chat view and save it so the user
            # can request detailed information
            self._last_error = e
            await chat_view.push_message(chattables.ErrorMessage(error=e))

        finally:
            await chat_view.stop_streaming()
            self._current_agent_task = None


if __name__ == "__main__":
    PiApp(ansi_color=True).run()
