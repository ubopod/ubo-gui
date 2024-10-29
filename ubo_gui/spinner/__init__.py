"""Spinner widget for loading indication."""

from __future__ import annotations

import pathlib

from kivy.animation import Animation
from kivy.lang.builder import Builder
from kivy.properties import NumericProperty
from kivy.uix.label import Label


class SpinnerWidget(Label):
    """Spinner widget for loading indication."""

    angle = NumericProperty(0)

    def on_kv_post(self: SpinnerWidget, base_widget: SpinnerWidget) -> None:
        """Start the spinner animation."""
        _ = base_widget
        rotation = Animation(angle=-360 * 100, duration=0.5 * 100) + Animation(
            angle=0,
            duration=0,
        )
        rotation.repeat = True
        rotation.start(self)


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('spinner_widget.kv').resolve().as_posix(),
)
