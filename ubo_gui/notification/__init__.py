from __future__ import annotations

import pathlib
import warnings
from typing import (
    TYPE_CHECKING,
    Callable,
)

from kivy.app import Builder
from kivy.metrics import dp
from kivy.properties import ColorProperty, ObjectProperty, StringProperty

from ubo_gui.constants import DANGER_COLOR
from ubo_gui.menu.types import ActionItem
from ubo_gui.page import PAGE_MAX_ITEMS, PageWidget

if TYPE_CHECKING:
    from ubo_gui.menu.types import Item


class NotificationAction:
    title: str
    callback: Callable

    def __init__(self: NotificationAction, *, title: str, callback: Callable) -> None:
        self.title = title
        self.callback = callback

    def __repr__(self: NotificationAction) -> str:
        """Return a string representation of this object."""
        return f'<NotificationAction(title={self.title}, callback={self.callback})>'


class NotificationWidget(PageWidget):
    """renders a notification."""

    __events__ = ('on_dismiss',)

    notification = ObjectProperty()
    notification_title: str = StringProperty()
    content: str = StringProperty()
    icon: str = StringProperty()
    color = ColorProperty()

    def __init__(
        self: NotificationWidget,
        *args: object,
        **kwargs: object,
    ) -> None:
        super().__init__(
            *args,
            items=[
                ActionItem(
                    icon='delete',
                    action=lambda: self.dispatch('on_dismiss') and None,
                    label='',
                    is_short=True,
                    background_color=DANGER_COLOR,
                ),
            ],
            **kwargs,
        )

    def go_down(self: NotificationWidget) -> None:
        """Scroll down the notification list."""
        self.ids.slider.animated_value -= dp(50)

    def go_up(self: NotificationWidget) -> None:
        """Scroll up the notification list."""
        self.ids.slider.animated_value += dp(50)

    def get_item(self: NotificationWidget, index: int) -> Item | None:
        """Get the page item at the given index."""
        if index != PAGE_MAX_ITEMS - 1:
            warnings.warn('index must be 2', ResourceWarning, stacklevel=1)
            return None
        return self.items[index - 2]

    def on_dismiss(self: PageWidget) -> None:
        """Signal when the notification is dismissed."""
        ...


Builder.load_file(
    pathlib.Path(__file__)
    .parent.joinpath('notification_widget.kv')
    .resolve()
    .as_posix(),
)
