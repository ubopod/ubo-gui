from __future__ import annotations

from kivy.animation import Animation
from kivy.properties import NumericProperty
from kivy.uix.slider import Slider


class AnimatedSlider(Slider):
    animated_value = NumericProperty(0)

    def __init__(self, **kwargs):
        self.value = self.animated_value
        super().__init__(**kwargs)

    def on_animated_value(
        self: AnimatedSlider,
        instance: AnimatedSlider,
        new_value: float,
    ):
        Animation(value=new_value, duration=0.2).start(self)
