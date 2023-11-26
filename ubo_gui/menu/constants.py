from kivy.app import Builder


PAGE_SIZE = 3
SHORT_WIDTH = 46

Builder.load_string(
    f"""
#:set UBO_GUI_PAGE_SIZE '{PAGE_SIZE}'
#:set UBO_GUI_SHORT_WIDTH '{SHORT_WIDTH}'
""",
)
