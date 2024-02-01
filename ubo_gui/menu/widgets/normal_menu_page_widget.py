"""Module for the `NormalMenuPageWidget` class."""
import pathlib

from kivy.app import Builder

from ubo_gui.page import PageWidget


class NormalMenuPageWidget(PageWidget):
    """renders a normal page of a `Menu`."""


Builder.load_file(
    pathlib.Path(__file__)
    .parent.joinpath('normal_menu_page_widget.kv')
    .resolve()
    .as_posix(),
)
