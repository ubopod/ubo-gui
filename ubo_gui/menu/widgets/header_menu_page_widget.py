"""Module for the `HeaderMenuPageWidget` class."""

from __future__ import annotations

import pathlib
import warnings
from typing import TYPE_CHECKING, Any, Sequence

from kivy.lang.builder import Builder
from kivy.properties import StringProperty

from ubo_gui.menu.constants import PAGE_SIZE
from ubo_gui.menu.widgets.item_widget import ItemWidget
from ubo_gui.page import PageWidget

if TYPE_CHECKING:
    from ubo_gui.menu.types import Item


class HeaderMenuPageWidget(PageWidget):
    """Renders a header page of a `Menu`."""

    heading = StringProperty()
    sub_heading = StringProperty()

    def __init__(
        self: HeaderMenuPageWidget,
        items: Sequence[Item | None],
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
        self.bind(on_kv_post=self.render)
        super().__init__(items, **kwargs)
        if len(items) > self.count - 2:
            msg = (
                '`HeaderMenuPageWidget` is initialized with more than '
                f'`{self.count - 2}` items'
            )
            raise ValueError(msg)
        self.bind(items=self.render)

    def render(self: HeaderMenuPageWidget, *_: object) -> None:
        """Render the widget."""
        self.ids.layout.clear_widgets()
        for i in range(self.count - 2):
            self.ids.layout.add_widget(
                ItemWidget(
                    item=self.items[i] if i < len(self.items) else None,
                    size_hint=(1, None),
                ),
            )

    def get_item(self: HeaderMenuPageWidget, index: int) -> Item | None:
        """Get the item at the given index."""
        if index != PAGE_SIZE - 1:
            warnings.warn(
                f'index must be {PAGE_SIZE - 1}',
                ResourceWarning,
                stacklevel=1,
            )
            return None
        try:
            return self.items[index - PAGE_SIZE + 1]
        except IndexError:
            return None


Builder.load_file(
    pathlib.Path(__file__)
    .parent.joinpath('header_menu_page_widget.kv')
    .resolve()
    .as_posix(),
)
