"""Module to store constants used in the application."""
from kivy.lang.builder import Builder

PRIMARY_COLOR = '#68B7FF'
SECONDARY_COLOR = '#363F4B'
TEXT_COLOR = '#FFFFFF'

DANGER_COLOR = '#FF3F51'
SUCCESS_COLOR = '#03F7AE'

Builder.load_string(
    f"""
#:set UBO_GUI_PRIMARY_COLOR '{PRIMARY_COLOR}'
#:set UBO_GUI_SECONDARY_COLOR '{SECONDARY_COLOR}'
#:set UBO_GUI_TEXT_COLOR '{TEXT_COLOR}'
#:set UBO_GUI_DANGER_COLOR '{DANGER_COLOR}'
#:set UBO_GUI_SUCCESS_COLOR '{SUCCESS_COLOR}'
""",
)
