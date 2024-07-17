"""Implement `ItemWidget`."""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Any, Callable

from kivy.lang.builder import Builder
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout

from ubo_gui.constants import PRIMARY_COLOR
from ubo_gui.menu.types import process_subscribable_value

if TYPE_CHECKING:
    from kivy.graphics.context_instructions import Color

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
    item: Item | None = ObjectProperty(allownone=True)
    opacity: float = NumericProperty(defaultvalue=1, min=0, max=1)
    progress: float = NumericProperty(defaultvalue=1, min=0, max=1)

    _width: float = NumericProperty()
    _progress: int = NumericProperty()

    def __init__(self: ItemWidget, item: Item | None = None, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize an `ItemWidget`."""
        self._subscriptions = []
        super().__init__(item=item, **kwargs)

    def __del__(self: ItemWidget) -> None:
        """Unsubscribe from the item."""
        self.clear_subscriptions()

    def on_item(self: ItemWidget, _: ItemWidget, value: Item | None) -> None:
        """Update the widget properties when the item changes."""
        self.clear_subscriptions()
        if value is None:
            self.is_set = False
        else:
            self.is_set = True
            self.label = ''
            self._subscriptions.append(
                process_subscribable_value(
                    value.label,
                    lambda value: setattr(self, 'label', value or ''),
                ),
            )

            self.is_short = False
            self._subscriptions.append(
                process_subscribable_value(
                    value.is_short,
                    lambda value: setattr(
                        self,
                        'is_short',
                        False if value is None else value,
                    ),
                ),
            )

            self.color = ItemWidget.color.defaultvalue
            self._subscriptions.append(
                process_subscribable_value(
                    value.color,
                    lambda value: setattr(
                        self,
                        'color',
                        value or ItemWidget.color.defaultvalue,
                    ),
                ),
            )

            self.background_color = ItemWidget.background_color.defaultvalue
            self._subscriptions.append(
                process_subscribable_value(
                    value.background_color,
                    lambda value: setattr(
                        self,
                        'background_color',
                        value or ItemWidget.background_color.defaultvalue,
                    ),
                ),
            )

            self.icon = ''
            self._subscriptions.append(
                process_subscribable_value(
                    value.icon,
                    lambda value: setattr(self, 'icon', value or ''),
                ),
            )

            self.opacity = value.opacity or 1
            self.progress = min(max(value.progress or 1, 0), 1)

    def clear_subscriptions(self: ItemWidget) -> None:
        """Clear the subscriptions."""
        for subscription in self._subscriptions:
            subscription()
        self._subscriptions.clear()


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('item_widget.kv').resolve().as_posix(),
)
