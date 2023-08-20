"""Implement a paginated menu.

The first page starts with a heading and its sub-heading.
Each item may have sub items, in that case activating this item will open a new menu
with its sub items.
Each item can optionally be styled differently.
"""
from __future__ import annotations

import pathlib
import warnings
from typing import TYPE_CHECKING, Union

from headless_kivy_pi import HeadlessWidget
from kivy.app import Builder, Widget
from kivy.core.window import ColorProperty, ListProperty, StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from typing_extensions import Any, NotRequired, TypedDict, TypeGuard

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


class Menu(TypedDict):
    """A class used to represent a menu.

    Attributes
    ----------
    title: str
        Rendered on top of the menu in all pages.

    heading: str
        Rendered in the first page of the menu, stating the purpose of the menu and its
    items.

    sub_heading: str
        Rendered beneath the heading in the first page of the menu with a smaller font.

    items: List[Item]
        List of the items of the menu
    """

    title: str
    heading: str
    sub_heading: str
    items: list[Item]


class BaseItem(TypedDict):
    """A class used to represent a menu item.

    Attributes
    ----------
    label: `str`
        The label of the item.

    color: `tuple` of `float`
        The color in rgba format as a list of floats, the list should contain 4
    elements: red, green, blue and alpha, each being a number in the range [0..1].
    For example (0.5, 0, 0.5, 0.8) represents a semi transparent purple.
    """

    label: str
    color: NotRequired[tuple[float, float, float, float]]
    icon: NotRequired[str]


class ActionItem(BaseItem):
    """A class used to represent an action menu item.

    Attributes
    ----------
    action: `Function`, optional
        If provided, activating this item will call this function.
    """

    action: Callable


def is_action_item(item: Item) -> TypeGuard[ActionItem]:
    """Check whether the item is an `ActionItem` or not."""
    return 'action' in item


class SubMenuItem(BaseItem):
    """A class used to represent a sub-menu menu item.

    Attributes
    ----------
    sub_menu: `Menu`, optional
        If provided, activating this item will open another menu, the description
        described in this field.
    """

    sub_menu: Menu


def is_sub_menu_item(item: Item) -> TypeGuard[SubMenuItem]:
    """Check whether the item is an `SubMenuItem` or not."""
    return 'sub_menu' in item


Item = Union[ActionItem, SubMenuItem]

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


class ItemWidget(Widget):
    """Renders an `Item`."""

    color = ColorProperty((1, 1, 1, 1))
    label = StringProperty()
    sub_menu = None


class PageWidget(Screen):
    """renders a page of a `Menu`."""

    items = ListProperty([])

    def __init__(
        self: PageWidget,
        items: list[Item],
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Initialize a `MenuWidget`.

        Parameters
        ----------
        items: `list` of `Item`
            The items to be shown in this page

        kwargs: Any
            Stuff that will get directly passed to the `__init__` method of Kivy's
        `Screen`.
        """
        super().__init__(**kwargs)
        self.items = items

    def get_item(self: PageWidget, index: int) -> Item | None:
        if not 0 <= index < len(self.items):
            msg = f"""index must be greater than or equal to 0 and less than {
            len(self.items)}"""
            warnings.warn(msg, ResourceWarning, stacklevel=1)
            return None
        return self.items[index]


class NormalPageWidget(PageWidget):
    """renders a normal page of a `Menu`."""


class HeaderPageWidget(PageWidget):
    """renders a header page of a `Menu`."""

    heading = StringProperty()
    sub_heading = StringProperty()

    def __init__(
        self: HeaderPageWidget,
        items: list[Item],
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
        super().__init__(items, **kwargs)
        self.heading = heading
        self.sub_heading = sub_heading

    def get_item(self: HeaderPageWidget, index: int) -> Item | None:
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
        if self.current_menu['heading']:
            first_page = HeaderPageWidget(
                menu['items'],
                menu['heading'],
                menu['sub_heading'],
                name='Page 0',
            )
        else:
            first_page = NormalPageWidget(menu['items'], name='Page 0')
        self.pages.append(first_page)
        self.add_widget(first_page)

        paginated_items = paginate(
            menu['items'], 2 if menu['heading'] else 0)
        for index, page_items in enumerate(paginated_items):
            page = NormalPageWidget(page_items, name=f'Page {index + 1}')
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
    __file__).parent.joinpath('menu.kv').as_posix())
