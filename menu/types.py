from __future__ import annotations

from typing import Callable, Literal, Union

from typing_extensions import NotRequired, TypedDict, TypeGuard


class BaseMenu(TypedDict):
    """A class used to represent a menu.

    Attributes
    ----------
    items: `list` of `Item`
        List of the items of the menu
    """

    items: list[Item] | Callable[[], list[Item]]


def menu_items(menu: Menu) -> list[Item]:
    """Return items of the menu.

    in case it's a function, the return value of the function is called.
    """
    return menu['items']() if\
        callable(menu['items']) else\
        menu['items']


class HeadedMenu(BaseMenu):
    """A class used to represent a headed menu.

    Attributes
    ----------
    title: `str`
        Rendered on top of the menu in all pages.

    heading: `str`
        Rendered in the first page of the menu, stating the purpose of the menu and its
    items.

    sub_heading: `str`
        Rendered beneath the heading in the first page of the menu with a smaller font.
    """

    title: str
    heading: str
    sub_heading: str


def is_headed_menu(menu: Menu) -> TypeGuard[ActionItem]:
    """Check whether the menu is a `HeadedMenu` or not."""
    return 'title' in menu and 'heading' in menu and 'sub_heading' in menu


class HeadlessMenu(BaseMenu):
    """A class used to represent a headless menu."""


def is_headless_menu(menu: Menu) -> TypeGuard[ActionItem]:
    """Check whether the menu is a `HeadedMenu` or not."""
    return 'title' not in menu and 'heading' not in menu and 'sub_heading' not in menu


Menu = Union[HeadedMenu, HeadlessMenu]


def menu_items(menu: Menu) -> list[Item]:
    """Return items of the menu.

    in case it's a function, the return value of the function is called.
    """
    return menu['items']() if\
        callable(menu['items']) else\
        menu['items']


class BaseItem(TypedDict):
    """A class used to represent a menu item.

    Attributes
    ----------
    label: `str`
        The label of the item.

    color: `tuple` of `float`
        The color in rgba format as a list of floats, the list should contain 4
    elements: red, green, blue and alpha, each being a number in the range [0..1].
    For example (0.5, 0, 0.5, 0.8) represents a semi transparent purple.
    """

    label: str
    color: NotRequired[tuple[float, float, float, float]]
    background_color: NotRequired[tuple[float, float, float, float]]
    icon: NotRequired[str]
    icon_path: NotRequired[str]
    icon_fit_mode: NotRequired[Literal[
        'scale-down', 'fill', 'contain', 'cover']]


class ActionItem(BaseItem):
    """A class used to represent an action menu item.

    Attributes
    ----------
    action: `Function`, optional
        If provided, activating this item will call this function.
    """

    action: Callable


def is_action_item(item: Item) -> TypeGuard[ActionItem]:
    """Check whether the item is an `ActionItem` or not."""
    return 'action' in item


class SubMenuItem(BaseItem):
    """A class used to represent a sub-menu menu item.

    Attributes
    ----------
    sub_menu: `Menu`, optional
        If provided, activating this item will open another menu, the description
        described in this field.
    """

    sub_menu: Menu


def is_sub_menu_item(item: Item) -> TypeGuard[SubMenuItem]:
    """Check whether the item is an `SubMenuItem` or not."""
    return 'sub_menu' in item


Item = Union[ActionItem, SubMenuItem]
