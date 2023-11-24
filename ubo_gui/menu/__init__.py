"""Implement a paginated menu.

The first page starts with a heading and its sub-heading.
Each item may have sub items, in that case activating this item will open a new menu
with its sub items.
Each item can optionally be styled differently.
"""
from __future__ import annotations

import pathlib
import uuid
import warnings
from typing import TYPE_CHECKING, cast

from headless_kivy_pi import HeadlessWidget
from kivy.app import Builder
from kivy.properties import AliasProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager

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
    from collections.abc import Iterator

    from menu.types import Menu
    from page import PageWidget
    from typing_extensions import Any

    from ubo_gui.animated_slider import AnimatedSlider


def paginate(items: list[Item], offset: int = 0) -> Iterator[list[Item]]:
    """Yield successive PAGE_SIZE-sized chunks from list.

    Parameters
    ----------
    items: `list` of `Item`
        The items to be paginated.

    offset: `int`
        An offset greater than or equal to zero and less than `PAGE_SIZE`. The size of
        the first page will be `PAGE_SIZE` - `offset`. The default value is 0.
    """
    for i in range(PAGE_SIZE - offset, len(items), PAGE_SIZE):
        yield items[i : i + PAGE_SIZE]


class MenuWidget(BoxLayout):
    """Paginated menu."""

    def get_pages(self: MenuWidget) -> list[PageWidget]:
        return self._pages

    def set_pages(self: MenuWidget, pages: list[PageWidget]) -> None:
        self._pages = pages

    def get_is_scrollbar_visible(self: MenuWidget) -> bool:
        return self.current_application is None and len(self.pages) > 1

    title = StringProperty(allownone=True)
    page_index = NumericProperty(0)
    depth = NumericProperty(0)
    pages = AliasProperty(getter=get_pages, setter=set_pages, bind=['depth'])
    is_scrollbar_visible = AliasProperty(
        getter=get_is_scrollbar_visible,
        bind=[
            'depth',
            'pages',
        ],
    )
    _pages: list[PageWidget]
    current_menu: Menu | None = None
    current_menu_items: list[Item]
    current_application: PageWidget | None = None
    menu_stack: list[tuple[Menu, int]]
    screen_manager: ScreenManager
    slider: AnimatedSlider

    def __init__(self: MenuWidget, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize a `MenuWidget`."""
        self.pages = []
        self.current_menu_items = []
        self.menu_stack = []
        super().__init__(**kwargs)
        HeadlessWidget.activate_low_fps_mode()

    @property
    def current_depth(self: MenuWidget) -> int:
        """Depth of current menu in menu tree."""
        return len(self.menu_stack) + (1 if self.current_application else 0)

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
        self.page_index += 1
        if self.page_index >= len(self.pages):
            self.page_index = 0
        self.screen_manager.transition.direction = 'up'
        self.update()

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
        self.page_index -= 1
        if self.page_index < 0:
            self.page_index = len(self.pages) - 1
        self.screen_manager.transition.direction = 'down'
        self.update()

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
        current_page: PageWidget = self.screen_manager.current_screen
        item = current_page.get_item(index)
        if not item:
            warnings.warn('Selected `item` is `None`', RuntimeWarning, stacklevel=1)
            return
        if is_action_item(item):
            item['action']()
        elif is_sub_menu_item(item):
            self.push_menu(item['sub_menu'])
        elif is_application_item(item):
            application_instance = item['application'](name=uuid.uuid4().hex)
            self.open_application(application_instance)

    def open_application(self: MenuWidget, application: PageWidget) -> None:
        """Open an application."""
        HeadlessWidget.activate_high_fps_mode()
        self.current_application = application
        self.pages.append(self.current_application)
        self.screen_manager.add_widget(self.current_application)
        self.screen_manager.transition.direction = 'left'
        self.screen_manager.current = self.current_application.name
        self.title = (
            self.current_application.title
            if hasattr(self.current_application, 'title')
            else None
        )
        self.current_application.bind(on_close=lambda _: self.go_back())
        self.depth = self.current_depth

    def go_back(self: MenuWidget) -> None:
        """Go back to the previous menu."""
        self.screen_manager.transition.direction = 'right'
        if self.current_application:
            HeadlessWidget.activate_high_fps_mode()
            self.current_application = None
            self.set_current_menu(self.current_menu)
        else:
            self.pop_menu()
        self.depth = self.current_depth

    def update(self: MenuWidget) -> None:
        """Activate the transition from the previously active page to the current page.

        Activate high fps mode to render the animation in high fps
        """
        HeadlessWidget.activate_high_fps_mode()
        self.screen_manager.current = f'Page {self.current_depth} {self.page_index}'

    def push_menu(self: MenuWidget, menu: Menu) -> None:
        """Go one level deeper in the menu stack."""
        self.screen_manager.transition.direction = 'left'
        if self.current_menu:
            self.menu_stack.append((self.current_menu, self.page_index))
        self.page_index = 0
        self.set_current_menu(menu)
        self.depth = self.current_depth

    def pop_menu(self: MenuWidget) -> None:
        """Come up one level from of the menu stack."""
        if self.current_depth == 0:
            return
        self.screen_manager.transition.direction = 'right'
        target_menu = self.menu_stack.pop()
        self.page_index = target_menu[1]
        self.set_current_menu(target_menu[0])
        self.depth = self.current_depth

    def set_current_menu(self: MenuWidget, menu: Menu | None) -> None:
        """Set the `current_menu` and create its pages."""
        HeadlessWidget.activate_high_fps_mode()
        self.pages.clear()
        self.screen_manager.clear_widgets()

        self.current_menu = menu
        self.current_menu_items = menu_items(menu)

        if not self.current_menu:
            return

        if 'heading' in self.current_menu:
            first_page = HeaderMenuPageWidget(
                self.current_menu_items[:1],
                cast(str, self.current_menu.get('heading', '')),
                cast(str, self.current_menu.get('sub_heading', '')),
                name=f'Page {self.current_depth} 0',
            )
        else:
            first_page = NormalMenuPageWidget(
                self.current_menu_items[:3],
                name=f'Page {self.current_depth} 0',
            )
        self.pages.append(first_page)
        self.screen_manager.add_widget(first_page)

        paginated_items = paginate(
            self.current_menu_items,
            2 if 'heading' in self.current_menu else 0,
        )
        for index, page_items in enumerate(paginated_items):
            page = NormalMenuPageWidget(
                page_items,
                name=f'Page {self.current_depth} {index + 1}',
            )
            self.pages.append(page)
            self.screen_manager.add_widget(page)
        self.title = menu_title(self.current_menu)
        if self.page_index >= len(self.pages):
            self.page_index = max(len(self.pages) - 1, 0)
        self.screen_manager.current = f'Page {self.current_depth} {self.page_index}'
        self.slider.value = len(self.pages) - 1 - self.page_index
        HeadlessWidget.activate_low_fps_mode()

    def on_kv_post(self: MenuWidget, _: Any) -> None:  # noqa: ANN401
        """Activate low fps mode when transition is done."""
        self.screen_manager = cast(ScreenManager, self.ids.screen_manager)
        on_progress_ = self.screen_manager.transition.on_progress

        def on_progress(progression: float) -> None:
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


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('menu.kv').resolve().as_posix(),
)
