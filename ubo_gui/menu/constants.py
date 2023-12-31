from kivy.app import Builder

from ubo_gui.page import PAGE_MAX_ITEMS

PAGE_SIZE = PAGE_MAX_ITEMS
SHORT_WIDTH = 46

Builder.load_string(
    f"""
#:set UBO_GUI_PAGE_SIZE '{PAGE_SIZE}'
#:set UBO_GUI_SHORT_WIDTH '{SHORT_WIDTH}'
""",
)
