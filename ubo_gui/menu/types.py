"""Class definition of main datatypes use in menus."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from immutable import Immutable

from ubo_gui.constants import PRIMARY_COLOR

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from kivy.graphics.context_instructions import Color

    from ubo_gui.page import PageWidget


class BaseMenu(Immutable):
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
    items: Sequence[Item] | Callable[[], Sequence[Item]]
    placeholder: str | None | Callable[[], str | None] = None


class HeadedMenu(BaseMenu):
    """A class used to represent a headed menu.

    Attributes
    ----------
    heading: `str`
        Rendered in the first page of the menu, stating the purpose of the menu and its
    items. Optionally it can be a callable returning the heading.

    sub_heading: `str`
        Rendered beneath the heading in the first page of the menu with a smaller font.
    Optionally it can be a callable returning the sub heading.

    """

    heading: str | Callable[[], str]
    sub_heading: str | Callable[[], str]


class HeadlessMenu(BaseMenu):
    """A class used to represent a headless menu."""


Menu: TypeAlias = HeadedMenu | HeadlessMenu


def menu_items(menu: Menu | None) -> Sequence[Item]:
    """Return items of the menu.

    in case it's a function, the return value of the function is called.
    """
    if not menu:
        return []
    return menu.items() if callable(menu.items) else menu.items


class Item(Immutable):
    """A class used to represent a menu item.

    Attributes
    ----------
    label: `str`
        The label of the item. Optionally it can be a callable returning the label.

    color: `str` or `tuple` of `float`
        The color by its name or in rgba format as a list of floats, the list should
    contain 4 elements: red, green, blue and alpha, each being a number in the range
    [0..1].
        For example (0.5, 0, 0.5, 0.8) represents a semi transparent purple, or the
    string 'yellow' represents color yellow.
        Optionally it can be a callable returning the color.

    background_color: `str` or `tuple` of `float`
        The background color by color name or in rgba format as a list of floats, the
    list should contain 4 elements red, green, blue and alpha, each being a number in
    the range [0..1].
        For example (0.5, 0, 0.5, 0.8) represents a semi transparent purple, or the
    string 'yellow' represents color yellow.
        Optionally it can be a callable returning the background color.

    icon: `str`
        Name of a Material Symbols icon, check here for the complete list:
    https://fonts.google.com/icons
        Optionally it can be a callable returning the icon.

    is_short: `bool`
        Whether the item should be rendered in short form or not. In short form only the
    icon of the item is rendered and its label is hidden.
        Optionally it can be a callable returning the is_short value.

    opacity: `float`
        Between 0 and 1, sets the transparency channel of the item.

    """

    key: str | None = None
    label: str | Callable[[], str] = ''
    color: Color | Callable[[], Color] = (1, 1, 1, 1)
    background_color: Color | Callable[[], Color] = PRIMARY_COLOR
    icon: str | None | Callable[[], str | None] = None
    is_short: bool | Callable[[], bool] = False
    opacity: float | None = None
    progress: float | None = None


class ActionItem(Item):
    """A class used to represent an action menu item.

    Attributes
    ----------
    action: `Function`
        If provided, activating this item will call this function.

    """

    action: Callable[
        [],
        Menu | Callable[[], Menu] | type[PageWidget] | PageWidget | None,
    ]


class ApplicationItem(Item):
    """A class used to represent an application menu item.

    Attributes
    ----------
    application: `PageWidget`
        If provided, activating this item will show this widget. Optionally it can be a
    callable returning the widget.

    """

    application: (
        PageWidget
        | type[PageWidget]
        | Callable[[], PageWidget]
        | Callable[[], type[PageWidget]]
    )


class SubMenuItem(Item):
    """A class used to represent a sub-menu menu item.

    Attributes
    ----------
    sub_menu: `Menu`
        If provided, activating this item will open another menu, the description
        described in this field. Optionally it can be a callable returning the menu.

    """

    sub_menu: Menu | Callable[[], Menu]
