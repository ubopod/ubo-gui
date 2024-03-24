"""A half circle gauge widget."""

from __future__ import annotations

import pathlib

from kivy.lang.builder import Builder
from kivy.properties import ColorProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout


class GaugeWidget(BoxLayout):
    """A widget that displays a gauge."""

    value = NumericProperty(50)
    min_value = NumericProperty(0)
    max_value = NumericProperty(100)
    fill_color = ColorProperty('red')
    background_color = ColorProperty('#D9D9D9')
    label = StringProperty('')

    _size = ListProperty([0, 0])
    _pos = ListProperty([0, 0])


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('gauge_widget.kv').resolve().as_posix(),
)
