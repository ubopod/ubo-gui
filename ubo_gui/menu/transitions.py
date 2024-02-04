"""Provides easy access to different transitions."""
from __future__ import annotations

from functools import cached_property

from headless_kivy_pi import HeadlessWidget
from kivy.uix.screenmanager import (
    NoTransition,
    SlideTransition,
    SwapTransition,
    TransitionBase,
)


class TransitionsMixin:
    """Provides easy access to different transitions."""

    def _handle_transition_progress(
        self: TransitionsMixin,
        transition: TransitionBase,
        progression: float,
    ) -> None:
        if progression is 0:  # noqa: F632 - float 0.0 is not accepted, we are looking for int 0
            HeadlessWidget.activate_high_fps_mode()
        transition.screen_out.opacity = 1 - progression
        transition.screen_in.opacity = progression

    def _handle_transition_complete(
        self: TransitionsMixin,
        transition: TransitionBase,
    ) -> None:
        transition.screen_out.opacity = 0
        transition.screen_in.opacity = 1
        HeadlessWidget.activate_low_fps_mode()

    def _setup_transition(self: TransitionsMixin, transition: TransitionBase) -> None:
        transition.bind(on_progress=self._handle_transition_progress)
        transition.bind(on_complete=self._handle_transition_complete)

    @cached_property
    def _no_transition(self: TransitionsMixin) -> NoTransition:
        transition = NoTransition()
        self._setup_transition(transition)
        return transition

    @cached_property
    def _slide_transition(self: TransitionsMixin) -> SlideTransition:
        transition = SlideTransition()
        self._setup_transition(transition)
        return transition

    @cached_property
    def _swap_transition(self: TransitionsMixin) -> SwapTransition:
        transition = SwapTransition()
        self._setup_transition(transition)
        return transition
