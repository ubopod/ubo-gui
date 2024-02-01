"""Module for the `HeaderMenuPageWidget` class."""
from __future__ import annotations

import pathlib
import warnings
from typing import TYPE_CHECKING, Any, Sequence

from kivy.app import Builder, StringProperty

from ubo_gui.menu.constants import PAGE_SIZE
from ubo_gui.page import PageWidget

if TYPE_CHECKING:
    from ubo_gui.menu.types import Item


class HeaderMenuPageWidget(PageWidget):
    """Renders a header page of a `Menu`."""

    heading = StringProperty()
    sub_heading = StringProperty()

    def __init__(
        self: HeaderMenuPageWidget,
        items: Sequence[Item],
        heading: str = '',
        sub_heading: str = '',
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Initialize a `HeaderMenuPageWidget`.

        Parameters
        ----------
        items: `Sequence`[[`Item`]]
            The item to be shown in this page

        heading: `str`
            The heading of the page

        sub_heading: `str`
            The sub-heading of the page

        kwargs: Any
            Stuff that will get directly passed to the `__init__` method of Kivy's
        `Screen`.

        """
        if len(items) > 1:
            msg = '`HeaderMenuPageWidget` is initialized with more than one item'
            raise ValueError(msg)
        super().__init__(items, **kwargs)
        self.heading = heading
        self.sub_heading = sub_heading

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
