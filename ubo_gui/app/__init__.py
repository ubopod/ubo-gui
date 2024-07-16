"""The main module for the Ubo GUI."""

from __future__ import annotations

import pathlib
from functools import cached_property
from typing import TYPE_CHECKING, cast

from headless_kivy import HeadlessWidget
from kivy.app import App
from kivy.core.text import DEFAULT_FONT, LabelBase
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivy.uix.label import Label

from ubo_gui import FONTS_PATH

LabelBase.register(
    name=DEFAULT_FONT,
    fn_regular=FONTS_PATH.joinpath('ArimoNerdFont-Regular.ttf').resolve().as_posix(),
    fn_bold=FONTS_PATH.joinpath('ArimoNerdFont-Bold.ttf').resolve().as_posix(),
    fn_italic=FONTS_PATH.joinpath('ArimoNerdFont-Italic.ttf').resolve().as_posix(),
    fn_bolditalic=FONTS_PATH.joinpath('ArimoNerdFont-BoldItalic.ttf')
    .resolve()
    .as_posix(),
)

if TYPE_CHECKING:
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.widget import Widget


class RootWidget(HeadlessWidget):
    """The root widget for the `UboApp`."""

    title = StringProperty('UBO', allownone=True)


class UboApp(App):
    """The main app for the Ubo GUI."""

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
        """The central section of the app."""
        return None

    def title_callback(self: UboApp, _: RootWidget, title: str | None) -> None:
        """Update the header label when the title changes."""
        if not self:
            return
        header_layout: BoxLayout = self.root.ids.header_layout
        if title is None:
            self.header_label.text = ''
            header_layout.opacity = 0
        else:
            self.header_label.text = title
            header_layout.opacity = 1

    @cached_property
    def header(self: UboApp) -> Widget | None:
        """The header section of the app."""
        self.header_label = Label(text=self.root.title or '', markup=True)

        self.root.bind(title=self.title_callback)

        return self.header_label

    @cached_property
    def footer(self: UboApp) -> Widget | None:
        """The footer section of the app."""
        return None
