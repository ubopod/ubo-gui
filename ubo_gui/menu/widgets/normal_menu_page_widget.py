"""Module for the `NormalMenuPageWidget` class."""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Sequence

from kivy.lang.builder import Builder

from ubo_gui.page import PageWidget

from .item_widget import ItemWidget

if TYPE_CHECKING:
    from ubo_gui.menu.types import Item


class NormalMenuPageWidget(PageWidget):
    """renders a normal page of a `Menu`."""

    def __init__(
        self: PageWidget,
        items: Sequence[Item | None] | None = None,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Initialize `NormalMenuPageWidget`."""
        self.item_widgets: list[ItemWidget] = []
        self.bind(on_kv_post=self.adjust_item_widgets)
        super().__init__(items, *args, **kwargs)
        self.bind(on_count=self.adjust_item_widgets)
        self.bind(items=self.render)

    def adjust_item_widgets(self: NormalMenuPageWidget, *args: object) -> None:
        """Initialize the widget."""
        _ = args
        for _ in range(len(self.item_widgets), self._count):
            self.item_widgets.append(ItemWidget(size_hint=(1, None)))
            self.ids.layout.add_widget(self.item_widgets[-1])
        for _ in range(self._count, len(self.item_widgets)):
            self.ids.layout.remove_widget(self.item_widgets[-1])
            del self.item_widgets[-1]
        self.render()

    def render(self: NormalMenuPageWidget, *_: object) -> None:
        """Render the widget."""
        if not self.item_widgets:
            return
        for i in range(self._count):
            self.item_widgets[i].item = self.items[i] if i < len(self.items) else None


Builder.load_file(
    pathlib.Path(__file__)
    .parent.joinpath('normal_menu_page_widget.kv')
    .resolve()
    .as_posix(),
)
