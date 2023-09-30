"""Demo of ubo-menu widget."""
from __future__ import annotations

import os
from functools import cached_property
from typing import TYPE_CHECKING, Literal

from headless_kivy_pi import setup_headless

os.environ['KIVY_METRICS_DENSITY'] = '1'
os.environ['KIVY_NO_CONFIG'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

setup_headless()

from kivy.core.window import (  # noqa: E402
    Keyboard,
    Window,
    WindowBase,
)

from app import UboApp  # noqa: E402
from menu import MenuWidget  # noqa: E402

if TYPE_CHECKING:
    from kivy.app import Widget

    from menu import Menu
    from menu.types import Item
    Modifier = Literal['ctrl', 'alt', 'meta', 'shift']

SETTINGS_MENU: Menu = {
    'title': 'Settings',
    'heading': 'Please choose',
    'sub_heading': 'This is sub heading',
    'items': [
        {
            'label': 'WiFi',
            'action': lambda: print('WiFi'),
            'icon': 'wifi',
        },
        {
            'label': 'Bluetooth',
            'action': lambda: print('Bluetooth'),
            'icon': 'bluetooth',
        },
        {
            'label': 'Audio',
            'action': lambda: print('Audio'),
            'icon': 'volume_up',
        },
    ],
}

MAIN_MENU: Menu = {
    'title': 'Main',
    'heading': 'What are you going to do?',
    'sub_heading': 'Choose from the options',
    'items': [
        {
            'label': 'Settings',
            'icon': 'settings',
            'sub_menu': SETTINGS_MENU,
        },
        {
            'label': 'Apps',
            'action': lambda: print('Apps'),
            'icon': 'apps',
        },
        {
            'label': 'About',
            'action': lambda: print('About'),
            'icon': 'info',
        },
    ],
}


def notifications_menu_items() -> list[Item]:
    return []


HOME_MENU: Menu = {
    'title': 'Dashboard',
    'items': [
        {
            'label': '',
            'sub_menu': MAIN_MENU,
            'icon': 'menu',
            'is_short': True,
        },
        {
            'label': '',
            'sub_menu': {
                'title': 'Notifications',
                'items': notifications_menu_items,
            },
            'color': 'yellow',
            'icon': 'info',
            'is_short': True,
        },
        {
            'label': 'Turn off',
            'action': lambda: print('Turning off'),
            'icon': 'power_settings_new',
            'is_short': True,
        },
    ],
}


class MenuApp(UboApp):
    """Menu application."""

    def build(self: MenuApp) -> Widget | None:
        Window.bind(on_keyboard=self.on_keyboard)
        return super().build()

    @cached_property
    def central(self: MenuApp) -> MenuWidget:
        """Build the app and initiate."""
        menu_widget = MenuWidget()
        menu_widget.set_current_menu(HOME_MENU)

        def title_callback(_: MenuWidget, title: str):
            self.root.title = title
        menu_widget.bind(title=title_callback)
        return menu_widget

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
