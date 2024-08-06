"""Module for the `NormalMenuPageWidget` class."""

from __future__ import annotations

import pathlib
import warnings
from typing import TYPE_CHECKING, Any, Sequence

from kivy.lang.builder import Builder
from kivy.properties import AliasProperty, NumericProperty, StringProperty

from ubo_gui.menu.widgets.item_widget import ItemWidget
from ubo_gui.page import PageWidget

if TYPE_CHECKING:
    from ubo_gui.menu.types import Item


HEADER_SIZE = 2


class MenuPageWidget(PageWidget):
    """renders a page of a `Menu`."""

    def get_has_heading(self: MenuPageWidget) -> bool:
        """Check if the page is rendering a heading."""
        return self.page_index == 0 and bool(self.heading or self.sub_heading)

    heading: str | None = StringProperty(allownone=True, default=None)
    sub_heading: str | None = StringProperty(allownone=True, default=None)
    page_index: int = NumericProperty()
    has_heading: bool = AliasProperty(
        getter=get_has_heading,
        bind=('heading', 'sub_heading', 'page_index'),
    )

    @property
    def head_size(self: MenuPageWidget) -> int:
        """Return the size of the header."""
        return HEADER_SIZE if self.has_heading else 0

    @property
    def _count(self: MenuPageWidget) -> int:
        return super()._count - self.head_size

    def __init__(
        self: MenuPageWidget,
        items: Sequence[Item | None] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Initialize `MenuPageWidget`.

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
        self.bind(heading=self.adjust_item_widgets)
        self.bind(sub_heading=self.adjust_item_widgets)
        self.bind(page_index=self.adjust_item_widgets)
        self.bind(items=self.render)

    def adjust_item_widgets(self: MenuPageWidget, *args: object) -> None:
        """Initialize the widget."""
        _ = args
        offset = self._offset if self.has_heading else 0
        for _ in range(len(self.item_widgets), self._count - offset):
            self.item_widgets.append(ItemWidget(size_hint=(1, None)))
            self.ids.layout.add_widget(self.item_widgets[-1])
        for _ in range(self._count - offset, len(self.item_widgets)):
            self.ids.layout.remove_widget(self.item_widgets[-1])
            del self.item_widgets[-1]
        self.render()

    def render(self: MenuPageWidget, *_: object) -> None:
        """Render the item widgets."""
        if not self.item_widgets:
            return
        if self.has_heading:
            for i in range(self._offset, self._count):
                self.item_widgets[i - self._offset].item = (
                    self.items[i] if i < len(self.items) else None
                )
        else:
            for i in range(self._count):
                self.item_widgets[i].item = (
                    self.items[i] if i < len(self.items) else None
                )

    def get_item(self: MenuPageWidget, index: int) -> Item | None:
        """Get the item at the given index."""
        if index < self.head_size:
            warnings.warn(
                f'index must be greater than or equal to {self.head_size}',
                ResourceWarning,
                stacklevel=1,
            )
            return None
        try:
            return self.items[index + self._offset - self.head_size]
        except IndexError:
            return None


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('menu_page_widget.kv').resolve().as_posix(),
)
