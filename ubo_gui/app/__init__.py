from __future__ import annotations

import pathlib
from functools import cached_property
from typing import TYPE_CHECKING, cast

from headless_kivy_pi import HeadlessWidget
from kivy.app import App, Builder, StringProperty, Widget
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.uix.label import Label

from ubo_gui import FONTS_PATH

LabelBase.register(
    name='material_symbols',
    fn_regular=FONTS_PATH.joinpath('MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].ttf')
    .resolve()
    .as_posix(),
)

if TYPE_CHECKING:
    from kivy.uix.boxlayout import BoxLayout


class RootWidget(HeadlessWidget):
    title = StringProperty('UBO', allownone=True)


class UboApp(App):
    def build(self: UboApp) -> Widget | None:
        """Build the app. This is the landing point for the app.

        The app can have a header, central section, and a footer.
        """
        self.root: RootWidget = cast(
            RootWidget,
            Builder.load_file(
                pathlib.Path(__file__).parent.joinpath('app.kv').resolve().as_posix(),
            ),
        )

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

        return self.root

    @cached_property
    def central(self: UboApp) -> Widget | None:
        return None

    @cached_property
    def header(self: UboApp) -> Widget | None:
        header_label = Label(text=self.root.title or '')

        def title_callback(_: RootWidget, title: str) -> None:
            header_layout: BoxLayout = self.root.ids.header_layout
            if title is not None:
                header_label.text = title
                header_layout.height = dp(30)
            else:
                header_label.text = ''
                header_layout.height = 0

        self.root.bind(title=title_callback)

        return header_label

    @cached_property
    def footer(self: UboApp) -> Widget | None:
        return None
