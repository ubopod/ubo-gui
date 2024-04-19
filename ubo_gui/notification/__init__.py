"""Notification widget."""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Callable

from immutable import Immutable
from kivy.lang.builder import Builder
from kivy.metrics import dp
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ColorProperty,
    StringProperty,
)

from ubo_gui.constants import DANGER_COLOR, INFO_COLOR
from ubo_gui.menu.types import ActionItem
from ubo_gui.page import PAGE_MAX_ITEMS, PageWidget

if TYPE_CHECKING:
    from ubo_gui.menu.types import Item


class NotificationAction(Immutable):
    """A notification action."""

    title: str
    callback: Callable


class NotificationWidget(PageWidget):
    """renders a notification."""

    __events__ = ('on_dismiss', 'on_info')

    notification_title: str = StringProperty()
    content: str = StringProperty()
    has_extra_information: bool = BooleanProperty(defaultvalue=False)
    icon: str = StringProperty()
    color = ColorProperty()

    def get_info_action(self: NotificationWidget) -> ActionItem | None:
        """Return the info action if `info` is available."""
        if not self.has_extra_information:
            return None

        def dispatch_info() -> None:
            self.dispatch('on_info')

        return ActionItem(
            icon='󰋼',
            action=dispatch_info,
            label='',
            is_short=True,
            background_color=INFO_COLOR,
        )

    info_action: ActionItem = AliasProperty(
        getter=get_info_action,
        bind=['has_extra_information'],
        cache=True,
    )

    def __init__(
        self: NotificationWidget,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Create a new `NotificationWidget` object."""

        def dispatch_dismiss() -> None:
            self.dispatch('on_dismiss')

        self.dismiss_action = ActionItem(
            icon='󰆴',
            action=dispatch_dismiss,
            label='',
            is_short=True,
            background_color=DANGER_COLOR,
        )
        super().__init__(
            *args,
            items=[],
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
        if index == PAGE_MAX_ITEMS - 2:
            return self.info_action
        if index == PAGE_MAX_ITEMS - 1:
            return self.dismiss_action
        return None

    def on_dismiss(self: PageWidget) -> None:
        """Signal when the notification is dismissed."""

    def on_info(self: PageWidget) -> None:
        """Signal when the info action is selected."""


Builder.load_file(
    pathlib.Path(__file__)
    .parent.joinpath('notification_widget.kv')
    .resolve()
    .as_posix(),
)
