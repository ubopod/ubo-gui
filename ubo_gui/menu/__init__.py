"""Implement a paginated menu.

The first page starts with a heading and its sub-heading.
Each item may have sub items, in that case activating this item will open a new menu
with its sub items.
Each item can optionally be styled differently.
"""
from __future__ import annotations

import math
import pathlib
import threading
import uuid
import warnings
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Self, Sequence, cast

from headless_kivy_pi import HeadlessWidget
from kivy.app import Builder
from kivy.properties import AliasProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager, TransitionBase

from ubo_gui.logger import logger
from ubo_gui.menu.transitions import TransitionsMixin
from ubo_gui.page import PageWidget

from .constants import PAGE_SIZE
from .types import (
    ActionItem,
    ApplicationItem,
    HeadedMenu,
    HeadlessMenu,
    Item,
    Menu,
    SubMenuItem,
    process_subscribable_value,
)
from .widgets.header_menu_page_widget import HeaderMenuPageWidget
from .widgets.normal_menu_page_widget import NormalMenuPageWidget

if TYPE_CHECKING:
    from ubo_gui.animated_slider import AnimatedSlider


@dataclass(kw_only=True)
class BaseStackItem:
    """An item in a menu stack."""

    parent: StackItem | None
    subscriptions: set[Callable[[], None]] = field(default_factory=set)

    def clear_subscriptions(self: BaseStackItem) -> None:
        """Clear all subscriptions."""
        subscriptions = self.subscriptions.copy()
        self.subscriptions.clear()
        for subscription in subscriptions:
            subscription()

    @property
    def root(self: BaseStackItem) -> StackItem:
        """Return the root item."""
        if self.parent:
            return self.parent.root
        return cast(StackItem, self)

    @property
    def title(self: Self) -> str:
        """Return the title of the item."""
        raise NotImplementedError


@dataclass(kw_only=True)
class StackMenuItem(BaseStackItem):
    """A menu item in a menu stack."""

    menu: Menu
    page_index: int

    @property
    def title(self: StackMenuItem) -> str:
        """Return the title of the menu."""
        return self.menu.title() if callable(self.menu.title) else self.menu.title


@dataclass(kw_only=True)
class StackApplicationItem(BaseStackItem):
    """An application item in a menu stack."""

    application: PageWidget

    @property
    def title(self: StackApplicationItem) -> str:
        """Return the title of the application."""
        return self.application.name


StackItem = StackMenuItem | StackApplicationItem


class MenuWidget(BoxLayout, TransitionsMixin):
    """Paginated menu."""

    widget_subscriptions: set[Callable[[], None]]
    widget_subscriptions_lock: threading.Lock
    screen_subscriptions: set[Callable[[], None]]
    screen_subscriptions_lock: threading.Lock

    _current_menu_items: Sequence[Item]
    _current_screen: Screen | None = None
    _title: str | None = None
    screen_manager: ScreenManager
    slider: AnimatedSlider

    def __init__(self: MenuWidget, **kwargs: dict[str, Any]) -> None:
        """Initialize a `MenuWidget`."""
        self._current_menu_items = []
        self.widget_subscriptions = set()
        self.widget_subscriptions_lock = threading.Lock()
        self.screen_subscriptions = set()
        self.screen_subscriptions_lock = threading.Lock()
        super().__init__(**kwargs)
        self.bind(stack=self.render)

    def __del__(self: MenuWidget) -> None:
        """Clear all subscriptions."""
        self.clear_widget_subscriptions()
        self.clear_screen_subscriptions()

    def set_root_menu(self: MenuWidget, root_menu: Menu) -> None:
        """Set the root menu."""
        self.stack = []
        self.push(root_menu, transition=self._no_transition)

    def get_depth(self: MenuWidget) -> int:
        """Return depth of the current screen."""
        return len(self.stack)

    def set_title(self: MenuWidget, title: str) -> bool:
        """Set the title of the currently active menu."""
        self._title = title
        return True

    def get_title(self: MenuWidget) -> str | None:
        """Return the title of the currently active menu."""
        if self.current_application:
            return getattr(self.current_application, 'title', None)
        if self.current_menu:
            return self._title
        return None

    def go_down(self: MenuWidget) -> None:
        """Go to the next page.

        If it is already the last page, rotate to the first page.
        """
        if self.current_application:
            self.current_application.go_down()
            return

        if self.pages <= 1:
            return
        self.page_index = (self.page_index + 1) % self.pages
        self.render_items()
        self._switch_to(
            self.current_screen,
            transition=self._slide_transition,
            direction='up',
        )

    def go_up(self: MenuWidget) -> None:
        """Go to the previous page.

        If it is already the first page, rotate to the last page.
        """
        if self.current_application:
            self.current_application.go_up()
            return

        if self.pages <= 1:
            return
        self.page_index = (self.page_index - 1) % self.pages
        self.render_items()
        self._switch_to(
            self.current_screen,
            transition=self._slide_transition,
            direction='down',
        )

    def open_menu(self: MenuWidget, menu: Menu | Callable[[], Menu]) -> None:
        """Open a menu."""
        last_sub_menu: Menu | None = None

        def handle_menu_change(menu: Menu) -> None:
            nonlocal last_sub_menu
            logger.debug(
                'Handle `sub_menu` change...',
                extra={
                    'new_sub_menu': menu,
                    'old_sub_menu': last_sub_menu,
                    'subscription_level': 'parent',
                },
            )
            if last_sub_menu:
                self.replace(menu)
            else:
                self.push(menu, transition=self._slide_transition, direction='left')
            last_sub_menu = menu

        susbscription = process_subscribable_value(
            menu,
            handle_menu_change,
        )

        self.top.subscriptions.add(susbscription)

    def select_action_item(self: MenuWidget, item: ActionItem) -> None:
        """Select an action item."""
        result = item.action()
        if not result:
            return
        if isinstance(result, type) and issubclass(result, PageWidget):
            application_instance = result(name=uuid.uuid4().hex)
            self.open_application(application_instance)
        else:
            self.open_menu(result)

    def select_application_item(self: MenuWidget, item: ApplicationItem) -> None:
        """Select an application item."""
        application_instance: PageWidget | None = None

        def handle_application_change(application: type[PageWidget]) -> None:
            nonlocal application_instance
            logger.debug(
                'Handle `application` change...',
                extra={
                    'new_application_class': application,
                    'old_application_class': type(application_instance),
                    'old_application': application_instance,
                    'subscription_level': 'parent',
                },
            )
            if application_instance:
                self.close_application(application_instance)
            application_instance = application(name=uuid.uuid4().hex)
            self.open_application(application_instance)

        subscription = process_subscribable_value(
            item.application,
            handle_application_change,
        )
        self.top.subscriptions.add(subscription)

    def select_submenu_item(self: MenuWidget, item: SubMenuItem) -> None:
        """Select a submenu item."""
        self.open_menu(item.sub_menu)

    def select(self: MenuWidget, index: int) -> None:
        """Select one of the items currently visible on the screen.

        Parameters
        ----------
        index: `int`
            An integer number, can only take values greater than or equal to zero and
            less than `PAGE_SIZE`

        """
        if not self.screen_manager.current_screen:
            warnings.warn('`current_screen` is `None`', RuntimeWarning, stacklevel=1)
            return
        current_page = cast(PageWidget, self.screen_manager.current_screen)
        item = current_page.get_item(index)

        if isinstance(item, ActionItem):
            self.select_action_item(item)
        if isinstance(item, ApplicationItem):
            self.select_application_item(item)
        if isinstance(item, SubMenuItem):
            self.select_submenu_item(item)

    def go_back(self: MenuWidget) -> None:
        """Go back to the previous menu."""
        if self.current_application and self.current_application.go_back():
            return
        HeadlessWidget.activate_high_fps_mode()
        self.pop()

    def render_items(self: MenuWidget, *_: object) -> None:
        """Render the items of the current menu."""
        self.clear_widget_subscriptions()
        if self.page_index == 0 and isinstance(self.current_menu, HeadedMenu):
            header_menu_page_widget = HeaderMenuPageWidget(
                self.current_menu_items[:1],
                name=f'Page {self.get_depth()} 0',
            )

            def handle_heading_change(heading: str) -> None:
                logger.debug(
                    'Handle `heading` change...',
                    extra={
                        'new_heading': heading,
                        'old_heading': header_menu_page_widget.heading,
                        'subscription_level': 'widget',
                    },
                )
                if heading != header_menu_page_widget.heading:
                    header_menu_page_widget.heading = heading

            self.widget_subscriptions.add(
                process_subscribable_value(
                    self.current_menu.heading,
                    handle_heading_change,
                ),
            )

            def handle_sub_heading_change(sub_heading: str) -> None:
                logger.debug(
                    'Handle `sub_heading` change...',
                    extra={
                        'new_sub_heading': sub_heading,
                        'old_sub_heading': header_menu_page_widget.sub_heading,
                        'subscription_level': 'widget',
                    },
                )
                if sub_heading != header_menu_page_widget.sub_heading:
                    header_menu_page_widget.sub_heading = sub_heading

            self.widget_subscriptions.add(
                process_subscribable_value(
                    self.current_menu.sub_heading,
                    handle_sub_heading_change,
                ),
            )

            self.current_screen = header_menu_page_widget
        else:
            offset = (
                -(PAGE_SIZE - 1) if isinstance(self.current_menu, HeadedMenu) else 0
            )
            self.current_screen = NormalMenuPageWidget(
                self.current_menu_items[
                    self.page_index * 3 + offset : self.page_index * 3 + 3 + offset
                ],
                name=f'Page {self.get_depth()} 0',
            )

    def render(self: MenuWidget, *_: object) -> None:
        """Return the current screen page."""
        self.clear_screen_subscriptions()

        if not self.stack:
            return

        if isinstance(self.top, StackApplicationItem):
            self.current_screen = self.top.application
        if isinstance(self.top, StackMenuItem):
            menu = self.top.menu
            last_items = None

            def handle_items_change(items: Sequence[Item]) -> None:
                nonlocal last_items
                logger.debug(
                    'Handle `items` change...',
                    extra={
                        'new_items': items,
                        'old_items': last_items,
                        'subscription_level': 'screen',
                    },
                )
                if items != last_items:
                    self.current_menu_items = items
                    self.render_items()
                    if last_items:
                        self._switch_to(
                            self.current_screen,
                            transition=self._no_transition,
                        )
                    last_items = items

            self.screen_subscriptions.add(
                process_subscribable_value(menu.items, handle_items_change),
            )

            def handle_title_change(title: str) -> None:
                logger.debug(
                    'Handle `title` change...',
                    extra={
                        'new_title': title,
                        'old_title': self.title,
                        'subscription_level': 'screen',
                    },
                )
                if self._title != title:
                    self.title = title

            self.screen_subscriptions.add(
                process_subscribable_value(menu.title, handle_title_change),
            )

    def get_current_screen(self: MenuWidget) -> Screen | None:
        """Return current screen."""
        return self._current_screen

    def _get_current_screen(self: MenuWidget) -> Screen | None:
        """Workaround for `AliasProperty` not working with overridden getters."""
        return self.get_current_screen()

    def set_current_screen(self: MenuWidget, screen: Screen) -> bool:
        """Set the current screen page."""
        self._current_screen = screen
        return True

    def open_application(self: MenuWidget, application: PageWidget) -> None:
        """Open an application."""
        HeadlessWidget.activate_high_fps_mode()
        self.push(
            application,
            transition=self._swap_transition,
            duration=0.2,
            direction='left',
        )
        application.bind(on_close=self.close_application)

    def clean_application(self: MenuWidget, application: PageWidget) -> None:
        """Clean up the application bounds."""
        application.unbind(on_close=self.close_application)

    def close_application(self: MenuWidget, application: PageWidget) -> None:
        """Close an application after its `on_close` event is fired."""
        self.clean_application(application)
        if application in self.stack:
            while application in self.stack:
                self.go_back()

    @property
    def top(self: MenuWidget) -> StackItem:
        """Return the top item of the stack."""
        if not self.stack:
            msg = 'stack is empty'
            raise IndexError(msg)
        return self.stack[-1]

    def replace(
        self: MenuWidget,
        item: Menu | PageWidget,
    ) -> None:
        """Replace the current menu or application."""
        subscriptions = self.top.subscriptions.copy()
        if isinstance(item, Menu):
            self.stack[-1] = StackMenuItem(
                menu=item,
                page_index=0,
                parent=self.top.parent,
            )

        elif isinstance(item, PageWidget):
            self.stack[-1] = StackApplicationItem(
                application=item,
                parent=self.top.parent,
            )
        self.top.subscriptions = subscriptions
        self._switch_to(
            self.current_screen,
            transition=self._no_transition,
        )

    def push(  # noqa: PLR0913
        self: MenuWidget,
        item: Menu | PageWidget,
        /,
        *,
        transition: TransitionBase | None,
        duration: float | None = None,
        direction: str | None = None,
        parent: StackItem | None = None,
    ) -> None:
        """Go one level deeper in the menu stack."""
        if isinstance(item, Menu):
            self.stack = [
                *self.stack,
                StackMenuItem(menu=item, page_index=0, parent=parent),
            ]
        elif isinstance(item, PageWidget):
            self.stack = [
                *self.stack,
                StackApplicationItem(application=item, parent=parent),
            ]

        self._switch_to(
            self.current_screen,
            transition=transition,
            duration=duration,
            direction=direction,
        )

    def pop(
        self: MenuWidget,
        /,
        *,
        transition: TransitionBase | None = None,
        duration: float | None = None,
        direction: str | None = 'right',
        keep_subscriptions: bool = False,
    ) -> None:
        """Come up one level from of the menu stack."""
        if self.depth == 1:
            return
        *self.stack, popped = self.stack
        if not keep_subscriptions and isinstance(popped, StackMenuItem):
            popped.clear_subscriptions()
        target = self.top
        transition_ = self._slide_transition
        if isinstance(target, PageWidget):
            transition_ = self._swap_transition
            if self.current_application:
                self.clean_application(self.current_application)
        elif self.current_application:
            self.clean_application(self.current_application)
            transition_ = self._swap_transition
        self._switch_to(
            self.current_screen,
            transition=transition or transition_,
            duration=duration,
            direction=direction,
        )

    def get_is_scrollbar_visible(self: MenuWidget) -> bool:
        """Return whether scroll-bar is needed or not."""
        return not self.current_application and self.pages > 1

    def on_kv_post(self: MenuWidget, base_widget: Any) -> None:  # noqa: ANN401
        """Activate low fps mode when transition is done."""
        _ = base_widget
        self.screen_manager = cast(ScreenManager, self.ids.screen_manager)
        self.slider = self.ids.slider

    def clear_widget_subscriptions(self: MenuWidget) -> None:
        """Clear widget subscriptions."""
        with self.widget_subscriptions_lock:
            subscriptions = self.widget_subscriptions.copy()
            self.widget_subscriptions.clear()
            for subscription in subscriptions:
                subscription()

    def clear_screen_subscriptions(self: MenuWidget) -> None:
        """Clear screen subscriptions."""
        # lock the mutex to do it atomic
        with self.screen_subscriptions_lock:
            subscriptions = self.screen_subscriptions.copy()
            self.screen_subscriptions.clear()
            for unsubscribe in subscriptions:
                unsubscribe()

    def get_current_application(self: MenuWidget) -> PageWidget | None:
        """Return the current application."""
        if self.stack and isinstance(self.top, StackApplicationItem):
            return self.top.application
        return None

    def get_current_menu(self: MenuWidget) -> Menu | None:
        """Return the current menu."""
        if self.stack and isinstance(self.top, StackMenuItem):
            return self.top.menu
        return None

    def get_page_index(self: MenuWidget) -> int:
        """Return the current page index."""
        if self.stack and isinstance(self.top, StackMenuItem):
            return self.top.page_index
        return 0

    def set_page_index(self: MenuWidget, page_index: int) -> bool:
        """Set the current page index."""
        if self.stack and isinstance(self.top, StackMenuItem):
            if self.top.page_index != page_index:
                self.top.page_index = page_index
                return True
            return False
        return True

    def get_pages(self: MenuWidget) -> int:
        """Return the number of pages of the currently active menu."""
        if isinstance(self.current_menu, HeadedMenu):
            return math.ceil((len(self.current_menu_items) + 2) / 3)
        if isinstance(self.current_menu, HeadlessMenu):
            return math.ceil(len(self.current_menu_items) / 3)
        return 0

    def get_current_menu_items(self: MenuWidget) -> Sequence[Item] | None:
        """Return current menu items."""
        return self._current_menu_items

    def set_current_menu_items(self: MenuWidget, items: Sequence[Item]) -> bool:
        """Set current menu items."""
        self._current_menu_items = items
        self.slider.value = self.get_pages() - 1
        return True

    stack: list[StackItem] = ListProperty()
    title = AliasProperty(
        getter=get_title,
        setter=set_title,
        bind=['stack'],
    )
    depth: int = AliasProperty(getter=get_depth, bind=['stack'], cache=True)
    pages: int = AliasProperty(
        getter=get_pages,
        bind=['current_menu_items'],
        cache=True,
    )
    page_index = AliasProperty(
        getter=get_page_index,
        setter=set_page_index,
        bind=['current_menu_items'],
    )
    current_menu_items: Sequence[Item] = AliasProperty(
        getter=get_current_menu_items,
        setter=set_current_menu_items,
    )
    current_application: PageWidget | None = AliasProperty(
        getter=get_current_application,
        bind=['stack'],
        cache=True,
    )
    current_menu: Menu | None = AliasProperty(
        getter=get_current_menu,
        bind=['stack'],
        cache=True,
    )
    current_screen: Screen | None = AliasProperty(
        getter=_get_current_screen,
        setter=set_current_screen,
    )
    is_scrollbar_visible = AliasProperty(
        getter=get_is_scrollbar_visible,
        bind=['pages'],
        cache=True,
    )


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('menu.kv').resolve().as_posix(),
)
