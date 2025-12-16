from typing import Protocol, Any, Sequence
import rich.traceback
from textual.widget import Widget
from textual.widgets import Static

# UI models adhering to the Panelable protocol are used to render
# content into the Panel widget


class Panelable(Protocol):
    def get_panel_widgets(self) -> Sequence[Widget]: ...


class TracebackDetails(Panelable):
    def __init__(self, error: Exception) -> None:
        self.error = error

    def get_panel_widgets(self) -> Sequence[Widget]:
        r = rich.traceback.Traceback.from_exception(
            type(self.error),
            self.error,
            self.error.__traceback__,
        )
        return [Static(r)]


class ToolResultDetails(Panelable):
    def __init__(self, content: list[Any]) -> None:
        self._content = content

    def get_panel_widgets(self) -> Sequence[Widget]:
        widgets = [Static(content) for content in self._content]
        return widgets
