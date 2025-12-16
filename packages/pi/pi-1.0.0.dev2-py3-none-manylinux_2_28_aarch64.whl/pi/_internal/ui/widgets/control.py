from __future__ import annotations

import asyncio
from typing import cast, Any, Literal

from rapidfuzz import fuzz
import rich.text

from textual import on
from textual.app import ComposeResult
from textual.timer import Timer
from textual.widgets import Static, TextArea
from textual.containers import Container
from textual.message import Message
from textual.events import Key

from pi._internal.ui.widgets import picker
from pi._internal.ui.models import pickables


class SidebarTextArea(TextArea):
    # customized version of TextArea that overrides some
    # key handling defaults and placeholder behavior
    PROMPT = "Your quest?"
    PROMPT_WS = " " * 5

    PLACEHOLDERS = [
        # Longest
        f"[i]{PROMPT}[/i]{PROMPT_WS}"
        "[dim][reverse] ↩ [/reverse] [i]send[/i][/dim]   "
        "[dim][reverse] ⎋ [/reverse] [i]quit[/i][/dim]   "
        "[dim][reverse] / [/reverse] [i]cmd[/i][/dim]",
        # Long
        f"[i]{PROMPT}[/i]{PROMPT_WS}"
        "[dim][reverse] ↩ [/reverse] [i]send[/i][/dim]   "
        "[dim][reverse] ⎋ [/reverse] [i]quit[/i][/dim]",
        # Shorter
        f"[i]{PROMPT}[/i]{PROMPT_WS}"
        f"[dim][reverse] ↩ [/reverse] [i]send[/i][/dim]",
        # Shortest
        f"[i]{PROMPT}[/i]",
    ]

    PLACEHOLDERS_LEN = [
        len(rich.text.Text.from_markup(placeholder).plain)
        for placeholder in PLACEHOLDERS
    ]

    # these keys are handled by the sidebar input
    BINDINGS = [
        ("up", "noop", ""),
        ("down", "noop", ""),
        ("enter", "noop", ""),
    ]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(placeholder=self.PLACEHOLDERS[0], **kwargs)
        self.highlight_cursor_line = False

    async def on_key(self, event: Key) -> None:
        if event.key in ("enter", "up", "down"):
            event.prevent_default()
        elif event.key in ("shift+enter", "ctrl+j"):
            # apparently terminals intercept shift+enter
            # and turn it into ctrl+j
            self.insert("\n")
            event.prevent_default()

    async def on_resize(self) -> None:
        # update the placeholder
        max_width = self.size.width - 6  # Account for padding

        for placeholder, placeholder_len in zip(
            self.PLACEHOLDERS, self.PLACEHOLDERS_LEN, strict=True
        ):
            if placeholder_len < max_width:
                self.placeholder = placeholder
                return


class SidebarInput(Container, can_focus=True):
    """
    This widget manages all user inputs, which currently may include text
    and selecting things from a Picker menu.

    As such, it owns the state of the navigation stack (a stack of Pickers),
    displays hints to guide the user, and emits custom events to notify the app
    and other widgets of user's actions.
    """

    BINDINGS = [
        ("enter", "submit", "Submit text or picker selection"),
        (
            "ctrl+c",
            "interrupt_agent('ctrl+c')",
            "Interrupt the current agent run",
        ),
        ("ctrl+d", "wrong_exit('ctrl+d')", "Wrong exit"),
        ("ctrl+q", "wrong_exit('ctrl+q')", "Wrong exit"),
        ("up", "up", "Move picker selection up or switch to chat"),
        ("down", "down", "Move picker selection down"),
        ("ctrl+p", "up", "Move picker selection up or switch to chat"),
        ("ctrl+n", "down", "Move picker selection down"),
        ("escape", "picker_cancel", "Cancel picker and go back"),
    ]

    DEFAULT_CSS = """
    SidebarInput {
        height: auto;
        width: 100%;
        border: none;
        margin: 0;
        padding: 0;
    }

    SidebarInput #nav-container {
        width: 100%;
    }

    SidebarInput #nav-container.hidden {
        display: none;
    }

    SidebarInput #input-text-area {
        height: auto;
        width: 1fr;
        margin: 0;
        padding: 0 2;
        border: round $surface-lighten-3;
        background: transparent;
    }

    SidebarInput #input-text-area:focus {
        border: round $primary;
    }

    SidebarInput #hint {
        color: $text-muted;
        margin: 0 2;
        margin-bottom: 1;
    }

    SidebarInput #hint.hidden {
        display: none;
    }
    """

    # STATE
    # commands that are available in the command palette
    _commands: list[pickables.Command] = [
        pickables.Command(
            id="/error",
            label="Show Error Details",
            description="Show detailed error information",
        ),
        pickables.Command(
            id="/new",
            label="New Session",
            description="Create a new chat session",
        ),
        pickables.Command(
            id="/list",
            label="List Sessions",
            description="Show all chat sessions",
        ),
    ]

    # threshold to filter out commands that do not match the query
    _fuzzy_threshold: float = 30.0

    # current nav stack. it can go up to two levels deep:
    # level 1: command palette
    # level 2: session picker
    # the user can go back up the stack using escape
    _nav_stack: list[picker.Picker] = []

    # timer to track when hints expire
    _hint_timer: Timer | None = None

    # CUSTOM EVENTS
    class Submit(Message):
        def __init__(self, content: str):
            self.content = content
            super().__init__()

    class Cancel(Message):
        def __init__(self, key_combo: str) -> None:
            self.key_combo = key_combo
            super().__init__()

    class WrongExit(Message):
        def __init__(self, key_combo: str) -> None:
            self.key_combo = key_combo
            super().__init__()

    class CommandChanged(Message):
        def __init__(self, text: str) -> None:
            self.text = text
            super().__init__()

    class RegularTextChanged(Message):
        def __init__(self, text: str) -> None:
            self.text = text
            super().__init__()

    class SessionListRequested(Message):
        def __init__(self, widget: SidebarInput) -> None:
            self.widget = widget
            super().__init__()

        @property
        def control(self) -> SidebarInput:
            return self.widget

    class NewSessionRequested(Message):
        def __init__(self) -> None:
            super().__init__()

    class SessionRequested(Message):
        def __init__(
            self, pickable_session: pickables.PickableSession
        ) -> None:
            self.pickable_session = pickable_session
            super().__init__()

    class ChatFocusRequested(Message):
        def __init__(self, direction: Literal["up", "down"] = "up") -> None:
            self.direction = direction
            super().__init__()

    class ErrorRequested(Message):
        pass

    def compose(self) -> ComposeResult:
        yield Container(id="nav-container", classes="hidden")
        yield Static("", id="hint", classes="hidden")
        yield SidebarTextArea(id="input-text-area")

    # NAVIGATION
    async def push_to_nav_stack(
        self,
        picker_widget: picker.Picker,
        pickables: list[pickables.Pickable] | None = None,
    ) -> None:
        """Push a new widget onto the nav stack"""
        container = self.query_one("#nav-container")
        container.remove_class("hidden")

        # hide all previous widgets
        for w in self._nav_stack:
            w.display = False

        # add new widget to the stack
        self._nav_stack.append(picker_widget)
        await container.mount(picker_widget)
        if pickables is not None:
            await picker_widget.bulk_render(pickables)

    async def pop_from_nav_stack(self) -> None:
        """Pop the top widget from the nav stack"""
        if not self._nav_stack:
            return

        # remove current top
        current = self._nav_stack.pop()
        await current.remove()

        # clear the text area
        text_area = self.query_one("#input-text-area", SidebarTextArea)
        with text_area.prevent(TextArea.Changed):
            text_area.text = ""

        # show previous if exists
        if self._nav_stack:
            self._nav_stack[-1].display = True

            if self._nav_stack[-1].id == "command-picker":
                # populate with "/" and move cursor to the right
                with text_area.prevent(TextArea.Changed):
                    text_area.text = "/"
                    text_area.move_cursor_relative(columns=1)
        else:
            # hide the container if there are no more widgets
            container = self.query_one("#nav-container")
            container.add_class("hidden")

    async def push_session_picker(
        self, sessions: list[pickables.Pickable]
    ) -> None:
        """Push session picker to nav stack"""

        # this method is called by the app. the app handles this
        # because it owns the the session state
        session_picker = picker.Picker(id="session-picker")
        asyncio.create_task(self.push_to_nav_stack(session_picker, sessions))

    # HINTS
    async def show_hint(self, hint: str, duration: float = 2.0) -> None:
        if self._hint_timer:
            self._hint_timer.stop()
            self._hint_timer = None

        hint_widget = self.query_one("#hint", Static)
        hint_widget.remove_class("hidden")
        hint_widget.update(hint)
        self._hint_timer = self.app.set_timer(duration, self.hide_hint)

    async def hide_hint(self) -> None:
        hint_widget = self.query_one("#hint", Static)
        hint_widget.add_class("hidden")
        self._hint_timer = None

    # EVENT HANDLERS
    async def on_text_area_changed(self, change: TextArea.Changed) -> None:
        # the user is typing something into the text area
        # it can be a command or an LLM prompt
        if change.text_area.text.startswith("/"):
            self.post_message(self.CommandChanged(change.text_area.text))
        else:
            self.post_message(self.RegularTextChanged(change.text_area.text))

    async def on_sidebar_input_command_changed(
        self, message: CommandChanged
    ) -> None:
        # push command palette to nav stack if it's not there
        # update command palette sorting

        # command palette is normally the first in the stack
        if not self._nav_stack:
            command_picker = picker.Picker(id="command-picker")
            asyncio.create_task(
                self.push_to_nav_stack(
                    command_picker,
                    cast(list[pickables.Pickable], self._commands),
                )
            )

        # update fuzzy scores for all commands to re-sort them
        query = message.text.lower().lstrip("/")

        filtered_commands: list[pickables.Command] = []
        for cmd in self._commands:
            if not query:
                # No query, give all commands equal score
                cmd.score = 100.0
            else:
                # Use fuzzy matching to score commands
                id_score = fuzz.ratio(query, cmd.id.lower().lstrip("/"))
                label_score = fuzz.ratio(query, cmd.label.lower().lstrip("/"))
                desc_score = fuzz.ratio(
                    query, cmd.description.lower().lstrip("/")
                )

                # Take the best score
                cmd.score = float(max(id_score, label_score, desc_score))

            if cmd.score > self._fuzzy_threshold:
                filtered_commands.append(cmd)

        # re-render with new scores
        assert (
            self._nav_stack and self._nav_stack[-1].id == "command-picker"
        ), f"Command picker should be on top, got {self._nav_stack[-1].id}"

        command_picker = self._nav_stack[-1]
        await command_picker.bulk_render(
            cast(list[pickables.Pickable], filtered_commands)
        )

        message.stop()

    async def on_sidebar_input_regular_text_changed(
        self, message: RegularTextChanged
    ) -> None:
        # if session list is on top, update sorting
        # if command palette is on top, pop it
        # if neither of those, do nothing

        if self._nav_stack and self._nav_stack[-1].id == "session-picker":
            # update sorting
            pass
        elif self._nav_stack and self._nav_stack[-1].id == "command-picker":
            asyncio.create_task(self.pop_from_nav_stack())

        message.stop()

    @on(picker.Picker.Selected, "#command-picker")
    async def handle_command_selected(
        self, message: picker.Picker.Selected
    ) -> None:
        # handle different commands:
        # for new emit a session change
        # for list push the new ui to the nav stack and render it
        # for error push the error ui to the nav stack and render it

        assert isinstance(message.pickable, pickables.Command), (
            f"Message pickable must be a Command, got {type(message.pickable)}"
        )

        match message.pickable.id:
            case "/new":
                self.post_message(self.NewSessionRequested())
                # reset sidebar input state
                for _ in range(len(self._nav_stack)):
                    asyncio.create_task(self.pop_from_nav_stack())
                self.query_one("#input-text-area", SidebarTextArea).text = ""
            case "/list":
                # request session list from app
                self.post_message(self.SessionListRequested(self))
                # the session picker will be pushed to nav stack by the app
                # because the app owns the session list
            case "/error":
                self.post_message(self.ErrorRequested())
                self.query_one("#input-text-area", SidebarTextArea).text = ""
            case _:
                pass

        text_area = self.query_one("#input-text-area", SidebarTextArea)
        with text_area.prevent(TextArea.Changed):
            text_area.text = ""
        text_area.focus()

        message.stop()

    @on(picker.Picker.Selected, "#session-picker")
    async def handle_session_selected(
        self, message: picker.Picker.Selected
    ) -> None:
        # emit a session change, clear nav stack

        match message.pickable:
            case pickables.PickableNewSession():
                self.post_message(self.NewSessionRequested())
            case pickables.PickableSession():
                self.post_message(self.SessionRequested(message.pickable))
            case _:
                raise ValueError(
                    f"Unknown pickable type: {type(message.pickable)}"
                )

        message.stop()
        text_area = self.query_one("#input-text-area", SidebarTextArea)
        text_area.focus()

        # reset sidebar input state
        for _ in range(len(self._nav_stack)):
            asyncio.create_task(self.pop_from_nav_stack())

    async def on_picker_cancelled(
        self, message: picker.Picker.Cancelled
    ) -> None:
        asyncio.create_task(self.pop_from_nav_stack())
        message.stop()

    async def on_focus(self) -> None:
        # pass focus to the text area
        # this is to simplify focus management at the app level
        # so that the app can focus the sidebar input itself
        text_area = self.query_one("#input-text-area", SidebarTextArea)
        text_area.focus()

    async def on_sidebar_input_wrong_exit(self, message: WrongExit) -> None:
        await self.show_hint(
            f"\\[Esc] to close (instead of {message.key_combo})"
        )
        message.stop()

    def check_action(
        self, action: str, parameters: tuple[object, ...]
    ) -> bool | None:
        # route keystrokes between the text area and the picker
        # when the picker is up, it receives navigation, submit and exit
        if action.startswith("picker_"):
            return bool(self._nav_stack)
        else:
            return True

    async def action_up(self) -> None:
        if self._nav_stack:
            # when there's a picker, cycle through options
            await self.action_picker_move_selection(-1)
        else:
            # otherwise move focus to chat to select a tool call
            # to render in the panel view
            self.post_message(self.ChatFocusRequested(direction="up"))

    async def action_down(self) -> None:
        if self._nav_stack:
            # when there's a picker, cycle through options
            await self.action_picker_move_selection(1)
        else:
            # otherwise move focus to chat to select a tool call
            # to render in the panel view
            self.post_message(self.ChatFocusRequested(direction="down"))

    async def action_submit(self) -> None:
        # route submit separately because can't bind two actions
        # to the same key combination
        if self._nav_stack:
            await self._nav_stack[-1].action_pick()
        else:
            chat_input = self.query_one("#input-text-area", SidebarTextArea)
            if chat_input.text:
                self.post_message(self.Submit(chat_input.text))
                chat_input.text = ""

    async def action_interrupt_agent(self, key: str) -> None:
        self.post_message(self.Cancel(key))

    async def action_wrong_exit(self, key: str) -> None:
        self.post_message(self.WrongExit(key))

    async def action_picker_move_selection(self, delta: int) -> None:
        await self._nav_stack[-1].action_move_hover(delta)

    async def action_picker_cancel(self) -> None:
        await self._nav_stack[-1].action_cancel()
