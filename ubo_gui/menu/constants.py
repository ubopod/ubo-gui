"""Module for defining constants used in the `Menu` widget."""

from kivy.lang.builder import Builder

from ubo_gui.page import PAGE_MAX_ITEMS

PAGE_SIZE = PAGE_MAX_ITEMS
SHORT_WIDTH = 46
MENU_ITEM_HEIGHT = 52
MENU_ITEM_GAP = 7

Builder.load_string(
    f"""
#:set UBO_GUI_PAGE_SIZE {PAGE_SIZE}
#:set UBO_GUI_SHORT_WIDTH {SHORT_WIDTH}
#:set UBO_GUI_MENU_ITEM_HEIGHT {MENU_ITEM_HEIGHT}
#:set UBO_GUI_MENU_ITEM_GAP {MENU_ITEM_GAP}
""",
)
