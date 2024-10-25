"""Spinner widget for loading indication."""

from __future__ import annotations

import math
from typing import Any, cast

from headless_kivy import HeadlessWidget
from kivy.clock import Clock
from kivy.graphics.context_instructions import Rotate
from kivy.properties import NumericProperty
from kivy.uix.label import Label


class SpinnerWidget(HeadlessWidget):
    """Spinner widget for loading indication."""

    angle = NumericProperty(0)

    def __init__(self: SpinnerWidget, **kwargs: object) -> None:
        """Initialize the SpinnerWidget class."""
        super().__init__(**cast(Any, kwargs))
        self.interval = Clock.schedule_interval(self.rotate_spinner, 1 / 40)
        self.label = Label(
            text='',
            color=(1, 1, 1),
        )
        self.label.bind(texture_size=self.label.setter('size'))
        self.bind(
            size=lambda *_: self.label.setter('center')(
                self.label,
                (self.width / 2, self.height / 2),
            ),
        )
        self.add_widget(self.label)

    def __del__(self: SpinnerWidget) -> None:
        """Remove the spinner widget."""
        self.interval.cancel()

    def rotate_spinner(self: SpinnerWidget, dt: float) -> None:
        """Rotate the spinner."""
        self.angle = (self.angle + dt) % math.tau
        with self.label.canvas.before:
            Rotate(
                angle=-dt * 400,
                origin=self.label.center,
            )
