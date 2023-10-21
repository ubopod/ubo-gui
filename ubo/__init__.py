from pathlib import Path

from kivy.factory import Factory

ROOT_PATH = Path(__file__).parent
ASSETS_PATH = ROOT_PATH.joinpath('assets')
FONTS_PATH = ASSETS_PATH.joinpath('fonts')


Factory.register('AnimatedSlider', module='ubo.animated_slider')
Factory.register('GaugeWidget', module='ubo.gauge')
Factory.register('ItemWidget', module='ubo.menu.item_widget')
Factory.register('MenuWidget', module='ubo.menu')
Factory.register('NotificationWidget', module='ubo.notification')
Factory.register('PromptWidget', module='ubo.prompt')
Factory.register('VolumeWidget', module='ubo.volume')
