from __future__ import annotations

from kivy.animation import Animation
from kivy.properties import BoundedNumericProperty
from kivy.uix.slider import Slider


class AnimatedSlider(Slider):
    animated_value = BoundedNumericProperty(0)

    def animated_value_error_handler(self, value):
        if value < self.min:
            return self.min
        if value > self.max:
            return self.max
        return 0

    def __init__(self, **kwargs):
        self.value = self.animated_value
        self.padding = 0
        super().__init__(**kwargs)
        self.property('animated_value').__init__(
            0,
            min=self.min,
            max=self.max,
            errorhandler=self.animated_value_error_handler,
        )

    def on_min(self: AnimatedSlider, _instance: AnimatedSlider, value: float):
        self.property('animated_value').set_min(self, value)

    def on_max(self: AnimatedSlider, _instance: AnimatedSlider, value: float):
        self.property('animated_value').set_max(self, value)

    def on_animated_value(
        self: AnimatedSlider,
        instance: AnimatedSlider,
        new_value: float,
    ):
        Animation(value=new_value, duration=0.2).start(self)
