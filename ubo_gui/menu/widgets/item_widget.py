"""Implement `ItemWidget`."""
from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Any, Callable

from kivy.app import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import (
    BooleanProperty,
    ColorProperty,
    ObjectProperty,
    StringProperty,
)

from ubo_gui.constants import PRIMARY_COLOR
from ubo_gui.menu.types import process_subscribable_value

if TYPE_CHECKING:
    from kivy.graphics import Color

    from ubo_gui.menu.types import Item


class ItemWidget(BoxLayout):
    """Renders an `Item`.

    Attributes
    ----------
    color: `tuple` of `int`
        Color of the item, used for its text and icon.

    background_color: `tuple` of `int`
        Background color of the item.

    label:
        The text rendered in the item.

    icon: `str`
        Name of a Material Symbols icon.

    """

    _subscriptions: list[Callable[[], None]]

    is_set: bool = BooleanProperty(defaultvalue=False)
    label: str = StringProperty()
    color: Color = ColorProperty((1, 1, 1, 1))
    background_color: Color = ColorProperty(PRIMARY_COLOR)
    icon: str = StringProperty(defaultvalue='')
    is_short: bool = BooleanProperty(defaultvalue=False)
    item: Item = ObjectProperty()

    def __init__(self: ItemWidget, **kwargs: dict[str, Any]) -> None:
        """Initialize an `ItemWidget`."""
        super().__init__(**kwargs)
        self._subscriptions = []

    def __del__(self: ItemWidget) -> None:
        """Unsubscribe from the item."""
        self.clear_subscriptions()

    def on_item(self: ItemWidget, instance: ItemWidget, value: Item | None) -> None:
        """Update the widget properties when the item changes."""
        self.clear_subscriptions()
        if value is not None:
            instance.is_set = True
            instance.label = ''
            self._subscriptions.append(
                process_subscribable_value(
                    value.label,
                    lambda value: setattr(instance, 'label', value or ''),
                ),
            )

            instance.is_short = False
            self._subscriptions.append(
                process_subscribable_value(
                    value.is_short,
                    lambda value: setattr(
                        instance,
                        'is_short',
                        False if value is None else value,
                    ),
                ),
            )

            instance.color = ItemWidget.color.defaultvalue
            self._subscriptions.append(
                process_subscribable_value(
                    value.color,
                    lambda value: setattr(
                        instance,
                        'color',
                        value or ItemWidget.color.defaultvalue,
                    ),
                ),
            )

            instance.background_color = ItemWidget.background_color.defaultvalue
            self._subscriptions.append(
                process_subscribable_value(
                    value.background_color,
                    lambda value: setattr(
                        instance,
                        'background_color',
                        value or ItemWidget.background_color.defaultvalue,
                    ),
                ),
            )

            instance.icon = ''
            self._subscriptions.append(
                process_subscribable_value(
                    value.icon,
                    lambda value: setattr(instance, 'icon', value or ''),
                ),
            )
        else:
            instance.is_set = False

    def clear_subscriptions(self: ItemWidget) -> None:
        """Clear the subscriptions."""
        for subscription in self._subscriptions:
            subscription()
        self._subscriptions.clear()


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('item_widget.kv').resolve().as_posix(),
)
