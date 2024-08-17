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
from typing import TYPE_CHECKING, Callable, Sequence, cast, overload

from headless_kivy import HeadlessWidget
from kivy.clock import mainthread
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
from ubo_gui.menu._transitions import TransitionsMixin
from ubo_gui.page import PageWidget

from .constants import PAGE_SIZE
from .stack_item import (
    VISUAL_SNAPSHOT_WIDTH,
    StackApplicationItem,
    StackItem,
    StackMenuItem,
    StackMenuItemSelection,
)
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
from .widgets.menu_page_widget import MenuPageWidget

if TYPE_CHECKING:
    from kivy.uix.widget import Widget

    from ubo_gui.animated_slider import AnimatedSlider


class MenuWidget(BoxLayout, TransitionsMixin):
    """Paginated menu."""

    menu_subscriptions: set[Callable[[], None]]
    menu_subscriptions_lock: threading.Lock
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
        self.menu_subscriptions = set()
        self.menu_subscriptions_lock = threading.Lock()
        self.screen_subscriptions = set()
        self.screen_subscriptions_lock = threading.Lock()
        self.stack_lock = threading.Lock()
        super().__init__(**kwargs)
        self.bind(stack=self._render)

    def __del__(self: MenuWidget) -> None:
        """Clear all subscriptions."""
        self._clear_menu_subscriptions()
        self._clear_screen_subscriptions()
        for item in self.stack:
            item.clear_subscriptions()

    def set_root_menu(self: MenuWidget, root_menu: Menu) -> None:
        """Set the root menu."""
        with self.stack_lock:
            if not self.stack:
                self._push(root_menu, transition=self._no_transition)
            else:
                self._replace_menu(self.root, root_menu)

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

    @mainthread
    def go_down(self: MenuWidget) -> None:
        """Go to the next page.

        If it is already the last page, rotate to the first page.
        """
        if self.current_application:
            self.current_application.go_down()
            return

        if self.pages == 1:
            return

        if self.current_menu:
            menu_page = cast(PageWidget, self.current_screen)

            menu_page.clone.page_index = self.page_index = (
                self.page_index + 1
            ) % self.pages
            menu_page.clone.items = self._menu_items(self.current_menu)

            self._switch_to(
                menu_page.clone,
                transition=self._slide_transition,
                direction='up',
            )
            self.current_screen = menu_page.clone

    @mainthread
    def go_up(self: MenuWidget) -> None:
        """Go to the previous page.

        If it is already the first page, rotate to the last page.
        """
        if self.current_application:
            self.current_application.go_up()
            return

        if self.pages == 1:
            return

        if self.current_menu:
            menu_page = cast(PageWidget, self.current_screen)

            menu_page.clone.page_index = self.page_index = (
                self.page_index - 1
            ) % self.pages
            menu_page.clone.items = self._menu_items(self.current_menu)

            self._switch_to(
                menu_page.clone,
                transition=self._slide_transition,
                direction='down',
            )
            self.current_screen = menu_page.clone

    def open_menu(
        self: MenuWidget,
        menu: Menu | Callable[[], Menu],
        *,
        key: str = '',
    ) -> None:
        """Open a menu."""
        parent = self.top
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
                    stack_item = self._replace_menu(stack_item, menu)
                elif menu:
                    stack_item = self._push(
                        menu,
                        parent=parent,
                        key=key,
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
        if item.key:
            self.open_menu(item.sub_menu, key=item.key)
        else:
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
            for item in self.stack[1:]:
                item.clear_subscriptions()
                if isinstance(item, StackApplicationItem):
                    item.application.dispatch('on_close')
            self.root.selection = None
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
        if self.page_index >= self.pages:
            self.page_index = self.pages - 1
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

    def _render_menu(self: MenuWidget, menu: Menu) -> MenuPageWidget:
        """Render the items of the current menu."""
        if self.page_index >= self.pages:
            self.page_index = self.pages - 1
        items = self._menu_items(menu)

        list_widget = MenuPageWidget(
            items,
            page_index=self.page_index,
            name=f'Page {self.get_depth()} {self.page_index}',
            count=PAGE_SIZE,
            render_surroundings=self.render_surroundings,
            padding_bottom=self.padding_bottom,
            padding_top=self.padding_top,
        )

        if isinstance(self.current_menu, HeadedMenu):

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

            self.menu_subscriptions.add(
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

            self.menu_subscriptions.add(
                process_subscribable_value(
                    self.current_menu.sub_heading,
                    handle_sub_heading_change,
                ),
            )

        return list_widget

    def _render(self: MenuWidget, *_: object) -> None:
        """Return the current screen page."""
        self._clear_screen_subscriptions()

        if not self.stack:
            return

        title = None
        if isinstance(self.top, StackApplicationItem):
            self.current_screen = self.top.application
            title = self.top.application.title
        if isinstance(self.top, StackMenuItem):
            menu = self.top.menu
            last_items = None
            menu_page: MenuPageWidget | None = None
            placeholder = None

            def handle_items_change(items: Sequence[Item]) -> None:
                nonlocal last_items, menu_page
                logger.debug(
                    'Handle `items` change...',
                    extra={
                        'new_items': items,
                        'old_items': last_items,
                        'subscription_level': 'screen',
                    },
                )
                self.current_menu_items = items
                if menu_page is None:
                    self._clear_menu_subscriptions()
                    menu_page = self._render_menu(menu)
                    # The clone here is solely needed for the visual transitions between
                    # menu pages, when `page_index` increases or decreases, the slide
                    # down/up transition needs a source and a target. So a clone of the
                    # original page is needed. If `ScreenManager` supported transition
                    # from a screen to itself we probably wouldn't need this.
                    menu_page.clone = self._render_menu(menu)
                    menu_page.clone.clone = menu_page
                    self.current_screen = menu_page
                else:
                    if self.page_index >= self.pages:
                        menu_page.page_index = self.page_index = self.pages - 1
                        menu_page.clone.page_index = self.page_index = self.pages - 1
                    menu_page.items = self._menu_items(menu)
                    menu_page.clone.items = self._menu_items(menu)
                menu_page.placeholder = placeholder
                menu_page.clone.placeholder = placeholder
                last_items = items

            self.screen_subscriptions.add(
                process_subscribable_value(menu.items, handle_items_change),
            )

            def handle_placeholder_change(new_placeholder: str | None) -> None:
                nonlocal placeholder
                logger.debug(
                    'Handle `placeholder` change...',
                    extra={
                        'new_placeholder': new_placeholder,
                        'old_placeholder': placeholder,
                        'subscription_level': 'widget',
                    },
                )
                placeholder = new_placeholder
                if menu_page:
                    menu_page.placeholder = placeholder

            self.menu_subscriptions.add(
                process_subscribable_value(
                    menu.placeholder,
                    handle_placeholder_change,
                ),
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
    def root(self: MenuWidget) -> StackMenuItem:
        """Return the root item."""
        if isinstance(self.stack[0], StackMenuItem):
            return self.stack[0]
        msg = 'root is not a `StackMenuItem`'
        raise ValueError(msg)

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

        cross_repeats = VISUAL_SNAPSHOT_WIDTH // 3
        cross = [
            '───' * cross_repeats,
            '╲ ╱' * cross_repeats,  # noqa: RUF001
            ' ╳ ' * cross_repeats,  # noqa: RUF001
            '╱ ╲' * cross_repeats,  # noqa: RUF001
            '───' * cross_repeats,
        ]

        def append(item: list[str]) -> None:
            for i in range(5):
                output[-(5 - i)] += item[i] if i < len(item) else ' ' * len(item[0])

        output = []
        for start_item in range(0, len(self.stack), 5):
            output.extend([''] * 5)
            for item in self.stack[start_item : min(start_item + 5, len(self.stack))]:
                append(start)
                append(item.visual_snapshot)
            append(end)
            append(
                [
                    f' {type(item).__name__} {item.title[:VISUAL_SNAPSHOT_WIDTH]} '
                    for item in self.stack[
                        start_item : min(start_item + 5, len(self.stack))
                    ]
                ],
            )

            output.extend([''] * 5)
            for item in self.stack[start_item : min(start_item + 5, len(self.stack))]:
                append(start)
                append(item.parent.visual_snapshot if item.parent else cross)
            append(end)

            output.extend([''] * 5)
            for item in self.stack[start_item : min(start_item + 5, len(self.stack))]:
                append(start)
                append(
                    item.selection.item.visual_snapshot
                    if isinstance(item, StackMenuItem) and item.selection
                    else cross,
                )
            append(end)
        if len(self.stack) % 5 != 0:
            for _ in range(5 - (len(self.stack) % 5)):
                append([' ' * (VISUAL_SNAPSHOT_WIDTH + 1)] * 5)

        return output

    def _replace_menu(
        self: MenuWidget,
        stack_item: StackMenuItem,
        menu: Menu,
        *,
        parent: StackItem | None = None,
    ) -> StackMenuItem:
        """Replace the current menu or application."""
        if stack_item not in self.stack:
            msg = '`stack_item` not found in stack'
            raise ValueError(msg) from None
        if stack_item.selection:
            items = [
                item
                for item in (menu.items() if callable(menu.items) else menu.items)
                if isinstance(item, SubMenuItem)
                and item.key == stack_item.selection.key
            ]
            if len(items) == 1:
                selection = items[0]
            elif len(items) > 1:
                msg = f'Found more than one item with key: {stack_item.selection.key}'
                raise ValueError(msg)
            else:
                selection = None
        else:
            selection = None
        index = self.stack.index(stack_item)
        new_item = self.stack[index] = StackMenuItem(
            menu=menu,
            page_index=stack_item.page_index,
            parent=parent or stack_item.parent,
            subscriptions=stack_item.subscriptions,
        )
        new_item.selection = (
            None
            if selection is None
            or stack_item.selection is None
            or not isinstance(selection.sub_menu, Menu)
            else StackMenuItemSelection(
                key=stack_item.selection.key,
                item=self._replace_menu(
                    stack_item.selection.item,
                    selection.sub_menu,
                    parent=new_item,
                ),
            )
        )

        if new_item is self.top:
            self._switch_to(self.current_screen, transition=self._no_transition)
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
        key: str | None = None,
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
        key: str | None = None,
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
        key: str | None = None,
    ) -> StackItem:
        """Go one level deeper in the menu stack."""
        if isinstance(item, Menu):
            new_top = StackMenuItem(menu=item, page_index=0, parent=parent)
        elif isinstance(item, PageWidget):
            new_top = StackApplicationItem(application=item, parent=parent)
        else:
            msg = f'Unsupported type: {type(item)}'
            raise TypeError(msg)

        if isinstance(parent, StackMenuItem) and isinstance(new_top, StackMenuItem):
            parent.selection = StackMenuItemSelection(key=key or '', item=new_top)

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
        popping_item = self.top
        if not keep_subscriptions:
            popping_item.clear_subscriptions()
        if isinstance(popping_item, StackApplicationItem):
            popping_item.application.dispatch('on_close')
        if isinstance(popping_item.parent, StackMenuItem):
            popping_item.parent.selection = None

        *self.stack, _ = self.stack

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

    def _clear_menu_subscriptions(self: MenuWidget) -> None:
        """Clear widget subscriptions."""
        with self.menu_subscriptions_lock:
            subscriptions = self.menu_subscriptions.copy()
            self.menu_subscriptions.clear()
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
    current_menu_type: type[Menu] | None = AliasProperty(
        getter=lambda self: type(self.current_menu) if self.current_menu else None,
        bind=['current_menu'],
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

    def __repr__(self: MenuWidget) -> str:
        """Return a string representation of the widget."""
        return '\n'.join(self._visual_snapshot)


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('menu.kv').resolve().as_posix(),
)
