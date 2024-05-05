"""Notification widget."""

from __future__ import annotations

import pathlib

from kivy.lang.builder import Builder
from kivy.metrics import dp
from kivy.properties import ColorProperty, StringProperty

from ubo_gui.page import PageWidget


class NotificationWidget(PageWidget):
    """renders a notification."""

    notification_title: str = StringProperty()
    content: str = StringProperty()
    icon: str = StringProperty()
    color = ColorProperty()

    def go_down(self: NotificationWidget) -> None:
        """Scroll down the notification list."""
        self.ids.slider.animated_value -= dp(50)

    def go_up(self: NotificationWidget) -> None:
        """Scroll up the notification list."""
        self.ids.slider.animated_value += dp(50)


Builder.load_file(
    pathlib.Path(__file__)
    .parent.joinpath('notification_widget.kv')
    .resolve()
    .as_posix(),
)
