"""Module for the `AnimatedSlider` class."""

from __future__ import annotations

import pathlib

from kivy.animation import Animation
from kivy.lang.builder import Builder
from kivy.properties import AliasProperty
from kivy.uix.slider import Slider


class AnimatedSlider(Slider):
    """A slider that moves up and down when its value is changed."""

    def set_animated_value(self: AnimatedSlider, value: float) -> bool:
        """Set the value of the `animated_value` property.

        Animates the slider moving to the new value.

        Arguments:
        ---------
        value: The new value that the `animated_value` property is being set to.

        """
        self._animated_value = max(self.min, min(value, self.max))
        Animation(value=self._animated_value, duration=0.2).start(self)
        return True

    def get_animated_value(self: AnimatedSlider) -> float:
        """Return the value of the `animated_value` property.

        Returns
        -------
            The value of the `animated_value` property.

        """
        return self._animated_value

    _animated_value = 0
    animated_value = AliasProperty(
        setter=set_animated_value,
        getter=get_animated_value,
    )

    def __init__(self: AnimatedSlider, **kwargs: object) -> None:
        """Initialize the `AnimatedSlider` class."""
        super().__init__(**kwargs)
        self.value = self.animated_value


Builder.load_file(
    pathlib.Path(__file__).parent.joinpath('animated_slider.kv').resolve().as_posix(),
)
