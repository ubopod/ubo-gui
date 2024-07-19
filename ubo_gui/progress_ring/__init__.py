"""ProgressRing widget."""

from __future__ import annotations

import pathlib

from kivy.lang.builder import Builder
from kivy.metrics import dp
from kivy.properties import ColorProperty, NumericProperty
from kivy.uix.widget import Widget


class ProgressRingWidget(Widget):
    """renders a progress ring."""

    progress: float = NumericProperty(defaultvalue=0, min=0, max=1)
    background_band_width: int = NumericProperty(defaultvalue=dp(1))
    band_width: int = NumericProperty(defaultvalue=dp(4))
    background_color = ColorProperty()
    color = ColorProperty()

    _progress: int = NumericProperty()


Builder.load_file(
    pathlib.Path(__file__)
    .parent.joinpath('progress_ring_widget.kv')
    .resolve()
    .as_posix(),
)
