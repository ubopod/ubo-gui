from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Callable

from kivy.core.window import ListProperty
from kivy.uix.screenmanager import Screen

if TYPE_CHECKING:
    from menu.types import Item
    from typing_extensions import Any


PAGE_MAX_ITEMS = 3


class PageWidget(Screen):
    """renders a page."""

    __events__ = ('on_close',)

    items = ListProperty([])
    title: str
    go_up: Callable
    go_down: Callable

    def __init__(
        self: PageWidget,
        items: list[Item] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Initialize a `PageWidget`.

        Parameters
        ----------
        items: `list` of `Item`
            The items to be shown in this page

        kwargs: Any
            Stuff that will get directly passed to the `__init__` method of Kivy's
        `Screen`.
        """
        if items and len(items) > PAGE_MAX_ITEMS:
            msg = f'`PageWidget` is initialized with more than `MAX_ITEMS`={PAGE_MAX_ITEMS} items'
            raise ValueError(msg)
        self.items = items or []
        super().__init__(**kwargs)

    def get_item(self: PageWidget, index: int) -> Item | None:
        if not 0 <= index < len(self.items):
            msg = f"""index must be greater than or equal to 0 and less than {
            len(self.items)}"""
            warnings.warn(msg, ResourceWarning, stacklevel=1)
            return None
        return self.items[index]

    def on_close(self: PageWidget) -> None:
        pass
