"""Implements the `PromptWidget` class.

A widget that renders a prompt with two options.
"""

from __future__ import annotations

import pathlib
import warnings
from abc import ABC, ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Sequence

from kivy.lang.builder import Builder
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ColorProperty,
    StringProperty,
)
from kivy.uix.widget import WidgetMetaclass

from ubo_gui.constants import DANGER_COLOR, SUCCESS_COLOR
from ubo_gui.menu.types import ActionItem

if TYPE_CHECKING:
    from ubo_gui.menu.types import Item, Menu
    from ubo_gui.page import PageWidget

PROMPT_OPTIONS = 2


class PromptWidgetMetaClass(ABCMeta, WidgetMetaclass):
    """Metaclass merging `ABC` and `PageWidget` for `PromptWidget` class."""


class PromptWidget(ABC, metaclass=PromptWidgetMetaClass):
    """A widget that renders a prompt."""

    icon: str = StringProperty()
    prompt: str = StringProperty()

    first_option_label: str = StringProperty()
    first_option_icon: str = StringProperty()
    first_option_is_short: bool = BooleanProperty(defaultvalue=False)
    first_option_background_color = ColorProperty(SUCCESS_COLOR)
    first_option_color = ColorProperty((0, 0, 0, 1))

    second_option_label: str = StringProperty()
    second_option_icon: str = StringProperty()
    second_option_is_short: bool = BooleanProperty(defaultvalue=False)
    second_option_background_color = ColorProperty(DANGER_COLOR)
    second_option_color = ColorProperty((1, 1, 1, 1))

    def get_first_item(self: PromptWidget) -> ActionItem | None:
        """Return the first item of the prompt."""
        if not self.first_option_label:
            return None
        return ActionItem(
            label=self.first_option_label,
            icon=self.first_option_icon,
            action=self.first_option_callback,
            is_short=self.first_option_is_short,
            background_color=self.first_option_background_color,
            color=self.first_option_color,
        )

    def get_second_item(self: PromptWidget) -> ActionItem | None:
        """Return the second item of the prompt."""
        if not self.second_option_label:
            return None
        return ActionItem(
            label=self.second_option_label,
            icon=self.second_option_icon,
            action=self.second_option_callback,
            is_short=self.second_option_is_short,
            background_color=self.second_option_background_color,
            color=self.second_option_color,
        )

    first_item: ActionItem = AliasProperty(
        getter=get_first_item,
        bind=[
            'first_option_label',
            'first_option_icon',
            'first_option_is_short',
            'first_option_background_color',
            'first_option_color',
        ],
        cache=True,
    )

    second_item: ActionItem = AliasProperty(
        getter=get_second_item,
        bind=[
            'second_option_label',
            'second_option_icon',
            'second_option_is_short',
            'second_option_background_color',
            'second_option_color',
        ],
        cache=True,
    )

    def _items_getter(self: PromptWidget) -> Sequence[Item | None]:
        return [self.first_item, self.second_item]

    def _items_setter(self: PromptWidget, value: Sequence[Item | None]) -> None:
        if len(value) == 0:
            return
        msg = 'Cannot set items'
        raise ValueError(msg)

    items: Sequence[Item | None] = AliasProperty(
        getter=_items_getter,
        setter=_items_setter,
        bind=['first_item', 'second_item'],
    )

    @abstractmethod
    def first_option_callback(
        self: PromptWidget,
    ) -> Menu | type[PageWidget] | None:
        """Do what the first option of the prompt should do in this callback.

        It can return a `SubMenuItem` or an `ApplicationItem` and it will become active
        if this prompt is rendered in a `MenuWidget`.
        """
        return

    @abstractmethod
    def second_option_callback(
        self: PromptWidget,
    ) -> Menu | type[PageWidget] | None:
        """Do what the second option of the prompt should do in this callback.

        It can return a `SubMenuItem` or an `ApplicationItem` and it will become active
        if this prompt is rendered in a `MenuWidget`.
        """
        return

    def get_item(self: PromptWidget, index: int) -> Item | None:
        """Return the page item at the given index."""
        if not 1 <= index <= PROMPT_OPTIONS:
            warnings.warn('index must be either 1 or 2', ResourceWarning, stacklevel=1)
            return None
        return self.first_item if index == 1 else self.second_item


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('prompt_widget.kv').resolve().as_posix(),
)
