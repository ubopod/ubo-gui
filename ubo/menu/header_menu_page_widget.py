from __future__ import annotations

import pathlib
import warnings
from typing import TYPE_CHECKING, Any

from kivy.app import Builder, StringProperty

from ubo.page import PageWidget

from .constants import PAGE_SIZE

if TYPE_CHECKING:
    from .types import Item


class HeaderMenuPageWidget(PageWidget):
    """renders a header page of a `Menu`."""

    heading = StringProperty()
    sub_heading = StringProperty()

    def __init__(
        self: HeaderMenuPageWidget,
        item: Item,
        heading: str,
        sub_heading: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Initialize a `HeaderMenuPageWidget`.

        Parameters
        ----------
        item: `Item`
            The item to be shown in this page

        heading: `str`
            The heading of the page

        sub_heading: `str`
            The sub-heading of the page

        kwargs: Any
            Stuff that will get directly passed to the `__init__` method of Kivy's
        `Screen`.
        """
        super().__init__([item], **kwargs)
        self.heading = heading
        self.sub_heading = sub_heading

    def get_item(self: HeaderMenuPageWidget, index: int) -> Item | None:
        if index != PAGE_SIZE - 1:
            warnings.warn('index must be 2', ResourceWarning, stacklevel=1)
            return None
        return self.items[index - 2]


Builder.load_file(pathlib.Path(
    __file__).parent.joinpath('header_menu_page_widget.kv').resolve().as_posix())
