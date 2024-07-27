"""Stack item classes for the menu stack."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Self, TypeVar, cast

if TYPE_CHECKING:
    from ubo_gui.page import PageWidget

    from .types import Menu

VISUAL_SNAPSHOT_WIDTH = 15


@dataclass(kw_only=True)
class BaseStackItem:
    """An item in a menu stack."""

    parent: StackItem | None
    subscriptions: set[Callable[[], None]] = field(default_factory=set)

    def clear_subscriptions(self: BaseStackItem) -> None:
        """Clear all subscriptions."""
        subscriptions = self.subscriptions.copy()
        self.subscriptions.clear()
        for unsubscribe in subscriptions:
            unsubscribe()

    @property
    def root(self: BaseStackItem) -> StackMenuItem:
        """Return the root item."""
        if self.parent:
            return self.parent.root
        return cast(StackMenuItem, self)

    @property
    def title(self: Self) -> str:
        """Return the title of the item."""
        raise NotImplementedError


@dataclass(kw_only=True)
class StackMenuItemSelection:
    """A selected menu item in a menu stack."""

    key: str
    item: StackMenuItem


@dataclass(kw_only=True)
class StackMenuItem(BaseStackItem):
    """A menu item in a menu stack."""

    menu: Menu
    page_index: int
    selection: StackMenuItemSelection | None = None

    @property
    def title(self: StackMenuItem) -> str:
        """Return the title of the menu."""
        return self.menu.title() if callable(self.menu.title) else self.menu.title

    @property
    def visual_snapshot(self: StackMenuItem) -> list[str]:
        """Return the snapshot of the menu."""
        T = TypeVar('T')

        def process_callable(object_: T | Callable[[], T]) -> T:
            return object_() if callable(object_) else object_

        items = process_callable(self.menu.items)
        title = process_callable(self.menu.title)[: VISUAL_SNAPSHOT_WIDTH - 2]
        padding = '─' * ((VISUAL_SNAPSHOT_WIDTH - len(title)) // 2)
        return [
            padding
            + title
            + padding
            + '─' * ((len(title) + VISUAL_SNAPSHOT_WIDTH) % 2),
            *(
                (
                    (process_callable(items[i].icon) or ' ')
                    + ' '
                    + str(process_callable(items[i].label))
                ).ljust(
                    VISUAL_SNAPSHOT_WIDTH,
                    ' ',
                )[:VISUAL_SNAPSHOT_WIDTH]
                if len(items) > i
                else ' ' * VISUAL_SNAPSHOT_WIDTH
                for i in range(3)
            ),
            '─' * VISUAL_SNAPSHOT_WIDTH,
        ]


@dataclass(kw_only=True)
class StackApplicationItem(BaseStackItem):
    """An application item in a menu stack."""

    application: PageWidget

    @property
    def title(self: StackApplicationItem) -> str:
        """Return the title of the application."""
        return self.application.name

    @property
    def visual_snapshot(self: StackApplicationItem) -> list[str]:
        """Return the snapshot of the application."""
        title = self.title[: VISUAL_SNAPSHOT_WIDTH - 2]
        padding = '─' * ((VISUAL_SNAPSHOT_WIDTH - len(title)) // 2)
        return [
            padding + title + padding + '─' * (len(title) % 2),
            ' ' * VISUAL_SNAPSHOT_WIDTH,
            f""" {(self.application.title or '-').ljust(VISUAL_SNAPSHOT_WIDTH - 2, " ")
            [:VISUAL_SNAPSHOT_WIDTH - 2]} """,
            ' ' * VISUAL_SNAPSHOT_WIDTH,
            '─' * VISUAL_SNAPSHOT_WIDTH,
        ]


StackItem = StackMenuItem | StackApplicationItem
