"""Initializes the ubo_gui package and registers various widgets using Kivy Factory.

It also defines the paths for assets and fonts used by the package.
"""

from pathlib import Path

from kivy.factory import Factory

__import__('ubo_gui.constants')
__import__('ubo_gui.menu.constants')

ROOT_PATH = Path(__file__).parent
ASSETS_PATH = ROOT_PATH.joinpath('assets')
FONTS_PATH = ASSETS_PATH.joinpath('fonts')


Factory.register('AnimatedSlider', module='ubo_gui.animated_slider')
Factory.register('GaugeWidget', module='ubo_gui.gauge')
Factory.register('ItemWidget', module='ubo_gui.menu.widgets.item_widget')
Factory.register('MenuWidget', module='ubo_gui.menu')
Factory.register('NotificationWidget', module='ubo_gui.notification')
Factory.register('PromptWidget', module='ubo_gui.prompt')
Factory.register('QRCodeWidget', module='ubo_gui.qrcode')
Factory.register('VolumeWidget', module='ubo_gui.volume')
