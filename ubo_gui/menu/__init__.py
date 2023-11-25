"""Implement a paginated menu.

The first page starts with a heading and its sub-heading.
Each item may have sub items, in that case activating this item will open a new menu
with its sub items.
Each item can optionally be styled differently.
"""
from __future__ import annotations

import math
import pathlib
import uuid
import warnings
from typing import TYPE_CHECKING, cast

from headless_kivy_pi import HeadlessWidget
from kivy.app import Builder
from kivy.properties import AliasProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager

from ubo_gui.page import PageWidget

from .constants import PAGE_SIZE
from .header_menu_page_widget import HeaderMenuPageWidget
from .normal_menu_page_widget import NormalMenuPageWidget
from .types import (
    Item,
    is_action_item,
    is_application_item,
    is_sub_menu_item,
    menu_items,
    menu_title,
)

if TYPE_CHECKING:
    from menu.types import Menu
    from typing_extensions import Any

    from ubo_gui.animated_slider import AnimatedSlider


class MenuWidget(BoxLayout):
    """Paginated menu."""

    _current_menu: Menu | None = None
    _current_application: PageWidget | None = None
    current_menu_items: list[Item]
    screen_manager: ScreenManager
    slider: AnimatedSlider

    def __init__(self: MenuWidget, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize a `MenuWidget`."""
        self.current_menu_items = []
        super().__init__(**kwargs)

    def set_root_menu(self: MenuWidget, root_menu: Menu) -> None:
        """Set the root menu."""
        self.current_menu = root_menu
        self.screen_manager.switch_to(self.current_screen)

    def get_depth(self: MenuWidget) -> int:
        """Return depth of the current screen."""
        return len(self.stack)

    def get_pages(self: MenuWidget) -> int:
        """Return the number of pages of the currently active menu."""
        if not self.current_menu:
            return 0
        if 'heading' in self.current_menu:
            return math.ceil((len(self.current_menu_items) + 2) / 3)
        return math.ceil(len(self.current_menu_items) / 3)

    def get_title(self: MenuWidget) -> str | None:
        """Return the title of the currently active menu."""
        if self.current_application:
            return getattr(self.current_application, 'title', None)
        if self.current_menu:
            return menu_title(self.current_menu)
        return None

    def go_down(self: MenuWidget) -> None:
        """Go to the next page.

        If it is already the last page, rotate to the first page.
        """
        if self.current_application:
            if hasattr(self.current_application, 'go_down'):
                self.current_application.go_down()
            return

        if len(self.current_menu_items) == 0:
            return
        self.page_index = (self.page_index + 1) % self.pages
        self.screen_manager.switch_to(self.current_screen, direction='up')

    def go_up(self: MenuWidget) -> None:
        """Go to the previous page.

        If it is already the first page, rotate to the last page.
        """
        if self.current_application:
            if hasattr(self.current_application, 'go_up'):
                self.current_application.go_up()
            return

        if len(self.current_menu_items) == 0:
            return
        self.page_index = (self.page_index - 1) % self.pages
        self.screen_manager.switch_to(self.current_screen, direction='down')

    def select(self: MenuWidget, index: int) -> None:
        """Select one of the items currently visible on the screen.

        Parameters
        ----------
        index: `int`
            An integer number, can only take values greater than or equal to zero and
            less than `PAGE_SIZE`
        """
        if self.screen_manager.current_screen is None:
            warnings.warn('`current_screen` is `None`', RuntimeWarning, stacklevel=1)
            return
        current_page = cast(PageWidget, self.screen_manager.current_screen)
        item = current_page.get_item(index)
        if not item:
            warnings.warn('Selected `item` is `None`', RuntimeWarning, stacklevel=1)
            return

        if is_action_item(item):
            item = item['action']()
            if not item:
                return
            if isinstance(item, type):
                application_instance = item(name=uuid.uuid4().hex)
                self.push_menu()
                self.open_application(application_instance)
            else:
                self.push_menu()
                self.current_menu = item
                self.screen_manager.switch_to(self.current_screen, direction='left')
        elif is_application_item(item):
            application_instance = item['application'](name=uuid.uuid4().hex)
            self.push_menu()
            self.open_application(application_instance)
        elif is_sub_menu_item(item):
            self.push_menu()
            self.current_menu = item['sub_menu']
            self.screen_manager.switch_to(self.current_screen, direction='left')

    def go_back(self: MenuWidget) -> None:
        """Go back to the previous menu."""
        if (
            self.current_application
            and hasattr(self.current_application, 'go_back')
            and self.current_application.go_back()
        ):
            return
        HeadlessWidget.activate_high_fps_mode()
        self.pop_menu()

    def get_current_screen(self: MenuWidget) -> Screen | None:
        """Return the current screen page."""
        if self.current_application:
            return self.current_application

        if not self.current_menu:
            return None

        if self.page_index == 0 and 'heading' in self.current_menu:
            return HeaderMenuPageWidget(
                self.current_menu_items[:1],
                cast(str, self.current_menu.get('heading', '')),
                cast(str, self.current_menu.get('sub_heading', '')),
                name=f'Page {self.get_depth()} 0',
            )

        offset = -(PAGE_SIZE - 1) if 'heading' in self.current_menu else 0
        return NormalMenuPageWidget(
            self.current_menu_items[
                self.page_index * 3 + offset : self.page_index * 3 + 3 + offset
            ],
            name=f'Page {self.get_depth()} 0',
        )

    def open_application(self: MenuWidget, application: PageWidget) -> None:
        """Open an application."""
        HeadlessWidget.activate_high_fps_mode()
        self.current_application = application
        self.screen_manager.switch_to(self.current_screen, direction='left')

        def on_close(_: PageWidget) -> None:
            self.go_back()
            application.unbind(on_close=on_close)

        application.bind(on_close=on_close)

    def push_menu(self: MenuWidget) -> None:
        """Go one level deeper in the menu stack."""
        if self.current_menu:
            self.stack.append((self.current_menu, self.page_index))
            self.current_menu = None
        elif self.current_application:
            self.stack.append(self.current_application)
            self.current_application = None
        self.page_index = 0

    def pop_menu(self: MenuWidget) -> None:
        """Come up one level from of the menu stack."""
        if self.depth == 0:
            return
        target = self.stack.pop()
        if isinstance(target, PageWidget):
            self.current_application = target
            self.current_menu = None
            self.page_index = 0
        else:
            self.current_application = None
            self.current_menu = target[0]
            self.page_index = target[1]
        self.screen_manager.switch_to(self.current_screen, direction='right')

    def get_is_scrollbar_visible(self: MenuWidget) -> bool:
        """Return whether scroll-bar is needed or not."""
        return self.current_application is None and self.pages > 1

    def get_current_application(self: MenuWidget) -> PageWidget | None:
        """Return current application."""
        return self._current_application

    def set_current_application(
        self: MenuWidget,
        application: PageWidget | None,
    ) -> bool:
        """Set current application."""
        self._current_application = application

        return True

    def get_current_menu(self: MenuWidget) -> Menu | None:
        """Return current menu."""
        return self._current_menu

    def set_current_menu(self: MenuWidget, menu: Menu | None) -> bool:
        """Set the current menu."""
        self.current_menu_items = menu_items(menu)
        self._current_menu = menu

        if not menu:
            self.page_index = 0
            return True

        pages = self.get_pages()
        if self.page_index >= pages:
            self.page_index = max(self.pages - 1, 0)
        self.slider.value = pages - 1 - self.page_index
        return True

    def on_kv_post(self: MenuWidget, _: Any) -> None:  # noqa: ANN401
        """Activate low fps mode when transition is done."""
        self.screen_manager = cast(ScreenManager, self.ids.screen_manager)
        on_progress_ = self.screen_manager.transition.on_progress

        def on_progress(progression: float) -> None:
            if progression is 0:  # noqa: F632 - float 0.0 is not accepted, we are looking for int 0
                HeadlessWidget.activate_high_fps_mode()
            self.screen_manager.transition.screen_out.opacity = 1 - progression
            self.screen_manager.transition.screen_in.opacity = progression
            on_progress_(progression)

        def on_complete() -> None:
            self.screen_manager.transition.screen_out.opacity = 0
            self.screen_manager.transition.screen_in.opacity = 1
            HeadlessWidget.activate_low_fps_mode()

        self.screen_manager.transition.on_progress = on_progress
        self.screen_manager.transition.on_complete = on_complete

        self.slider = self.ids.slider

    page_index = NumericProperty(0)
    stack: list[tuple[Menu, int] | PageWidget] = ListProperty()
    title = AliasProperty(
        getter=get_title,
        bind=['current_menu', 'current_application'],
        cache=True,
    )
    depth: int = AliasProperty(
        getter=get_depth,
        bind=['current_menu', 'current_application'],
        cache=True,
    )
    pages: int = AliasProperty(getter=get_pages, bind=['current_menu'], cache=True)
    current_application: PageWidget | None = AliasProperty(
        getter=get_current_application,
        setter=set_current_application,
        cache=True,
    )
    current_menu: Menu | None = AliasProperty(
        getter=get_current_menu,
        setter=set_current_menu,
        cache=True,
    )
    current_screen: Menu | None = AliasProperty(
        getter=get_current_screen,
        cache=True,
        bind=['current_menu', 'page_index', 'current_application'],
    )
    is_scrollbar_visible = AliasProperty(
        getter=get_is_scrollbar_visible,
        bind=['pages', 'current_application'],
        cache=True,
    )


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('menu.kv').resolve().as_posix(),
)
