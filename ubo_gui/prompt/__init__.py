from __future__ import annotations

import pathlib
import warnings
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from kivy.app import Builder
from kivy.properties import BooleanProperty, StringProperty

from ubo_gui.page import PageWidget

if TYPE_CHECKING:
    from ubo_gui.menu.types import Item, Menu

PROMPT_OPTIONS = 2


class PromptWidgetMetaClass(type(ABC), type(PageWidget)):
    ...


class PromptWidget(PageWidget, ABC, metaclass=PromptWidgetMetaClass):
    icon = StringProperty()
    prompt = StringProperty()
    first_option_label = StringProperty()
    first_option_icon = StringProperty()
    first_option_is_short = BooleanProperty(default=False)
    second_option_label = StringProperty()
    second_option_icon = StringProperty()
    second_option_is_short = BooleanProperty(default=False)

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
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init__(
            items=[
                {
                    'label': self.first_option_label,
                    'icon': self.first_option_icon,
                    'action': self.first_option_callback,
                    'is_short': self.first_option_is_short,
                },
                {
                    'label': self.second_option_label,
                    'icon': self.second_option_icon,
                    'action': self.second_option_callback,
                    'is_short': self.second_option_is_short,
                },
            ],
            **kwargs,
        )

    def get_item(self: PromptWidget, index: int) -> Item | None:
        if not 1 <= index <= PROMPT_OPTIONS:
            warnings.warn('index must be either 1 or 2', ResourceWarning, stacklevel=1)
            return None
        return self.items[index - 1]


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('prompt_widget.kv').resolve().as_posix()
)
