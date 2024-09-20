"""Initializes the ubo_gui package and registers various widgets using Kivy Factory.

It also defines the paths for assets and fonts used by the package.
"""

from pathlib import Path

ROOT_PATH = Path(__file__).parent
ASSETS_PATH = ROOT_PATH.joinpath('assets')
FONTS_PATH = ASSETS_PATH.joinpath('fonts')


def setup() -> None:
    """Register various widgets using Kivy Factory and sets up the constants."""
    from kivy.factory import Factory
    from kivy.lang.builder import Builder

    from ubo_gui import constants
    from ubo_gui.menu import constants as menu_constants

    Builder.load_string(
        f"""
    #:set UBO_GUI_PRIMARY_COLOR '{constants.PRIMARY_COLOR}'
    #:set UBO_GUI_SECONDARY_COLOR '{constants.SECONDARY_COLOR}'
    #:set UBO_GUI_SECONDARY_COLOR_LIGHT '{constants.SECONDARY_COLOR_LIGHT}'
    #:set UBO_GUI_TEXT_COLOR '{constants.TEXT_COLOR}'

    #:set UBO_GUI_INFO_COLOR '{constants.INFO_COLOR}'
    #:set UBO_GUI_DANGER_COLOR '{constants.DANGER_COLOR}'
    #:set UBO_GUI_WARNING_COLOR '{constants.WARNING_COLOR}'
    #:set UBO_GUI_SUCCESS_COLOR '{constants.SUCCESS_COLOR}'

    #:set UBO_GUI_PAGE_SIZE {menu_constants.PAGE_SIZE}
    #:set UBO_GUI_SHORT_WIDTH {menu_constants.SHORT_WIDTH}
    #:set UBO_GUI_MENU_ITEM_HEIGHT {menu_constants.MENU_ITEM_HEIGHT}
    #:set UBO_GUI_MENU_ITEM_GAP {menu_constants.MENU_ITEM_GAP}
    """,
    )

    Factory.register('AnimatedSlider', module='ubo_gui.animated_slider')
    Factory.register('GaugeWidget', module='ubo_gui.gauge')
    Factory.register('ItemWidget', module='ubo_gui.menu.widgets.item_widget')
    Factory.register('MenuWidget', module='ubo_gui.menu')
    Factory.register('NotificationWidget', module='ubo_gui.notification')
    Factory.register('ProgressRingWidget', module='ubo_gui.progress_ring')
    Factory.register('PromptWidget', module='ubo_gui.prompt')
    Factory.register('QRCodeWidget', module='ubo_gui.qrcode')
    Factory.register('VolumeWidget', module='ubo_gui.volume')
