from __future__ import annotations

import pathlib
from functools import cached_property
from typing import TYPE_CHECKING

from headless_kivy_pi import HeadlessWidget
from kivy.app import App, Builder, StringProperty, Widget
from kivy.uix.label import Label

if TYPE_CHECKING:
    from kivy.uix.layout import BoxLayout


class RootWidget(HeadlessWidget):
    title = StringProperty('UBO')


class UboApp(App):
    def build(self: UboApp) -> Widget | None:
        self.root: RootWidget = Builder.load_file(pathlib.Path(
            __file__).parent.joinpath('app.kv').as_posix())

        central_layout: BoxLayout = self.root.ids.central_layout
        if self.central:
            central_layout.add_widget(self.central)

        header_layout: BoxLayout = self.root.ids.header_layout
        if self.header:
            header_layout.add_widget(self.header)

        footer_layout: BoxLayout = self.root.ids.footer_layout
        if self.footer:
            footer_layout.add_widget(self.footer)

        return self.root

    @cached_property
    def central(self: UboApp) -> Widget | None:
        return None

    @cached_property
    def header(self: UboApp) -> Widget | None:
        return Label(text=self.root.title)

    @cached_property
    def footer(self: UboApp) -> Widget | None:
        return None
