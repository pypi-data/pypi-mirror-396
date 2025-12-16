from textual.widget import Widget
from wcwidth import wcwidth  # type: ignore[import-untyped]

from textual.widgets import Static
from textual.containers import VerticalScroll
from textual.app import ComposeResult
from textual.message import Message

from pi._internal.ui.models import panelables

# Pick a private-use character with a width of 1 as our background
# Keep in sync with virtual_pty.rs
TRANSPARENT_CHAR = "\ue000"
assert wcwidth(TRANSPARENT_CHAR) == 1


class PanelContainer(VerticalScroll, can_focus=True):
    BINDINGS = [
        ("escape", "hide", "Hide the panel"),
    ]

    class HideRequested(Message):
        pass

    async def action_hide(self) -> None:
        self.post_message(self.HideRequested())


class Panel(Static, can_focus=True, can_focus_children=True):
    """Widget that fills the entire screen with the transparent background
    character"""

    DEFAULT_CSS = """
    Panel {
        border: none;
        background: transparent;
    }

    #panel-container {
        height: 100%;
        width: 100%;
        margin: 4 8;
        padding: 2 4;
        border: round $surface-lighten-3;
        background: transparent;
        scrollbar-size: 1 1;
        scrollbar-color: $primary;
        scrollbar-background: transparent;
    }

    #panel-container:focus {
        border: round $primary;
    }

    #panel-container.hidden {
        display: none;
    }

    #panel-container > Static {
        margin-bottom: 1;
    }

    #panel-container > Static:last-child {
        margin-bottom: 0;
    }
    """

    _panel_content: Widget | None = None

    class FocusYielded(Message):
        pass

    def compose(self) -> ComposeResult:
        yield PanelContainer(id="panel-container", classes="hidden")

    def render(self) -> str:
        # Fill the entire widget area with the background character
        # This character signals to the Rust renderer to show shell content
        # instead
        width, height = self.size
        if width == 0 or height == 0:
            return TRANSPARENT_CHAR
        # Create a grid of background characters
        line = TRANSPARENT_CHAR * width
        return "\n".join([line] * height)

    async def update_content(self, panelable: panelables.Panelable) -> None:
        container = self.query_one("#panel-container")
        await container.remove_children()
        widgets = panelable.get_panel_widgets()
        container.mount_all(widgets)

    def show(self) -> None:
        container = self.query_one("#panel-container")
        container.remove_class("hidden")

    def hide(self) -> None:
        container = self.query_one("#panel-container")
        container.add_class("hidden")

    @property
    def is_hidden(self) -> bool:
        container = self.query_one("#panel-container")
        return container.has_class("hidden")

    def on_resize(self) -> None:
        """Re-render when the widget size changes"""
        self.refresh()

    async def on_focus(self) -> None:
        # pass focus to the child container that's going to
        # draw the border and handle all the key presses.
        # this is to simplify focus management at the app level
        # so that the app can focus the panel itself
        container = self.query_one("#panel-container")
        container.focus()

    async def on_panel_container_hide_requested(
        self, message: PanelContainer.HideRequested
    ) -> None:
        self.hide()
        self.post_message(self.FocusYielded())
        message.stop()
