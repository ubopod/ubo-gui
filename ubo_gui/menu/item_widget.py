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

if TYPE_CHECKING:
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

    is_set = BooleanProperty(defaultvalue=False)
    label = StringProperty()
    color = ColorProperty((1, 1, 1, 1))
    background_color = ColorProperty(PRIMARY_COLOR)
    icon = StringProperty(defaultvalue='')
    is_short = BooleanProperty(defaultvalue=False)
    item = ObjectProperty()

    def on_item(self: ItemWidget, instance: ItemWidget, value: Item | None) -> None:
        if value is not None:
            instance.is_set = True
            instance.label = value.label or ''
            instance.is_short = False if value.is_short is None else value.is_short
            instance.color = value.color or ItemWidget.color.defaultvalue
            instance.background_color = (
                value.background_color or ItemWidget.background_color.defaultvalue
            )
            instance.icon = value.icon or ''
        else:
            instance.is_set = False


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('item_widget.kv').resolve().as_posix(),
)
