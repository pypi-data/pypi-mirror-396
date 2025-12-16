from __future__ import annotations

from typing import Any
from textual.widgets import Static
from textual.message import Message
from textual.containers import VerticalScroll
from textual.widget import Widget

from pi._internal.ui.models import pickables
from pi._internal.ui.widgets import graphics


class PickerItem(Static, can_focus=True):
    """A single pickable item in the picker"""

    DEFAULT_CSS = """
    PickerItem {
        padding: 0 2;
        height: auto;
        width: 100%;
        background: $surface;
    }

    PickerItem:focus {
        background: $secondary;
        color: $text;
    }

    PickerItem.hover {
        background: $primary;
        color: $text;
    }
    """

    BINDINGS = [
        ("enter", "pick", "Pick this item"),
    ]

    up_sep: graphics.Separator
    down_sep: graphics.Separator

    class Picked(Message):
        def __init__(self, widget: PickerItem) -> None:
            self.widget = widget
            super().__init__()

        @property
        def control(self) -> PickerItem:
            return self.widget

    class Hovered(Message):
        def __init__(self, widget: PickerItem) -> None:
            self.widget = widget
            super().__init__()

        @property
        def control(self) -> PickerItem:
            return self.widget

    def __init__(
        self,
        pickable: pickables.Pickable,
        up_sep: graphics.Separator,
        down_sep: graphics.Separator,
        **kwargs: Any,
    ) -> None:
        super().__init__("", **kwargs)
        self.pickable = pickable

        self.up_sep = up_sep
        self.down_sep = down_sep

    def hover(self) -> None:
        # not to be used directly by the PickerItem itself
        # because there's Picker logic that relies on .hover
        self.up_sep.add_class("up")
        self.down_sep.add_class("down")
        self.add_class("hover")

    def unhover(self) -> None:
        self.up_sep.remove_class("up")
        self.down_sep.remove_class("down")
        self.remove_class("hover")

    async def action_pick(self) -> None:
        self.post_message(self.Picked(widget=self))
        # everything else will be handled by the parent Picker

    def on_mount(self) -> None:
        """Render the item when mounted"""
        self.update(self.pickable.get_picker_label())

    async def on_focus(self) -> None:
        self.post_message(self.Hovered(widget=self))
        await self.action_pick()

    def on_blur(self) -> None:
        self.unhover()


class Picker(VerticalScroll):
    """A navigable list of pickables"""

    DEFAULT_CSS = """
    Picker {
        height: 100%;
        scrollbar-size: 1 1;
        scrollbar-color: #5f5faf;
        align: center bottom;
    }

    Picker.bottom-docked {
    }

    Picker > Container {
        height: auto;
    }
    """

    hover_item_index: int = 0

    class Selected(Message):
        def __init__(self, widget: Picker, pickable: pickables.Pickable):
            self.widget = widget
            self.pickable = pickable
            super().__init__()

        @property
        def control(self) -> Picker:
            # the picker that sent the message
            # necessary to enable the @on decorator
            return self.widget

    class Cancelled(Message):
        def __init__(self, widget: Picker) -> None:
            self.widget = widget
            super().__init__()

        @property
        def control(self) -> Picker:
            return self.widget

    async def bulk_render(self, pickables: list[pickables.Pickable]) -> None:
        """Render items from pickables"""
        await self.remove_children()

        if not pickables:
            return

        sorted_pickables = sorted(
            pickables,
            key=lambda p: p.get_picker_sort_key(),
        )

        widgets: list[Widget] = []
        prev_sep = graphics.Separator()
        widgets.append(prev_sep)
        for pickable in sorted_pickables:
            next_sep = graphics.Separator()
            item = PickerItem(
                pickable=pickable,
                up_sep=prev_sep,
                down_sep=next_sep,
            )
            widgets.append(item)
            widgets.append(next_sep)
            prev_sep = next_sep

        await self.mount_all(widgets)

        self.query(PickerItem).last().hover()
        self.refresh()

    async def action_move_hover(self, delta: int) -> None:
        """Move hover up or down"""

        items = self.query(PickerItem)

        hover_item = items.filter(".hover").first()
        hover_index = list(items).index(hover_item) if hover_item else 0

        hover_item.unhover()
        new_index = (hover_index + delta) % len(items)
        items[new_index].hover()
        items[new_index].scroll_visible()

    async def action_pick(self) -> None:
        # forward action to the item
        # everything else will be handled in on_picker_item_picked
        await self.query_one(".hover", PickerItem).action_pick()

    async def action_cancel(self) -> None:
        self.post_message(self.Cancelled(widget=self))

    async def on_picker_item_hovered(self, event: PickerItem.Hovered) -> None:
        items = self.query(PickerItem).filter(".hover")

        if items:
            hover_item = items.first()
            hover_item.unhover()

        event.control.hover()
        event.control.scroll_visible()

    async def on_picker_item_picked(self, event: PickerItem.Picked) -> None:
        """Handle item picked messages from PickerItems"""
        self.post_message(
            self.Selected(widget=self, pickable=event.control.pickable)
        )
