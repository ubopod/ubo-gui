from __future__ import annotations

import pathlib
import uuid
import warnings
from datetime import datetime, timezone
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable, Mapping

from kivy.app import Builder
from kivy.event import EventDispatcher
from kivy.metrics import dp
from kivy.properties import ColorProperty, ObjectProperty, StringProperty

from ubo_gui.menu.types import ActionItem, ApplicationItem
from ubo_gui.page import PAGE_MAX_ITEMS, PageWidget

if TYPE_CHECKING:
    from typing_extensions import Any

    from ubo_gui.menu.types import Item


class Importance(Enum):
    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


IMPORTANCE_ICONS = {
    Importance.CRITICAL: 'dangerous',
    Importance.HIGH: 'warning',
    Importance.MEDIUM: 'info',
    Importance.LOW: 'priority',
}

IMPORTANCE_COLORS = {
    Importance.CRITICAL: '#D32F2F',
    Importance.HIGH: '#FFA000',
    Importance.MEDIUM: '#FFEB3B',
    Importance.LOW: '#2196F3',
}


class NotificationAction:
    title: str
    callback: Callable

    def __init__(self: NotificationAction, *, title: str, callback: Callable) -> None:
        self.title = title
        self.callback = callback

    def __repr__(self: NotificationAction) -> str:
        """Return a string representation of this object."""
        return f'<NotificationAction(title={self.title}, callback={self.callback})>'


class Notification:
    title: str
    content: str
    importance: Importance
    timestamp: datetime
    is_read: bool
    sender: str | None
    actions: list[NotificationAction]
    icon: str
    expiry_date: datetime | None

    def __init__(
        self: Notification,
        *,
        title: str,
        content: str,
        importance: Importance = Importance.LOW,
        sender: str | None = None,
        actions: list[NotificationAction] | None = None,
        icon: str | None = None,
        expiry_date: datetime | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        if actions is None:
            actions = []
        if timestamp is None:
            timestamp = datetime.now(tz=timezone.utc)
        if icon is None:
            icon = IMPORTANCE_ICONS[importance]

        self.id = str(uuid.uuid4())
        self.title = title
        self.content = content
        self.importance = importance
        self.timestamp = timestamp
        self.is_read = False
        self.sender = sender
        self.actions = actions
        self.icon = icon
        self.expiry_date = expiry_date

    def mark_read(self: Notification) -> None:
        """Mark this notification as read."""
        self.is_read = True

    def mark_unread(self: Notification) -> None:
        """Mark this notification as unread."""
        self.is_read = False

    def is_expired(self: Notification) -> bool:
        """Return whether this notification is expired."""
        return (
            self.expiry_date is not None
            and datetime.now(tz=timezone.utc) > self.expiry_date
        )

    def __repr__(self: Notification) -> str:
        """Return a string representation of this object."""
        return (
            f'<Notification(id={self.id}, title={self.title}, '
            f'content={self.content}, importance={self.importance.name}, '
            f'timestamp={self.timestamp}, is_read={self.is_read}, '
            f'sender={self.sender}, actions={self.actions}, icon={self.icon}, '
            f'expiry_date={self.expiry_date})>'
        )


class NotificationManager(EventDispatcher):
    __events__ = ('on_change',)

    _notifications: list[Notification]

    def __init__(
        self: NotificationManager,
        *args: list[Any],
        **kwargs: dict[str, Any],
    ) -> None:
        self._notifications = []
        super().__init__(*args, **kwargs)

    def notify(
        self: NotificationManager,
        *,
        title: str,
        content: str,
        importance: Importance = Importance.LOW,
        sender: str | None = None,
        actions: list[NotificationAction] | None = None,
        icon: str | None = None,
        expiry_date: datetime | None = None,
    ) -> None:
        """Add a notification to the notification manager."""
        self._notifications.append(
            Notification(
                title=title,
                content=content,
                importance=importance,
                sender=sender,
                actions=actions,
                icon=icon,
                expiry_date=expiry_date,
            ),
        )
        self.dispatch('on_change')

    @property
    def unread_count(self: NotificationManager):
        """Return the number of unread notifications."""
        return len(
            [
                notification
                for notification in self._notifications
                if not notification.is_read
            ],
        )

    def remove(self: NotificationManager, notification: Notification):
        """Remove a notification from the notification manager."""
        self._notifications.remove(notification)
        self.dispatch('on_change')

    def menu_items(self: NotificationManager) -> list[Item]:
        """Return a list of menu items for the notification manager."""
        manager = self

        def notification_widget_builder(
            notification: Notification,
            index: int,
        ) -> type[PageWidget]:
            """Return a notification widget for the given notification."""
            class NotificationWrapper(NotificationWidget):
                def __init__(self, **kwargs) -> None:
                    super().__init__(
                        notification=notification,
                        title=f'Notification ({index+1}/'
                        f'{len(manager._notifications)})',
                        **kwargs,
                    )

            return NotificationWrapper

        return [
            ApplicationItem(
                label=notification.title,
                icon=notification.icon,
                color='black',
                background_color=IMPORTANCE_COLORS[notification.importance],
                application=notification_widget_builder(notification, index),
            )
            for index, notification in enumerate(self._notifications)
        ]

    def on_change(self: NotificationManager) -> None:
        pass


notification_manager = NotificationManager()


class NotificationWidget(PageWidget):
    """renders a notification."""

    notification = ObjectProperty()
    color = ColorProperty()
    title = StringProperty()

    def __init__(
        self: NotificationWidget,
        *,
        notification: Notification,
        title: str,
        **kwargs: Mapping[str, Any],
    ) -> None:
        self.notification = notification
        self.color = IMPORTANCE_COLORS[notification.importance]
        self.title = title

        def close() -> None:
            notification_manager.remove(notification)
            notification_manager.dispatch('on_close')

        super().__init__(
            items=[
                {
                    'icon': 'delete',
                    'action': close,
                    'label': '',
                    'is_short': True,
                },
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


Builder.load_file(
    pathlib.Path(__file__)
    .parent.joinpath('notification_widget.kv')
    .resolve()
    .as_posix(),
)
