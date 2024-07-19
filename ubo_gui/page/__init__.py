"""Module containing the `PageWidget` class."""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Self, Sequence

from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.screenmanager import Screen

if TYPE_CHECKING:
    from ubo_gui.menu.types import Item


PAGE_MAX_ITEMS = 3


class PageWidget(Screen):
    """A `Screen` that represents a page in the menu."""

    __events__ = ('on_close',)

    items: Sequence[Item | None] = ListProperty([])
    title: str | None = StringProperty(allownone=True, defaultvalue=None)
    count: int = NumericProperty(defaultvalue=PAGE_MAX_ITEMS)
    placeholder: str | None = StringProperty(allownone=True)
    render_surroundings: bool = BooleanProperty(
        defaultvalue=False,
        cache=True,
    )
    padding_top: int = NumericProperty(defaultvalue=0)
    padding_bottom: int = NumericProperty(defaultvalue=0)

    def get_is_empty(self: PageWidget) -> bool:
        """Check if there is no item in items or all of them are `None`."""
        return all(i is None for i in self.items)

    is_empty: bool = AliasProperty(getter=get_is_empty, bind=('items',))

    @property
    def _count(self: PageWidget) -> int:
        return self.count + (2 if self.render_surroundings else 0)

    @property
    def _offset(self: PageWidget) -> int:
        return 1 if self.render_surroundings else 0

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
        if items and len(items) > self._count:
            msg = f"""`PageWidget` is initialized with more than `count`={
            self.count} items"""
            raise ValueError(msg)

    def get_item(self: PageWidget, index: int) -> Item | None:
        """Get the page item at the given index."""
        index += self._offset
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
