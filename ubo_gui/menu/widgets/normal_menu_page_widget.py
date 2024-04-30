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
        self.bind(on_kv_post=self.render)
        super().__init__(items, *args, **kwargs)
        self.bind(items=self.render)

    def render(self: NormalMenuPageWidget, *_: object) -> None:
        """Render the widget."""
        self.ids.layout.clear_widgets()
        for i in range(self.count):
            self.ids.layout.add_widget(
                ItemWidget(
                    item=self.items[i] if i < len(self.items) else None,
                    size_hint=(1, None),
                ),
            )


Builder.load_file(
    pathlib.Path(__file__)
    .parent.joinpath('normal_menu_page_widget.kv')
    .resolve()
    .as_posix(),
)
