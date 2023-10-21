"""Demo of ubo-menu widget."""
from __future__ import annotations

import datetime
import os
from functools import cached_property
from threading import Thread
from typing import TYPE_CHECKING, Literal

from headless_kivy_pi import setup_headless
from kivy.app import Widget
from kivy.base import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from ubo.gauge import GaugeWidget
from ubo.keypad import ButtonName, ButtonStatus, Keypad
from ubo.volume import VolumeWidget

os.environ['KIVY_METRICS_DENSITY'] = '1'
os.environ['KIVY_NO_CONFIG'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

setup_headless()

from kivy.core.window import (  # noqa: E402
    Keyboard,
    Window,
    WindowBase,
)

from ubo.app import UboApp  # noqa: E402
from ubo.menu import MenuWidget  # noqa: E402
from ubo.notification import (  # noqa: E402
    Importance,
    notification_manager,
)
from ubo.prompt import PromptWidget  # noqa: E402

if TYPE_CHECKING:
    from menu import Menu
    Modifier = Literal['ctrl', 'alt', 'meta', 'shift']

notification_manager.notify(
    title='Low priority',
    content='Something happened but it is not important and this content is very long'
    'since we need a very long content to check the scrollability of the widget',
    importance=Importance.LOW,
    sender='demo',
)
notification_manager.notify(
    title='Medium priority',
    content='Something happened and it is somehow important',
    importance=Importance.MEDIUM,
    sender='demo',
)
notification_manager.notify(
    title='High priority',
    content='Something happened and it is important',
    importance=Importance.HIGH,
    sender='demo',
)
notification_manager.notify(
    title='Critical priority',
    content='Something happened and it is critically important',
    importance=Importance.CRITICAL,
    sender='demo',
)


class WifiPrompt(PromptWidget):
    icon = 'wifi_off'
    prompt = 'Not Connected'
    first_option_label = 'Add'
    first_option_icon = 'add'

    def first_option_callback(self: WifiPrompt):
        notification_manager.notify(
            title='Wifi added',
            content='This Wifi network has been added',
            icon='wifi',
            sender='Wifi',
        )

    second_option_label = 'Forget'
    second_option_icon = 'delete'

    def second_option_callback(self: WifiPrompt):
        notification_manager.notify(
            title='Wifi forgot',
            content='This Wifi network is forgotten',
            importance=Importance.CRITICAL,
            sender='Wifi',
        )


SETTINGS_MENU: Menu = {
    'title': 'Settings',
    'heading': 'Please choose',
    'sub_heading': 'This is sub heading',
    'items': [
        {
            'label': 'WiFi',
            'application': WifiPrompt,
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
                'title': lambda: f'Notifications ({notification_manager.unread_count})',
                'items': notification_manager.menu_items,
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


class MenuApp(UboApp, Keypad):
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

        def set_value(_dt: float) -> None:
            gauge.value = value[0]

        def calculate_value() -> None:
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

        def set_value(_dt: int) -> None:
            gauge.value = psutil.virtual_memory().percent

        Clock.schedule_interval(set_value, 1)

        return gauge

    @cached_property
    def clock_widget(self: MenuApp) -> Label:
        clock = Label(font_size=dp(20))
        local_timzone = datetime.datetime.now(
            datetime.timezone.utc).astimezone().tzinfo

        def now() -> datetime.datetime:
            return datetime.datetime.now(local_timzone)

        def set_value(_dt: int) -> None:
            clock.text = now().strftime('%H:%M')

        set_value(0)

        def initialize(_dt: int) -> None:
            Clock.schedule_interval(set_value, 60)

        Clock.schedule_once(initialize, 60 - now().second + 1)

        return clock

    @cached_property
    def central(self: MenuApp) -> Widget:
        horizontal_layout = BoxLayout()

        self.menu_widget.size_hint = (None, 1)
        self.menu_widget.width = dp(50)
        horizontal_layout.add_widget(self.menu_widget)

        central_column = BoxLayout(
            orientation='vertical', spacing=dp(12), padding=dp(16))
        central_column.add_widget(self.cpu_gauge)
        central_column.add_widget(self.ram_gauge)
        central_column.size_hint = (1, 1)
        horizontal_layout.add_widget(central_column)

        right_column = BoxLayout(orientation='vertical')
        right_column.add_widget(VolumeWidget(value=40))
        right_column.size_hint = (None, 1)
        horizontal_layout.add_widget(right_column)

        def handle_depth_change(_instance: Widget, depth: int) -> None:
            if depth == 0:
                self.menu_widget.size_hint = (None, 1)
                self.menu_widget.width = dp(50)
                central_column.size_hint = (1, 1)
                right_column.size_hint = (None, 1)
            else:
                self.menu_widget.size_hint = (1, 1)
                central_column.size_hint = (0, 1)
                right_column.size_hint = (0, 1)

        self.menu_widget.bind(depth=handle_depth_change)

        return horizontal_layout

    @cached_property
    def footer(self: MenuApp) -> Widget:
        layout = BoxLayout()

        normal_footer_layout = BoxLayout(
            orientation='horizontal', spacing=0, padding=0)
        normal_footer_layout.add_widget(Label(
            text='reply',
            font_name='material_symbols',
            font_size=dp(20),
            font_features='fill=1',
            size_hint=(None, 1),
        ))
        normal_footer_layout.add_widget(Widget(size_hint=(1, 1)))

        home_footer_layout = BoxLayout(
            orientation='horizontal', spacing=0, padding=0)
        home_footer_layout.add_widget(
            Widget(size_hint=(None, 1), width=dp(16)))
        home_footer_layout.add_widget(self.clock_widget)
        home_footer_layout.add_widget(Widget(size_hint=(1, 1)))

        for icon in ['camera', 'lan', 'mic_off', 'bluetooth', 'wifi_off']:
            label = Label(
                text=icon,
                font_name='material_symbols',
                font_size=dp(20),
                font_features='fill=1',
                size_hint=(.5, 1),
            )
            home_footer_layout.add_widget(label)
            if icon == 'camera':
                label.color = 'green'

        home_footer_layout.add_widget(
            Widget(size_hint=(None, 1), width=dp(16)))

        def handle_depth_change(_instance: Widget, depth: int) -> None:
            if depth == 0:
                if normal_footer_layout in layout.children:
                    layout.remove_widget(normal_footer_layout)
                    layout.add_widget(home_footer_layout)
            elif home_footer_layout in layout.children:
                layout.remove_widget(home_footer_layout)
                layout.add_widget(normal_footer_layout)

        self.menu_widget.bind(depth=handle_depth_change)

        layout.add_widget(home_footer_layout)

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

    def on_button_event(
        self: MenuApp,
        button_pressed: ButtonName,
        button_status: ButtonStatus,
    ) -> None:
        if button_status == 'pressed':
            if button_pressed == ButtonName.UP:
                Clock.schedule_once(
                    lambda dt: self.menu_widget.go_to_previous_page(), -1)
            elif button_pressed == ButtonName.DOWN:
                Clock.schedule_once(
                    lambda dt: self.menu_widget.go_to_next_page(), -1)
            elif button_pressed == ButtonName.TOP_LEFT:
                Clock.schedule_once(lambda dt: self.menu_widget.select(0), -1)
            elif button_pressed == ButtonName.MIDDLE_LEFT:
                Clock.schedule_once(lambda dt: self.menu_widget.select(1), -1)
            elif button_pressed == ButtonName.BOTTOM_LEFT:
                Clock.schedule_once(lambda dt: self.menu_widget.select(2), -1)
            elif button_pressed == ButtonName.BACK:
                Clock.schedule_once(lambda dt: self.menu_widget.go_back(), -1)
        self.root.reset_fps_control_queue()


def main() -> None:
    """Instantiate the `MenuApp` and run it."""
    app = MenuApp()
    app.run()


if __name__ == '__main__':
    main()
