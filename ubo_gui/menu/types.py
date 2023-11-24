from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Union

from typing_extensions import NotRequired, TypedDict, TypeGuard

if TYPE_CHECKING:
    from page import PageWidget


class BaseMenu(TypedDict):
    """A class used to represent a menu.

    Attributes
    ----------
    title: `str`
        Rendered on top of the menu in all pages. Optionally it can be a callable
    returning the title.

    items: `list` of `Item`
        List of the items of the menu. Optionally it can be a callable returning the
    list of items
    """

    title: str | Callable[[], str]
    items: list[Item] | Callable[[], list[Item]]


class HeadedMenu(BaseMenu):
    """A class used to represent a headed menu.

    Attributes
    ----------
    heading: `str`
        Rendered in the first page of the menu, stating the purpose of the menu and its
    items.

    sub_heading: `str`
        Rendered beneath the heading in the first page of the menu with a smaller font.
    """

    heading: str
    sub_heading: str


def is_headed_menu(menu: Menu) -> TypeGuard[ActionItem]:
    """Check whether the menu is a `HeadedMenu` or not."""
    return 'heading' in menu and 'sub_heading' in menu


class HeadlessMenu(BaseMenu):
    """A class used to represent a headless menu."""


def is_headless_menu(menu: Menu) -> TypeGuard[ActionItem]:
    """Check whether the menu is a `HeadedMenu` or not."""
    return 'heading' not in menu and 'sub_heading' not in menu


Menu = Union[HeadedMenu, HeadlessMenu]


def menu_items(menu: Menu | None) -> list[Item]:
    """Return items of the menu.

    in case it's a function, the return value of the function is called.
    """
    if not menu:
        return []
    return menu['items']() if callable(menu['items']) else menu['items']


def menu_title(menu: Menu) -> str:
    """Return items of the menu.

    in case it's a function, the return value of the function is called.
    """
    return menu['title']() if callable(menu['title']) else menu['title']


class BaseItem(TypedDict):
    """A class used to represent a menu item.

    Attributes
    ----------
    label: `str`
        The label of the item.

    color: `str` or `tuple` of `float`
        The color by its name or in rgba format as a list of floats, the list should
    contain 4 elements: red, green, blue and alpha, each being a number in the range
    [0..1].
        For example (0.5, 0, 0.5, 0.8) represents a semi transparent purple, or the
    string 'yellow' represents color yellow.

    background_color: `str` or `tuple` of `float`
        The background color by color name or in rgba format as a list of floats, the
    list should contain 4 elements red, green, blue and alpha, each being a number in
    the range [0..1].
        For example (0.5, 0, 0.5, 0.8) represents a semi transparent purple, or the
    string 'yellow' represents color yellow.

    icon: `str`
        Name of a Material Symbols icon, check here for the complete list:
    https://fonts.google.com/icons

    is_short: `bool`
        Whether the item should be rendered in short form or not. In short form only the
    icon of the item is rendered and its label is hidden.
    """

    label: str
    color: NotRequired[str | tuple[float, float, float, float]]
    background_color: NotRequired[str | tuple[float, float, float, float]]
    icon: NotRequired[str]
    is_short: NotRequired[bool]


class ActionItem(BaseItem):
    """A class used to represent an action menu item.

    Attributes
    ----------
    action: `Function`
        If provided, activating this item will call this function.
    """

    action: Callable


def is_action_item(item: Item) -> TypeGuard[ActionItem]:
    """Check whether the item is an `ActionItem` or not."""
    return 'action' in item


class ApplicationItem(BaseItem):
    """A class used to represent an application menu item.

    Attributes
    ----------
    application: `PageWidget`
        If provided, activating this item will show this widget
    """

    application: type[PageWidget]


def is_application_item(item: Item) -> TypeGuard[ApplicationItem]:
    """Check whether the item is an `ApplicationItem` or not."""
    return 'application' in item


class SubMenuItem(BaseItem):
    """A class used to represent a sub-menu menu item.

    Attributes
    ----------
    sub_menu: `Menu`
        If provided, activating this item will open another menu, the description
        described in this field.
    """

    sub_menu: Menu


def is_sub_menu_item(item: Item) -> TypeGuard[SubMenuItem]:
    """Check whether the item is an `SubMenuItem` or not."""
    return 'sub_menu' in item


Item = Union[ActionItem, SubMenuItem, ApplicationItem]
