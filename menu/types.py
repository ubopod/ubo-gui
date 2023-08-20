from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Union

from typing_extensions import NotRequired, TypedDict, TypeGuard

if TYPE_CHECKING:
    from collections.abc import Callable


class Menu(TypedDict):
    """A class used to represent a menu.

    Attributes
    ----------
    title: `str`
        Rendered on top of the menu in all pages.

    heading: `str`
        Rendered in the first page of the menu, stating the purpose of the menu and its
    items.

    sub_heading: `str`
        Rendered beneath the heading in the first page of the menu with a smaller font.

    items: `list` of `Item`
        List of the items of the menu
    """

    title: str
    heading: str
    sub_heading: str
    items: list[Item]


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
