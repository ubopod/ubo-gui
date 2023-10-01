"""Demo of ubo-menu widget."""
from __future__ import annotations

import os
from functools import cached_property
from threading import Thread
from typing import TYPE_CHECKING, Literal

from gauge import GaugeWidget
from headless_kivy_pi import setup_headless
from kivy.base import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from volume import VolumeWidget

os.environ['KIVY_METRICS_DENSITY'] = '1'
os.environ['KIVY_NO_CONFIG'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

setup_headless()

from app import UboApp  # noqa: E402
from kivy.core.window import (  # noqa: E402
    Keyboard,
    Window,
    WindowBase,
)
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
    def menu_widget(self: MenuApp) -> MenuWidget:
        """Build the main menu and initiate it."""
        menu_widget = MenuWidget()
        menu_widget.set_current_menu(HOME_MENU)

        def title_callback(_: MenuWidget, title: str):
            self.root.title = title
        self.root.title = menu_widget.title
        menu_widget.bind(title=title_callback)

        return menu_widget

    @cached_property
    def cpu_gauge(self: MenuApp) -> GaugeWidget:
        import psutil
        gauge = GaugeWidget(value=0, fill_color='#24D636', label='CPU')

        value = [0]

        def set_value(_dt: float):
            gauge.value = value[0]

        def calculate_value():
            value[0] = psutil.cpu_percent(interval=1, percpu=False)
            Clock.schedule_once(set_value)

        Clock.schedule_interval(
            lambda _dt: Thread(target=calculate_value).start(),
            1,
        )

        return gauge

    @cached_property
    def ram_gauge(self: MenuApp) -> GaugeWidget:
        import psutil
        gauge = GaugeWidget(
            value=psutil.virtual_memory().percent,
            fill_color='#D68F24',
            label='RAM',
        )

        def set_value(_dt: int):
            gauge.value = psutil.virtual_memory().percent

        Clock.schedule_interval(set_value, 1)

        return gauge

    @cached_property
    def central(self: MenuApp) -> Widget:
        horizontal_layout = BoxLayout()

        self.menu_widget.size_hint = (None, 1)
        horizontal_layout.add_widget(self.menu_widget)

        central_column = BoxLayout(
            orientation='vertical', spacing=24, padding=24)
        central_column.add_widget(self.cpu_gauge)
        central_column.add_widget(self.ram_gauge)
        central_column.size_hint = (1, 1)
        horizontal_layout.add_widget(central_column)

        right_column = BoxLayout(orientation='vertical')
        right_column.add_widget(VolumeWidget(value=40))
        right_column.size_hint = (None, 1)
        horizontal_layout.add_widget(right_column)

        def handle_depth_change(_instance: Widget, depth: int):
            if depth == 0:
                self.menu_widget.size_hint = (None, 1)
                self.menu_widget.width = 100
                central_column.size_hint = (1, 1)
                right_column.size_hint = (None, 1)
                horizontal_layout._trigger_layout()
            else:
                self.menu_widget.size_hint = (1, 1)
                central_column.size_hint = (0, 1)
                right_column.size_hint = (0, 1)
                horizontal_layout._trigger_layout()

        self.menu_widget.bind(depth=handle_depth_change)

        return horizontal_layout

    @cached_property
    def footer(self: MenuApp) -> Widget:
        layout = BoxLayout(orientation='horizontal')
        [layout.add_widget(Label(
            text=icon,
            font_name='material_symbols',
            font_size=36,
            font_features='fill=1',
        )) for icon in ['camera', 'lan', 'mic_off', 'bluetooth', 'wifi_off']]
        layout.children[-1].color = 'green'
        return layout

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
                self.menu_widget.go_to_previous_page()
            elif key == Keyboard.keycodes['down']:
                self.menu_widget.go_to_next_page()
            elif key == Keyboard.keycodes['1']:
                self.menu_widget.select(0)
            elif key == Keyboard.keycodes['2']:
                self.menu_widget.select(1)
            elif key == Keyboard.keycodes['3']:
                self.menu_widget.select(2)
            elif key == Keyboard.keycodes['left']:
                self.menu_widget.go_back()


def main() -> None:
    """Instantiate the `MenuApp` and run it."""
    app = MenuApp()
    app.run()


if __name__ == '__main__':
    main()
