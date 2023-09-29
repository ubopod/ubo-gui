from __future__ import annotations

import pathlib
from functools import cached_property
from typing import TYPE_CHECKING

from headless_kivy_pi import HeadlessWidget
from kivy.app import App, Builder, StringProperty, Widget
from kivy.core.text import LabelBase
from kivy.uix.label import Label

LabelBase.register(
    name='material_symbols',
    fn_regular=pathlib.Path(__file__).parent.parent.joinpath(
        'assets',
        'fonts',
        'MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].ttf',
    ).resolve().as_posix(),
)

if TYPE_CHECKING:
    from kivy.uix.layout import BoxLayout


class RootWidget(HeadlessWidget):
    title = StringProperty('UBO')


class UboApp(App):
    def build(self: UboApp) -> Widget | None:
        self.root: RootWidget = Builder.load_file(pathlib.Path(
            __file__).parent.joinpath('app.kv').resolve().as_posix())

        if self.root is None:
            return None

        central_layout: BoxLayout = self.root.ids.central_layout
        if self.central:
            central_layout.add_widget(self.central)

        header_layout: BoxLayout = self.root.ids.header_layout
        if self.header:
            header_layout.add_widget(self.header)

        footer_layout: BoxLayout = self.root.ids.footer_layout
        if self.footer:
            footer_layout.add_widget(self.footer)

        def title_callback(_: RootWidget, title: str):
            if self.header is None:
                return
            self.header.text = title
        self.root.bind(title=title_callback)

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
