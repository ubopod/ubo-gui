from __future__ import annotations

import pathlib
import warnings
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from kivy.app import Builder
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ColorProperty,
    StringProperty,
)

from ubo_gui.page import PageWidget

if TYPE_CHECKING:
    from ubo_gui.menu.types import ActionItem, Item, Menu

PROMPT_OPTIONS = 2


class PromptWidgetMetaClass(type(ABC), type(PageWidget)):
    ...


class PromptWidget(PageWidget, ABC, metaclass=PromptWidgetMetaClass):
    icon = StringProperty()
    prompt = StringProperty()

    first_option_label = StringProperty()
    first_option_icon = StringProperty()
    first_option_is_short = BooleanProperty(default=False)
    first_option_background_color = ColorProperty('#03F7AE')
    first_option_color = ColorProperty((0, 0, 0, 1))

    second_option_label = StringProperty()
    second_option_icon = StringProperty()
    second_option_is_short = BooleanProperty(default=False)
    second_option_background_color = ColorProperty('#FF3F51')
    second_option_color = ColorProperty((1, 1, 1, 1))

    def get_first_item(self: PromptWidget) -> ActionItem | None:
        if self.first_option_label is None:
            return None
        return {
            'label': self.first_option_label,
            'icon': self.first_option_icon,
            'action': self.first_option_callback,
            'is_short': self.first_option_is_short,
            'background_color': self.first_option_background_color,
            'color': self.first_option_color,
        }

    def get_second_item(self: PromptWidget) -> ActionItem | None:
        if self.second_option_label is None:
            return None
        return {
            'label': self.second_option_label,
            'icon': self.second_option_icon,
            'action': self.second_option_callback,
            'is_short': self.second_option_is_short,
            'background_color': self.second_option_background_color,
            'color': self.second_option_color,
        }

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

    def __init__(
        self: PromptWidget,
        items: None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init__(items=items, **kwargs)

    def get_item(self: PromptWidget, index: int) -> Item | None:
        if not 1 <= index <= PROMPT_OPTIONS:
            warnings.warn('index must be either 1 or 2', ResourceWarning, stacklevel=1)
            return None
        return self.first_item if index == 1 else self.second_item


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('prompt_widget.kv').resolve().as_posix(),
)
