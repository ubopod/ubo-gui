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
from ubo_gui.menu.constants import SHORT_WIDTH

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

    is_set = BooleanProperty(False)
    label = StringProperty()
    color = ColorProperty((1, 1, 1, 1))
    background_color = ColorProperty(PRIMARY_COLOR)
    icon = StringProperty()
    is_short = BooleanProperty(False)
    item = ObjectProperty()

    def on_item(self: ItemWidget, instance: ItemWidget, value: Item | None) -> None:
        if value is not None:
            instance.is_set = True
            instance.label = value['label']
            if 'is_short' in value:
                instance.is_short = value['is_short']
            if 'color' in value:
                instance.color = value['color']
            if 'background_color' in value:
                instance.background_color = value['background_color']
            if 'icon' in value:
                instance.icon = value['icon']
        else:
            instance.is_set = False


Builder.load_string(
    f"""
#:set SHORT_WIDTH {SHORT_WIDTH}
""",
)

Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('item_widget.kv').resolve().as_posix(),
)
