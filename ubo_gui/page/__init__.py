"""Module containing the `PageWidget` class."""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Self, Sequence

from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.screenmanager import Screen

if TYPE_CHECKING:
    from menu.types import Item


PAGE_MAX_ITEMS = 3


class PageWidget(Screen):
    """A `Screen` that represents a page in the menu."""

    __events__ = ('on_close',)

    items: Sequence[Item | None] = ListProperty([])
    title: str | None = StringProperty(allownone=True, defaultvalue=None)
    count = NumericProperty(defaultvalue=PAGE_MAX_ITEMS)
    offset = NumericProperty(defaultvalue=0)
    placeholder = StringProperty(allownone=True)
    render_surroundings = BooleanProperty(
        default=False,
        cache=True,
    )
    padding_top = NumericProperty(default=0)
    padding_bottom = NumericProperty(default=0)

    def go_up(self: Self) -> None:
        """Implement this method to provide custom logic for up key."""
        return

    def go_down(self: Self) -> None:
        """Implement this method to provide custom logic for down key."""
        return

    def go_back(self: Self) -> bool | None:
        """Implement this method to provide custom logic for back key.

        Return `true` if back button is handled and the default behavior should be
        avoided
        """
        return

    def __init__(
        self: PageWidget,
        items: Sequence[Item | None] | None = None,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Initialize a `PageWidget`.

        Parameters
        ----------
        items: `list` of `Item`
            The items to be shown in this page

        args: object
            Stuff that will get directly passed to the `__init__` method of Kivy's

        kwargs: object
            Stuff that will get directly passed to the `__init__` method of Kivy's
        `Screen`.

        """
        self.items = items or []
        super().__init__(*args, **kwargs)
        if items and len(items) > self.count:
            msg = f"""`PageWidget` is initialized with more than `MAX_ITEMS`={
            self.count} items"""
            raise ValueError(msg)

    def get_item(self: PageWidget, index: int) -> Item | None:
        """Get the page item at the given index."""
        index += self.offset
        if not 0 <= index < len(self.items):
            msg = f"""index must be greater than or equal to 0 and less than {
            len(self.items)}"""
            warnings.warn(msg, ResourceWarning, stacklevel=1)
            return None
        return self.items[index]

    def on_close(self: PageWidget) -> None:
        """Signal when the page is closed."""

    def __repr__(self: PageWidget) -> str:
        """Return a string representation of the `PageWidget`."""
        return (
            f'<{self.__class__.__name__}@PageWidget name="{self.name}" '
            f'title="{self.title}">'
        )
