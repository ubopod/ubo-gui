"""Demo of ubo-menu widget."""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Literal

from headless_kivy_pi import setup_headless

setup_headless()

os.environ['KIVY_METRICS_DENSITY']= '1'
os.environ['KIVY_NO_CONFIG'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

from .menu import MainWidget  # noqa: E402, I001
from kivy.app import App  # noqa: E402
from kivy.core.window import (  # noqa: E402
    Keyboard,
    Window,
    WindowBase,
)

if TYPE_CHECKING:
    from .menu import Menu
    Modifier = Literal['ctrl', 'alt', 'meta', 'shift']

MAIN_MENU: Menu = {
    'title': 'Hello world',
    'heading': 'Please choose an item',
    'sub_heading': 'This is sub heading',
    'items': [
        {
            'label': 'First Item',
            'sub_menu': {
                'title': 'Sub menu',
                'heading': 'Please choose an item',
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
        },
        {
            'label': 'Third Item',
            'action': lambda: print('Third item selected'),
        },
        {
            'label': 'Fourth Item',
            'action': lambda: print('Fourth item selected'),
        },
    ],
}


class MenuApp(App):
    """Menu application."""

    root: MainWidget

    def build(self: MenuApp) -> MainWidget:
        """Build the app and initiate."""
        Window.bind(on_keyboard=self.on_keyboard)
        root = MainWidget()
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
                self.root.go_to_previous_page()
            elif key == Keyboard.keycodes['down']:
                self.root.go_to_next_page()
            elif key == Keyboard.keycodes['1']:
                self.root.select(0)
            elif key == Keyboard.keycodes['2']:
                self.root.select(1)
            elif key == Keyboard.keycodes['3']:
                self.root.select(2)
            elif key == Keyboard.keycodes['left']:
                self.root.go_back()


def main() -> None:
    """Instantiate the `MenuApp` and run it."""
    app = MenuApp()
    app.run()


if __name__ == '__main__':
    main()
