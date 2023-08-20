"""Demo of ubo-menu widget."""
from __future__ import annotations

import os
from functools import cached_property
from typing import TYPE_CHECKING, Literal

from headless_kivy_pi import setup_headless

setup_headless()

from app import UboApp  # noqa: E402

os.environ['KIVY_METRICS_DENSITY']= '1'
os.environ['KIVY_NO_CONFIG'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

from kivy.core.window import (  # noqa: E402
    Keyboard,
    Window,
    WindowBase,
)

from menu import MenuWidget  # noqa: E402

if TYPE_CHECKING:
    from menu import Menu
    Modifier = Literal['ctrl', 'alt', 'meta', 'shift']

MAIN_MENU: Menu = {
    'title': 'UBO',
    'heading': 'What are you going to do?',
    'sub_heading': 'Choose from the options',
    'items': [
        {
            'label': 'First Item',
            'icon': 'chevron-down',
            'sub_menu': {
                'title': 'Nested',
                'heading': 'Please choose',
                'sub_heading': 'This is sub heading',
                'items': [
                    {
                        'label': 'Nested item',
                        'action': lambda: print('Nested item selected'),
                    },
                ],
            },
        },
        {
            'label': 'Second Item',
            'color': (1, 0, 1, 1),
            'action': lambda: print('Second item selected'),
            'icon': 'chevron-up',
        },
        {
            'label': 'Third Item',
            'action': lambda: print('Third item selected'),
        },
        {
            'label': 'Fourth Item',
            'action': lambda: print('Fourth item selected'),
        },
        {
            'label': 'Fifth Item',
            'action': lambda: print('Fifth item selected'),
        },
    ],
}


class MenuApp(UboApp):
    """Menu application."""

    @cached_property
    def central(self: MenuApp):
        """Build the app and initiate."""
        Window.bind(on_keyboard=self.on_keyboard)
        root = MenuWidget()
        root.set_current_menu(MAIN_MENU)
        return root

    def on_keyboard(
        self: MenuApp,
        _: WindowBase,
        key: int,
        _scancode: int,
        _codepoint: str,
        modifier: list[Modifier],
    ) -> None:
        """Handle keyboard events."""
        if modifier == []:
            if key == Keyboard.keycodes['up']:
                self.root.title = '123'
                self.central.go_to_previous_page()
            elif key == Keyboard.keycodes['down']:
                self.central.go_to_next_page()
            elif key == Keyboard.keycodes['1']:
                self.central.select(0)
            elif key == Keyboard.keycodes['2']:
                self.central.select(1)
            elif key == Keyboard.keycodes['3']:
                self.central.select(2)
            elif key == Keyboard.keycodes['left']:
                self.central.go_back()


def main() -> None:
    """Instantiate the `MenuApp` and run it."""
    app = MenuApp()
    app.run()


if __name__ == '__main__':
    main()
