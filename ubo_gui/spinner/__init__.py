"""Spinner widget for loading indication."""

from __future__ import annotations

import pathlib
from typing import Any, cast

from headless_kivy import HeadlessWidget
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.properties import NumericProperty
from kivy.uix.label import Label


class SpinnerWidget(HeadlessWidget, Label):
    """Spinner widget for loading indication."""

    angle = NumericProperty(0)

    def __init__(self: SpinnerWidget, **kwargs: object) -> None:
        """Initialize the SpinnerWidget class."""
        super().__init__(**cast(Any, kwargs))
        self.interval = Clock.schedule_interval(self.rotate_spinner, 1 / 60)

    def __del__(self: SpinnerWidget) -> None:
        """Cancel the interval when the widget is deleted."""
        self.interval.cancel()

    def rotate_spinner(self: SpinnerWidget, dt: float) -> None:
        """Rotate the spinner."""
        self.angle -= dt * 500
        self.angle %= 360


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('spinner_widget.kv').resolve().as_posix(),
)
