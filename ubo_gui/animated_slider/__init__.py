"""Module for the `AnimatedSlider` class."""

from __future__ import annotations

from kivy.animation import Animation
from kivy.properties import BoundedNumericProperty
from kivy.uix.slider import Slider


class AnimatedSlider(Slider):
    """A slider that moves up and down when its value is changed."""

    animated_value = BoundedNumericProperty(0)

    def animated_value_error_handler(self: AnimatedSlider, value: float) -> float:
        """Handle error for the `animated_value` property's `errorhandler` argument.

        This method is called when the `animated_value` property is set to a
        value outside of its `min` and `max` bounds.
        This method returns the value that the `animated_value` property should be
        set to, instead of the value that was passed to it.
        """
        if value < self.min:
            return self.min
        if value > self.max:
            return self.max
        return 0

    def __init__(self: AnimatedSlider, **kwargs: object) -> None:
        """Initialize the `AnimatedSlider` class."""
        super().__init__(**kwargs)
        self.value = self.animated_value
        self.padding = 0
        self.property('animated_value').__init__(
            0,
            min=self.min,
            max=self.max,
            errorhandler=self.animated_value_error_handler,
        )

    def on_min(self: AnimatedSlider, *largs: float) -> None:
        """Handle the `min` property being set to a new value."""
        value = largs[1]
        self.property('animated_value').set_min(self, value)

    def on_max(self: AnimatedSlider, *largs: float) -> None:
        """Handle the `max` property being set to a new value."""
        value = largs[1]
        self.property('animated_value').set_max(self, value)

    def on_animated_value(
        self: AnimatedSlider,
        _: AnimatedSlider,
        new_value: float,
    ) -> None:
        """Handle the `animated_value` property being set to a new value.

        Animates the slider moving to the new value.

        Arguments:
        ---------
            new_value: The new value that the `animated_value` property is being set to.

        """
        Animation(value=new_value, duration=0.2).start(self)
