"""Spinner widget for loading indication."""

from __future__ import annotations

import pathlib
import re

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
        self.rotation_animation = Animation(
            angle=-360 * 100,
            duration=0.5 * 100,
        ) + Animation(
            angle=0,
            duration=0,
        )
        self.rotation_animation.repeat = True
        self.bind(text=self.handle_text_change)
        self.handle_text_change(self, self.text)

    def handle_text_change(self: SpinnerWidget, _: SpinnerWidget, text: str) -> None:
        """Decide whether to show the spinner or not."""
        text = re.sub(r'\[(?P<tag>\w+)=.*?\](?P<text>.*?)\[/\1\]', r'\g<text>', text)
        if text == '':
            self.rotation_animation.start(self)
        else:
            self.rotation_animation.cancel(self)


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('spinner_widget.kv').resolve().as_posix(),
)
