from __future__ import annotations

import pathlib

from kivy.app import Builder
from kivy.properties import ColorProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout


class Scrollbar(BoxLayout):
    pages = NumericProperty()
    current_page = NumericProperty()
    bar_color = ColorProperty('#ABA7A7')
    handle_color = ColorProperty('#D9D9D9')


Builder.load_file(pathlib.Path(
    __file__).parent.joinpath('scrollbar.kv').resolve().as_posix())
