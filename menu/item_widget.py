"""Implement `ItemWidget`."""
from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

from kivy.app import Builder, ObjectProperty, StringProperty, Widget
from kivy.graphics import Color
from kivy.graphics.svg import Svg
from kivy.uix.label import ColorProperty
from kivy.uix.scatter import Scatter

if TYPE_CHECKING:
    from . import Item


class SvgWidget(Scatter):
    source = StringProperty()
    color = ColorProperty()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.redraw()

    def redraw(self: SvgWidget):
        if self.source:
            with self.canvas:
                Color(self.color)
                svg = Svg(self.source)
            self.scale = self.height / svg.height
            self.width = svg.width * self.scale
        else:
            self.width = 0

    def on_source(self: SvgWidget, _instance: SvgWidget, _value: str):
        self.redraw()


class ItemWidget(Widget):
    """Renders an `Item`.

    Attributes
    ----------
    color: `tuple` of `int`
        Color of the item, used for its text and icon.

    background_color: `tuple` of `int`
        Background color of the item.

    label:
        The text rendered in the item.

    icon_path: `str`
        The path of a SVG or PNG file to be rendered in place of the icon of the item.

    icon_fit_mode: `str`
        Icon's `fit_mode` as described
        https://kivy.org/doc/stable/api-kivy.uix.image.html#kivy.uix.image.Image.fit_mode
    """

    label = StringProperty()
    color = ColorProperty((1, 1, 1, 1))
    background_color = ColorProperty((1, 0, 0, 1))
    icon_path = StringProperty()
    icon_fit_mode = StringProperty('contain')
    item = ObjectProperty()

    def on_item(self: ItemWidget, instance: ItemWidget, value: Item):
        instance.label = value['label']
        if 'color' in value:
            instance.color = value['color']
        if 'background_color' in value:
            instance.background_color = value['background_color']
        if 'icon_path' in value:
            instance.icon_path = value['icon_path']
        elif 'icon' in value:
            instance.icon_path = pathlib.Path(
                'assets', 'icons', value['icon'] + '.svg').resolve().as_posix()
        if 'icon_fit_mode' in value:
            instance.icon_fit_mode = value['icon_fit_mode']


Builder.load_file(pathlib.Path(
    __file__).parent.joinpath('item_widget.kv').resolve().as_posix())
