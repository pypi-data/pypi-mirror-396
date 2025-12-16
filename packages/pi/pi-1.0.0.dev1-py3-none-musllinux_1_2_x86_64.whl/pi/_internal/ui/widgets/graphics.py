import asyncio
from typing import Self
from rich.segment import Segment
from rich.style import Style

from textual.containers import Container
from textual.geometry import Region, Size
from textual.strip import Strip
from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult
from textual import work


class BaseLine(Widget):
    DEFAULT_CSS = """
    BaseLine {
        width: 100%;
        height: 1;
    }
    """

    ALLOW_SELECT = False

    char: str

    def render(self) -> str:
        # Make this widget "unselectable" -- it ultimately has no text value.
        return ""

    def get_content_height(
        self, container: Size, viewport: Size, width: int
    ) -> int:
        return 1

    def render_lines(self, crop: Region) -> list[Strip]:
        width = crop.width

        widget_bg_color = self.background_colors[1]
        widget_bg = widget_bg_color.rich_color if widget_bg_color else None

        # For half blocks: color is the foreground (the half that's filled)
        border_style = Style(color=widget_bg)

        return [
            Strip(
                [Segment(self.char * width, border_style)],
                width,
            ),
        ]


class TopLine(BaseLine):
    DEFAULT_CSS = """
    TopLine {
        dock: top;
    }
    """

    char: str = "▄"


class BottomLine(BaseLine):
    DEFAULT_CSS = """
    TopLine {
        dock: bottom;
    }
    """

    char: str = "▀"


class SlimBox(Container):
    DEFAULT_CSS = """
    SlimBox {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield TopLine()
        yield from super().compose()
        yield BottomLine()


class Separator(BaseLine):
    char = " "

    DEFAULT_CSS = """
    Separator.up, Separator.down {
        background: $primary;
    }
    """

    def add_class(self, *class_names: str, update: bool = True) -> Self:
        if "up" in class_names:
            self.char = "▄"
            self.refresh()
        elif "down" in class_names:
            self.char = "▀"
            self.refresh()
        else:
            self.char = " "
            self.refresh()

        return super().add_class(*class_names, update=update)

    def remove_class(self, *class_names: str, update: bool = True) -> Self:
        if "up" in class_names or "down" in class_names:
            self.char = " "
            self.refresh()

        return super().remove_class(*class_names, update=update)


class StreamingIndicator(Static):
    DEFAULT_CSS = """
    StreamingIndicator {
        height: 1;
        margin: 1 0;
        color: $text-muted;
    }
    """

    FRAMES = [
        "⠀ ",
        "⠁ ",
        "⠉ ",
        "⠉⠁",
        "⠋⠁",
        "⠛⠁",
        "⠛⠃",
        "⠟⠃",
        "⠿⠃",
        "⠿⠇",
        "⠾⠇",
        "⠶⠇",
        "⠶⠆",
        "⠴⠆",
        "⠤⠆",
        "⠤⠄",
        "⠠⠄",
        " ⠄",
    ]

    def on_mount(self) -> None:
        """Start the spinner when mounted."""
        self.spinner_worker = self.animate_spinner()

    @work(exclusive=True)
    async def animate_spinner(self) -> None:
        index = 0
        while True:
            self.update(self.FRAMES[index])
            index = (index + 1) % len(self.FRAMES)
            await asyncio.sleep(0.1)

    def on_unmount(self) -> None:
        self.spinner_worker.cancel()
