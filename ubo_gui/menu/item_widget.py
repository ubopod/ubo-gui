"""Implement `ItemWidget`."""
from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

from kivy.app import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import (
    BooleanProperty,
    ColorProperty,
    ObjectProperty,
    StringProperty,
)

from ubo_gui.constants import PRIMARY_COLOR
from ubo_gui.menu.types import process_value

if TYPE_CHECKING:
    from kivy.graphics import Color

    from . import Item


class ItemWidget(BoxLayout):
    """Renders an `Item`.

    Attributes
    ----------
    color: `tuple` of `int`
        Color of the item, used for its text and icon.

    background_color: `tuple` of `int`
        Background color of the item.

    label:
        The text rendered in the item.

    icon: `str`
        Name of a Material Symbols icon.
    """

    is_set: bool = BooleanProperty(defaultvalue=False)
    label: str = StringProperty()
    color: Color = ColorProperty((1, 1, 1, 1))
    background_color: Color = ColorProperty(PRIMARY_COLOR)
    icon: str = StringProperty(defaultvalue='')
    is_short: bool = BooleanProperty(defaultvalue=False)
    item: Item = ObjectProperty()

    def on_item(self: ItemWidget, instance: ItemWidget, value: Item | None) -> None:
        """Update the widget properties when the item changes."""
        if value is not None:
            instance.is_set = True
            instance.label = process_value(value.label) or ''
            is_short = process_value(value.is_short)
            instance.is_short = False if is_short is None else is_short
            instance.color = process_value(value.color) or ItemWidget.color.defaultvalue
            instance.background_color = (
                process_value(value.background_color)
                or ItemWidget.background_color.defaultvalue
            )
            instance.icon = process_value(value.icon) or ''
        else:
            instance.is_set = False


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('item_widget.kv').resolve().as_posix(),
)
