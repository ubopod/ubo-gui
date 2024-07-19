"""Module for the `HeaderMenuPageWidget` class."""

from __future__ import annotations

import pathlib
import warnings
from typing import TYPE_CHECKING, Any, Sequence

from kivy.lang.builder import Builder
from kivy.properties import StringProperty

from ubo_gui.menu.widgets.item_widget import ItemWidget
from ubo_gui.page import PageWidget

if TYPE_CHECKING:
    from ubo_gui.menu.types import Item


HEADER_SIZE = 2


class HeaderMenuPageWidget(PageWidget):
    """Renders a header page of a `Menu`."""

    heading = StringProperty()
    sub_heading = StringProperty()

    def __init__(
        self: HeaderMenuPageWidget,
        items: Sequence[Item | None] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Initialize a `HeaderMenuPageWidget`.

        Parameters
        ----------
        items: `Sequence`[[`Item`]]
            The item to be shown in this page

        kwargs: Any
            Stuff that will get directly passed to the `__init__` method of Kivy's
        `Screen`.

        """
        self.item_widgets: list[ItemWidget] = []
        self.bind(on_kv_post=self.adjust_item_widgets)
        super().__init__(items, **kwargs)
        self.bind(on_count=self.adjust_item_widgets)
        self.bind(items=self.render)

    def adjust_item_widgets(self: HeaderMenuPageWidget, *args: object) -> None:
        """Initialize the widget."""
        _ = args
        for _ in range(len(self.item_widgets), self.count - 2):
            self.item_widgets.append(ItemWidget(size_hint=(1, None)))
            self.ids.layout.add_widget(self.item_widgets[-1])
        for _ in range(self.count - 2, len(self.item_widgets)):
            self.ids.layout.remove_widget(self.item_widgets[-1])
            del self.item_widgets[-1]
        self.render()

    def render(self: HeaderMenuPageWidget, *_: object) -> None:
        """Render the widget."""
        if not self.item_widgets:
            return
        offset = 1 if self.render_surroundings else 0
        for i in range(self.count - 2):
            self.item_widgets[i].item = (
                self.items[i + offset] if i + offset < len(self.items) else None
            )

    def get_item(self: HeaderMenuPageWidget, index: int) -> Item | None:
        """Get the item at the given index."""
        offset = 1 if self.render_surroundings else 0
        if index < HEADER_SIZE:
            warnings.warn(
                f'index must be greater than or equal to {HEADER_SIZE}',
                ResourceWarning,
                stacklevel=1,
            )
            return None
        try:
            return self.items[index - HEADER_SIZE + offset]
        except IndexError:
            return None


Builder.load_file(
    pathlib.Path(__file__)
    .parent.joinpath('header_menu_page_widget.kv')
    .resolve()
    .as_posix(),
)
