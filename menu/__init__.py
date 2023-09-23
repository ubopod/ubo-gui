"""Implement a paginated menu.

The first page starts with a heading and its sub-heading.
Each item may have sub items, in that case activating this item will open a new menu
with its sub items.
Each item can optionally be styled differently.
"""
from __future__ import annotations

import pathlib
import warnings
from typing import TYPE_CHECKING

from headless_kivy_pi import HeadlessWidget
from kivy.app import Builder
from kivy.core.window import StringProperty
from kivy.uix.screenmanager import ScreenManager

from menu.item_widget import ItemWidget  # noqa: F401
from menu.types import is_action_item, is_sub_menu_item
from page import PageWidget

if TYPE_CHECKING:
    from collections.abc import Iterator

    from typing_extensions import Any

    from menu.types import Item, Menu


PAGE_SIZE = 3


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
    for i in range(PAGE_SIZE-offset, len(items), PAGE_SIZE):
        yield items[i:i + PAGE_SIZE]


class NormalMenuPageWidget(PageWidget):
    """renders a normal page of a `Menu`."""


class HeaderMenuPageWidget(PageWidget):
    """renders a header page of a `Menu`."""

    heading = StringProperty()
    sub_heading = StringProperty()

    def __init__(
        self: HeaderMenuPageWidget,
        item: Item,
        heading: str,
        sub_heading: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Initialize a `MenuWidget`.

        Parameters
        ----------
        items: `list` of `Item`
            The items to be shown in this page

        heading: `str`
            The heading of the page

        sub_heading: `str`
            The sub-heading of the page

        kwargs: Any
            Stuff that will get directly passed to the `__init__` method of Kivy's
        `Screen`.
        """
        super().__init__([item], **kwargs)
        self.heading = heading
        self.sub_heading = sub_heading

    def get_item(self: HeaderMenuPageWidget, index: int) -> Item | None:
        if index != PAGE_SIZE - 1:
            warnings.warn('index must be 2', ResourceWarning, stacklevel=1)
            return None
        return self.items[index - 2]


class MenuWidget(ScreenManager):
    """Paginated menu."""

    page_index: int = 0
    pages: list[PageWidget]
    current_menu: Menu
    menu_stack: list[Menu]

    def __init__(self: MenuWidget, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize a `MainWidget`."""
        self.pages = []
        self.menu_stack = []
        super().__init__(**kwargs)
        HeadlessWidget.activate_low_fps_mode()

    def go_to_next_page(self: MenuWidget) -> None:
        """Go to the next page.

        If it is already the last page, rotate to the first page.
        """
        if len(self.current_menu['items']) == 0:
            return
        self.page_index += 1
        if self.page_index >= len(self.pages):
            self.page_index = 0
        self.transition.direction = 'up'
        self.update()

    def go_to_previous_page(self: MenuWidget) -> None:
        """Go to the previous page.

        If it is already the first page, rotate to the last page.
        """
        if len(self.current_menu['items']) == 0:
            return
        self.page_index -= 1
        if self.page_index < 0:
            self.page_index = len(self.pages) - 1
        self.transition.direction = 'down'
        self.update()

    def select(self: MenuWidget, index: int) -> None:
        """Select one of the items currently visible on the screen.

        Parameters
        ----------
        index: `int`
            An integer number, can only take values greater than or equal to zero and
            less than `PAGE_SIZE`
        """
        current_page: PageWidget = self.current_screen
        item = current_page.get_item(index)
        if not item:
            return
        if is_action_item(item):
            item['action']()
        if is_sub_menu_item(item):
            self.push_menu(item['sub_menu'])

    def go_back(self: MenuWidget) -> None:
        """Go back to the previous menu."""
        self.pop_menu()

    def update(self: MenuWidget) -> None:
        """Activate the transition from the previously active page to the current page.

        Activate high fps mode to render the animation in high fps
        """
        HeadlessWidget.activate_high_fps_mode()
        self.current = f'Page {self.page_index}'

    def push_menu(self: MenuWidget, menu: Menu) -> None:
        """Go one level deeper in the menu stack."""
        self.menu_stack.append(self.current_menu)
        self.set_current_menu(menu)

    def pop_menu(self: MenuWidget) -> None:
        """Come up one level from of the menu stack."""
        if len(self.menu_stack) == 0:
            return
        self.set_current_menu(self.menu_stack.pop())

    def set_current_menu(self: MenuWidget, menu: Menu) -> None:
        """Set the `current_menu` and create its pages."""
        HeadlessWidget.activate_high_fps_mode()
        while len(self.pages) > 0:
            self.remove_widget(self.pages.pop())
        self.current_menu = menu
        if 'heading' in self.current_menu:
            first_page = HeaderMenuPageWidget(
                menu['items'][0],
                menu['heading'],
                menu['sub_heading'],
                name='Page 0',
            )
        else:
            first_page = NormalMenuPageWidget(menu['items'][:3], name='Page 0')
        self.pages.append(first_page)
        self.add_widget(first_page)

        paginated_items = paginate(
            menu['items'], 2 if 'heading' in menu else 0)
        for index, page_items in enumerate(paginated_items):
            page = NormalMenuPageWidget(page_items, name=f'Page {index + 1}')
            self.pages.append(page)
            self.add_widget(page)
        HeadlessWidget.activate_low_fps_mode()

    def on_kv_post(self: MenuWidget, _: Any) -> None:  # noqa: ANN401
        """Activate low fps mode when transition is done."""
        a = self.transition.on_progress

        def on_progress(progress):
            self.transition.screen_out.opacity = (1 - progress)
            self.transition.screen_in.opacity = progress
            a(progress)

        def on_complete():
            self.transition.screen_out.opacity = 0
            self.transition.screen_in.opacity = 1
            HeadlessWidget.activate_low_fps_mode()

        self.transition.on_progress = on_progress
        self.transition.on_complete = on_complete


Builder.load_file(pathlib.Path(
    __file__).parent.joinpath('menu.kv').resolve().as_posix())
