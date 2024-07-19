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
from typing import TYPE_CHECKING, Callable, Self, Sequence, TypeVar, cast, overload

from headless_kivy import HeadlessWidget
from kivy.lang.builder import Builder
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ListProperty,
    NumericProperty,
)
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
    from kivy.uix.widget import Widget

    from ubo_gui.animated_slider import AnimatedSlider

VISUAL_SNAPSHOT_WIDTH = 14


@dataclass(kw_only=True)
class BaseStackItem:
    """An item in a menu stack."""

    parent: StackItem | None
    subscriptions: set[Callable[[], None]] = field(default_factory=set)

    def clear_subscriptions(self: BaseStackItem) -> None:
        """Clear all subscriptions."""
        subscriptions = self.subscriptions.copy()
        self.subscriptions.clear()
        for unsubscribe in subscriptions:
            unsubscribe()

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

    @property
    def visual_snapshot(self: StackMenuItem) -> list[str]:
        """Return the snapshot of the menu."""
        T = TypeVar('T')

        def process_callable(object_: T | Callable[[], T]) -> T:
            return object_() if callable(object_) else object_

        items = process_callable(self.menu.items)
        title = process_callable(self.menu.title)[: VISUAL_SNAPSHOT_WIDTH - 2]
        padding = '─' * ((VISUAL_SNAPSHOT_WIDTH - len(title)) // 2)
        return [
            padding + title + padding + '─' * (len(title) % 2),
            *(
                (
                    (process_callable(items[i].icon) or ' ')
                    + ' '
                    + process_callable(items[i].label)
                ).ljust(
                    VISUAL_SNAPSHOT_WIDTH,
                    ' ',
                )[:VISUAL_SNAPSHOT_WIDTH]
                if len(items) > i
                else ' ' * VISUAL_SNAPSHOT_WIDTH
                for i in range(3)
            ),
            '─' * VISUAL_SNAPSHOT_WIDTH,
        ]


@dataclass(kw_only=True)
class StackApplicationItem(BaseStackItem):
    """An application item in a menu stack."""

    application: PageWidget

    @property
    def title(self: StackApplicationItem) -> str:
        """Return the title of the application."""
        return self.application.name

    @property
    def visual_snapshot(self: StackApplicationItem) -> list[str]:
        """Return the snapshot of the application."""
        title = self.title[: VISUAL_SNAPSHOT_WIDTH - 2]
        padding = '─' * ((VISUAL_SNAPSHOT_WIDTH - len(title)) // 2)
        return [
            padding + title + padding + '─' * (len(title) % 2),
            ' ' * VISUAL_SNAPSHOT_WIDTH,
            f""" {(self.application.title or '-').ljust(VISUAL_SNAPSHOT_WIDTH - 2, " ")
            [:VISUAL_SNAPSHOT_WIDTH - 2]} """,
            ' ' * VISUAL_SNAPSHOT_WIDTH,
            '─' * VISUAL_SNAPSHOT_WIDTH,
        ]


StackItem = StackMenuItem | StackApplicationItem


class MenuWidget(BoxLayout, TransitionsMixin):
    """Paginated menu."""

    widget_subscriptions: set[Callable[[], None]]
    widget_subscriptions_lock: threading.Lock
    screen_subscriptions: set[Callable[[], None]]
    screen_subscriptions_lock: threading.Lock
    stack_lock: threading.Lock

    _current_menu_items: Sequence[Item]
    _current_screen: Screen | None = None
    _title: str | None = None
    screen_manager: ScreenManager
    slider: AnimatedSlider

    def __init__(self: MenuWidget, **kwargs: object) -> None:
        """Initialize a `MenuWidget`."""
        self._current_menu_items = []
        self.widget_subscriptions = set()
        self.widget_subscriptions_lock = threading.Lock()
        self.screen_subscriptions = set()
        self.screen_subscriptions_lock = threading.Lock()
        self.stack_lock = threading.Lock()
        super().__init__(**kwargs)
        self.bind(stack=self._render)

    def __del__(self: MenuWidget) -> None:
        """Clear all subscriptions."""
        self._clear_widget_subscriptions()
        self._clear_screen_subscriptions()

    def set_root_menu(self: MenuWidget, root_menu: Menu) -> None:
        """Set the root menu."""
        with self.stack_lock:
            self.stack = []
            self._push(root_menu, transition=self._no_transition)

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

        if self.pages == 1:
            return
        self.page_index = (self.page_index + 1) % self.pages
        self._render_menu()
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

        if self.pages == 1:
            return
        self.page_index = (self.page_index - 1) % self.pages
        self._render_menu()
        self._switch_to(
            self.current_screen,
            transition=self._slide_transition,
            direction='down',
        )

    def open_menu(self: MenuWidget, menu: Menu | Callable[[], Menu]) -> None:
        """Open a menu."""
        stack_item: StackMenuItem | None = None
        subscription: Callable[[], None] | None = None

        def handle_menu_change(menu: Menu) -> None:
            nonlocal stack_item, subscription
            logger.debug(
                'Handle `sub_menu` change...',
                extra={
                    'new_sub_menu': menu,
                    'old_sub_menu': stack_item.menu if stack_item else None,
                    'subscription_level': 'parent',
                },
            )
            with self.stack_lock:
                if stack_item:
                    stack_item = self._replace(stack_item, menu)
                else:
                    stack_item = self._push(
                        menu,
                        transition=self._slide_transition,
                        direction='left',
                    )
                    if subscription:
                        stack_item.subscriptions.add(subscription)

        subscription = process_subscribable_value(
            menu,
            handle_menu_change,
        )
        if stack_item:
            stack_item.subscriptions.add(subscription)

    def select_action_item(self: MenuWidget, item: ActionItem) -> None:
        """Select an action item."""
        result = item.action()
        if not result:
            return
        if isinstance(result, type) and issubclass(result, PageWidget):
            self.open_application(result())
        elif isinstance(result, PageWidget):
            self.open_application(result)
        elif isinstance(result, Menu) or callable(result):
            self.open_menu(result)
        else:
            msg = f'Unsupported returned value by `ActionItem`: {type(result)}'
            raise TypeError(msg)

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
            application_instance = application()
            self.open_application(application_instance)

        self.top.subscriptions.add(
            process_subscribable_value(
                item.application,
                handle_application_change,
            ),
        )

    def select_submenu_item(self: MenuWidget, item: SubMenuItem) -> None:
        """Select a submenu item."""
        self.open_menu(item.sub_menu)

    def select_item(self: MenuWidget, item: Item) -> None:
        """Select an item.

        Parameters
        ----------
        item: `Item`
            The item to select

        """
        if isinstance(item, ActionItem):
            self.select_action_item(item)
        if isinstance(item, ApplicationItem):
            self.select_application_item(item)
        if isinstance(item, SubMenuItem):
            self.select_submenu_item(item)

    def select(self: MenuWidget, index: int) -> None:
        """Select one of the items currently visible on the screen based on its index.

        Parameters
        ----------
        index: `int`
            An integer number, can only take values greater than or equal to zero and
            less than `PAGE_SIZE`

        """
        if not self.screen_manager.current_screen:
            warnings.warn('`current_screen` is `None`', RuntimeWarning, stacklevel=1)
            return
        if self._is_preparation_in_progress:
            return
        current_page = cast(PageWidget, self.current_screen)
        item = current_page.get_item(index)
        if item:
            self.select_item(item)

    def go_back(self: MenuWidget) -> None:
        """Go back to the previous menu."""
        if self.current_application:
            if not self.current_application.go_back():
                self.close_application(self.current_application)
        elif self.current_menu:
            with self.stack_lock:
                self._pop()

    def go_home(self: MenuWidget) -> None:
        """Go back to the root menu."""
        with self.stack_lock:
            self.stack = self.stack[:1]
            self._switch_to(
                self.current_screen,
                transition=self._rise_in_transition,
            )

    def _menu_items(
        self: MenuWidget,
        menu: Menu,
    ) -> Sequence[Item | None]:
        """Render a normal menu."""
        offset = -(PAGE_SIZE - 1) if isinstance(menu, HeadedMenu) else 0
        items: list[Item | None] = list(
            self.current_menu_items[
                max(self.page_index * PAGE_SIZE + offset, 0) : self.page_index
                * PAGE_SIZE
                + PAGE_SIZE
                + offset
            ],
        )
        if self.render_surroundings:
            previous_item = (
                None
                if self.page_index == 0
                else (
                    padding_item := self.current_menu_items[
                        self.page_index * PAGE_SIZE + offset - 1
                    ]
                )
                and Item(
                    label=padding_item.label,
                    icon=padding_item.icon,
                    background_color=padding_item.background_color,
                    is_short=padding_item.is_short,
                    opacity=0.6,
                )
            )
            next_item = (
                None
                if self.page_index == self.pages - 1
                else (
                    padding_item := self.current_menu_items[
                        self.page_index * PAGE_SIZE + PAGE_SIZE + offset
                    ]
                )
                and Item(
                    label=padding_item.label,
                    icon=padding_item.icon,
                    background_color=padding_item.background_color,
                    is_short=padding_item.is_short,
                    opacity=0.6,
                )
            )
            items = [previous_item, *items, next_item]
        return items

    def _render_menu(self: MenuWidget, *_: object) -> PageWidget | None:
        """Render the items of the current menu."""
        self._clear_widget_subscriptions()
        if self.page_index >= self.pages:
            self.page_index = self.pages - 1
        if not self.current_menu:
            return None
        items = self._menu_items(self.current_menu)
        if self.page_index == 0 and isinstance(self.current_menu, HeadedMenu):
            list_widget = HeaderMenuPageWidget(
                items,
                name=f'Page {self.get_depth()} 0',
                count=PAGE_SIZE - 2,
                render_surroundings=self.render_surroundings,
                padding_bottom=self.padding_bottom,
                padding_top=self.padding_top,
            )

            def handle_heading_change(heading: str) -> None:
                logger.debug(
                    'Handle `heading` change...',
                    extra={
                        'new_heading': heading,
                        'old_heading': list_widget.heading,
                        'subscription_level': 'widget',
                    },
                )
                list_widget.heading = heading

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
                        'old_sub_heading': list_widget.sub_heading,
                        'subscription_level': 'widget',
                    },
                )
                list_widget.sub_heading = sub_heading

            self.widget_subscriptions.add(
                process_subscribable_value(
                    self.current_menu.sub_heading,
                    handle_sub_heading_change,
                ),
            )
        else:
            list_widget = NormalMenuPageWidget(
                items,
                name=f'Page {self.get_depth()} 0',
                count=PAGE_SIZE,
                render_surroundings=self.render_surroundings,
                padding_bottom=self.padding_bottom,
                padding_top=self.padding_top,
            )

        self.current_screen = list_widget

        def handle_placeholder_change(placeholder: str | None) -> None:
            logger.debug(
                'Handle `placeholder` change...',
                extra={
                    'new_placeholder': placeholder,
                    'old_placeholder': list_widget.placeholder,
                    'subscription_level': 'widget',
                },
            )
            list_widget.placeholder = placeholder

        self.widget_subscriptions.add(
            process_subscribable_value(
                self.current_menu.placeholder,
                handle_placeholder_change,
            ),
        )

        return list_widget

    def _render(self: MenuWidget, *_: object) -> None:
        """Return the current screen page."""
        self._clear_screen_subscriptions()

        for line in self._visual_snapshot:
            logger.debug(line)

        if not self.stack:
            return

        title = None
        if isinstance(self.top, StackApplicationItem):
            self.current_screen = self.top.application
            title = self.top.application.title
        if isinstance(self.top, StackMenuItem):
            menu = self.top.menu
            last_items = None
            menu_widget = None

            def handle_items_change(items: Sequence[Item]) -> None:
                nonlocal last_items, menu_widget
                logger.debug(
                    'Handle `items` change...',
                    extra={
                        'new_items': items,
                        'old_items': last_items,
                        'subscription_level': 'screen',
                    },
                )
                self.current_menu_items = items
                if menu_widget is None:
                    menu_widget = self._render_menu()
                else:
                    menu_widget.items = self._menu_items(menu)
                last_items = items

            self.screen_subscriptions.add(
                process_subscribable_value(menu.items, handle_items_change),
            )

            title = menu.title

        def handle_title_change(title: str | None) -> None:
            logger.debug(
                'Handle `title` change...',
                extra={
                    'new_title': title,
                    'old_title': self.title,
                    'subscription_level': 'screen',
                },
            )
            self.title = title

        self.screen_subscriptions.add(
            process_subscribable_value(title, handle_title_change),
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
        with self.stack_lock:
            headless_widget = HeadlessWidget.get_instance(self)
            if headless_widget:
                headless_widget.activate_high_fps_mode()
            application.name = uuid.uuid4().hex
            application.padding_bottom = self.padding_bottom
            application.padding_top = self.padding_top
            self._push(
                application,
                transition=self._swap_transition,
                duration=0.2,
                direction='left',
            )

    def close_application(self: MenuWidget, application: PageWidget) -> None:
        """Close an application after its `on_close` event is fired."""
        # Remove `application` and all applications in the stack with their `root` being
        # `application` from stack and clear their bindings and subscriptions.
        # If any of these applications are the top of the stack, remove it with `pop` to
        # ensure the animation is played.
        with self.stack_lock:
            if any(
                isinstance(item.root, StackApplicationItem)
                and item.root.application is application
                for item in self.stack
            ):
                to_be_removed = [
                    cast(StackApplicationItem, item)
                    for item in self.stack
                    if isinstance(item.root, StackApplicationItem)
                    and item.root.application is application
                    and item is not self.top
                ]

                for item in to_be_removed:
                    item.clear_subscriptions()
                    item.application.dispatch('on_close')

                self.stack = [item for item in self.stack if item not in to_be_removed]

                if (
                    isinstance(self.top.root, StackApplicationItem)
                    and self.top.root.application is application
                ):
                    self._pop()

    @property
    def top(self: MenuWidget) -> StackItem:
        """Return the top item of the stack."""
        if not self.stack:
            msg = 'stack is empty'
            raise IndexError(msg)
        return self.stack[-1]

    @property
    def _visual_snapshot(self: MenuWidget) -> list[str]:
        start = [
            '╭',
            '│',
            '│',
            '│',
            '╰',
        ]
        end = [
            '╮',
            '│',
            '│',
            '│',
            '╯',
        ]

        def append(item: list[str]) -> None:
            for i in range(5):
                output[-(5 - i)] += item[i]

        output = []
        for start_item in range(0, len(self.stack), 5):
            output.extend([''] * 5)
            for item in self.stack[start_item : min(start_item + 5, len(self.stack))]:
                append(start)
                append(item.visual_snapshot)
            append(end)
        if len(self.stack) % 5 != 0:
            for _ in range(5 - (len(self.stack) % 5)):
                append([' ' * (VISUAL_SNAPSHOT_WIDTH + 1)] * 5)

        for i in range(len(self.stack)):
            output[i] += (
                f' {type(self.stack[i]).__name__} '
                f'{self.stack[i].title[:VISUAL_SNAPSHOT_WIDTH]} '
            )
        return output

    @overload
    def _replace(
        self: MenuWidget,
        stack_item: StackItem,
        item: Menu,
    ) -> StackMenuItem: ...
    @overload
    def _replace(  # pyright: ignore[reportOverlappingOverload]
        self: MenuWidget,
        stack_item: StackItem,
        item: PageWidget,
    ) -> StackApplicationItem: ...
    def _replace(
        self: MenuWidget,
        stack_item: StackItem,
        item: Menu | PageWidget,
    ) -> StackItem:
        """Replace the current menu or application."""
        if stack_item not in self.stack:
            msg = '`stack_item` not found in stack'
            raise ValueError(msg) from None
        if isinstance(item, Menu):
            new_item = StackMenuItem(
                menu=item,
                page_index=0,
                parent=self.top.parent,
            )

        elif isinstance(item, PageWidget):
            new_item = StackApplicationItem(
                application=item,
                parent=self.top.parent,
            )
        else:
            msg = f'Unsupported type: {type(item)}'
            raise TypeError(msg)
        new_item.subscriptions = stack_item.subscriptions
        self.stack[self.stack.index(stack_item)] = new_item
        if self.top is new_item:
            self._switch_to(
                self.current_screen,
                transition=self._no_transition,
            )
        return new_item

    @overload
    def _push(
        self: MenuWidget,
        item: Menu,
        /,
        *,
        transition: TransitionBase | None,
        duration: float | None = None,
        direction: str | None = None,
        parent: StackItem | None = None,
    ) -> StackMenuItem: ...
    @overload
    def _push(  # pyright: ignore[reportOverlappingOverload]
        self: MenuWidget,
        item: PageWidget,
        /,
        *,
        transition: TransitionBase | None,
        duration: float | None = None,
        direction: str | None = None,
        parent: StackItem | None = None,
    ) -> StackApplicationItem: ...
    def _push(  # noqa: PLR0913
        self: MenuWidget,
        item: Menu | PageWidget,
        /,
        *,
        transition: TransitionBase | None,
        duration: float | None = None,
        direction: str | None = None,
        parent: StackItem | None = None,
    ) -> StackItem:
        """Go one level deeper in the menu stack."""
        if isinstance(item, Menu):
            new_top = StackMenuItem(menu=item, page_index=0, parent=parent)
        elif isinstance(item, PageWidget):
            new_top = StackApplicationItem(application=item, parent=parent)
        else:
            msg = f'Unsupported type: {type(item)}'
            raise TypeError(msg)
        self.stack = [*self.stack, new_top]

        self._switch_to(
            self.current_screen,
            transition=transition,
            duration=duration,
            direction=direction,
        )

        return new_top

    def _pop(
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
        if not keep_subscriptions:
            popped.clear_subscriptions()
        if isinstance(popped, StackApplicationItem):
            popped.application.dispatch('on_close')
        target = self.top
        transition_ = self._slide_transition
        if isinstance(target, StackApplicationItem) or self.current_application:
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

    def on_kv_post(self: MenuWidget, base_widget: Widget) -> None:
        """Run after the widget is fully constructed."""
        _ = base_widget
        self.screen_manager = cast(ScreenManager, self.ids.screen_manager)
        self.slider = self.ids.slider

    def _clear_widget_subscriptions(self: MenuWidget) -> None:
        """Clear widget subscriptions."""
        with self.widget_subscriptions_lock:
            subscriptions = self.widget_subscriptions.copy()
            self.widget_subscriptions.clear()
            for unsubscribe in subscriptions:
                unsubscribe()

    def _clear_screen_subscriptions(self: MenuWidget) -> None:
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
            return max(math.ceil((len(self.current_menu_items) + 2) / 3), 1)
        if isinstance(self.current_menu, HeadlessMenu):
            return max(math.ceil(len(self.current_menu_items) / 3), 1)
        return 0

    def get_current_menu_items(self: MenuWidget) -> Sequence[Item] | None:
        """Return current menu items."""
        return self._current_menu_items

    def set_current_menu_items(self: MenuWidget, items: Sequence[Item]) -> bool:
        """Set current menu items."""
        self._current_menu_items = items
        self.slider.value = self.get_pages() - 1 - self.page_index
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
        bind=['current_menu_items', 'current_menu'],
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
    render_surroundings = BooleanProperty(
        defaultvalue=False,
        cache=True,
    )
    padding_bottom = NumericProperty(defaultvalue=0)
    padding_top = NumericProperty(defaultvalue=0)


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('menu.kv').resolve().as_posix(),
)
