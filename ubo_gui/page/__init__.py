"""Module containing the `PageWidget` class."""
from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Self, Sequence

from kivy.properties import ListProperty, StringProperty
from kivy.uix.screenmanager import Screen

if TYPE_CHECKING:
    from menu.types import Item


PAGE_MAX_ITEMS = 3


class PageWidget(Screen):
    """A `Screen` that represents a page in the menu."""

    __events__ = ('on_close',)

    items: Sequence[Item] = ListProperty([])
    title: str | None = StringProperty(allownone=True, defaultvalue=None)

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
        items: Sequence[Item] | None = None,
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
        if items and len(items) > PAGE_MAX_ITEMS:
            msg = f"""`PageWidget` is initialized with more than `MAX_ITEMS`={
            PAGE_MAX_ITEMS} items"""
            raise ValueError(msg)
        self.items = items or []
        super().__init__(*args, **kwargs)

    def get_item(self: PageWidget, index: int) -> Item | None:
        """Get the page item at the given index."""
        if not 0 <= index < len(self.items):
            msg = f"""index must be greater than or equal to 0 and less than {
            len(self.items)}"""
            warnings.warn(msg, ResourceWarning, stacklevel=1)
            return None
        return self.items[index]

    def on_close(self: PageWidget) -> None:
        """Signal when the page is closed."""

    def on_leave(self: PageWidget, *args: object) -> None:
        """Override `on_leave` to dispatch `on_close` event."""
        self.dispatch('on_close')
        return super().on_leave(*args)
