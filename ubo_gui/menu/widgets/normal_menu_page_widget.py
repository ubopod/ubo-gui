"""Module for the `NormalMenuPageWidget` class."""

import pathlib

from kivy.lang.builder import Builder
from kivy.properties import StringProperty

from ubo_gui.page import PageWidget


class NormalMenuPageWidget(PageWidget):
    """renders a normal page of a `Menu`."""

    placeholder = StringProperty(allownone=True)


Builder.load_file(
    pathlib.Path(__file__)
    .parent.joinpath('normal_menu_page_widget.kv')
    .resolve()
    .as_posix(),
)
