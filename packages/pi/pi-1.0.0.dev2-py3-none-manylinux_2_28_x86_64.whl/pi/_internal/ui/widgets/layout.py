from typing import Any

from textual.widgets import Static
from textual.message import Message
from textual.events import MouseDown, MouseUp, MouseMove


class ResizeHandle(Static):
    """A draggable vertical resize handle"""

    class Dragged(Message):
        def __init__(self, new_width_percent: int):
            self.new_width_percent = new_width_percent
            super().__init__()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__("", **kwargs)
        self.is_dragging = False

    def on_mouse_down(self, event: MouseDown) -> None:
        self.is_dragging = True
        self.capture_mouse()
        event.stop()

    def on_mouse_up(self, event: MouseUp) -> None:
        self.is_dragging = False
        self.release_mouse()
        event.stop()

    def on_mouse_move(self, event: MouseMove) -> None:
        if self.is_dragging:
            # Calculate new sidebar width as percentage
            terminal_width = self.screen.size.width
            # event.screen_x is the x position on the screen
            new_width_percent = int(
                ((terminal_width - event.screen_x) / terminal_width) * 100
            )

            # Clamp between 20% and 80%
            new_width_percent = max(20, min(80, new_width_percent))

            self.post_message(self.Dragged(new_width_percent))
            event.stop()
