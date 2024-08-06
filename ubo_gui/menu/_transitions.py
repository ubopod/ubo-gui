"""Provides easy access to different transitions."""

from __future__ import annotations

import threading
from functools import cached_property
from typing import Any, NotRequired, TypedDict

from headless_kivy import HeadlessWidget
from kivy.clock import mainthread
from kivy.uix.screenmanager import (
    NoTransition,
    RiseInTransition,
    Screen,
    ScreenManager,
    SlideTransition,
    SwapTransition,
    TransitionBase,
)
from kivy.uix.widget import Widget


class SwitchParameters(TypedDict):
    """Parameters for switching screens."""

    duration: NotRequired[float | None]
    direction: NotRequired[str | None]


class TransitionsMixin:
    """Provides easy access to different transitions."""

    transition_queue: list[
        tuple[Screen | None, TransitionBase, str | None, float | None]
    ]
    screen_manager: ScreenManager
    _is_transition_in_progress: bool = False
    _is_preparation_in_progress: bool = False
    _transition_progress_lock: threading.Lock

    def __init__(self: TransitionsMixin, **kwargs: dict[str, Any]) -> None:
        """Initialize the transitions mixin."""
        _ = kwargs
        self._transition_progress_lock = threading.Lock()
        self.transition_queue = []

    def _handle_transition_progress(
        self: TransitionsMixin,
        transition: TransitionBase,
        progression: float,
    ) -> None:
        transition.screen_out.opacity = 1 - progression
        transition.screen_in.opacity = progression

    def _handle_transition_complete(
        self: TransitionsMixin,
        transition: TransitionBase,
    ) -> None:
        transition.screen_out.opacity = 0
        transition.screen_in.opacity = 1
        with self._transition_progress_lock:
            if self.transition_queue:
                (
                    (screen, transition, direction, duration),
                    *self.transition_queue,
                ) = self.transition_queue
                if (
                    len(self.transition_queue) > 1
                    and transition is not self._no_transition
                ):
                    duration = 0.08
                switch_parameters: SwitchParameters = {}
                if duration is not None:
                    switch_parameters['duration'] = duration
                if direction is not None:
                    switch_parameters['direction'] = direction
                self._perform_switch(
                    screen,
                    transition=transition,
                    **switch_parameters,
                )
            else:
                if isinstance(self, Widget):
                    headless_widget = HeadlessWidget.get_instance(self)
                    if headless_widget:
                        headless_widget.activate_low_fps_mode()
                self._is_transition_in_progress = False

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
    def _rise_in_transition(self: TransitionsMixin) -> RiseInTransition:
        transition = RiseInTransition()
        self._setup_transition(transition)
        return transition

    @cached_property
    def _swap_transition(self: TransitionsMixin) -> SwapTransition:
        transition = SwapTransition()
        self._setup_transition(transition)
        return transition

    @mainthread
    def _perform_switch(
        self: TransitionsMixin,
        screen: Screen | None,
        /,
        *,
        transition: TransitionBase,
        duration: float | None = None,
        direction: str | None = None,
    ) -> None:
        if duration is None:
            duration = 0.2
        self.screen_manager.switch_to(
            screen,
            transition=transition,
            duration=duration,
            **({} if direction is None else {'direction': direction}),
        )
        self._is_preparation_in_progress = False

    def _switch_to(
        self: TransitionsMixin,
        screen: Screen | None,
        /,
        *,
        transition: TransitionBase,
        duration: float | None = None,
        direction: str | None = None,
    ) -> None:
        """Switch to a new screen."""
        if screen is self.screen_manager.current_screen:
            return
        if duration is None:
            duration = 0 if transition is self._no_transition else 0.3
        with self._transition_progress_lock:
            if self._is_transition_in_progress:
                self.transition_queue = [
                    *self.transition_queue,
                    (screen, transition, direction, duration),
                ]
            else:
                if isinstance(self, Widget):
                    headless_widget = HeadlessWidget.get_instance(self)
                    if headless_widget:
                        headless_widget.activate_high_fps_mode()
                self._is_transition_in_progress = transition is not self._no_transition
                self._is_preparation_in_progress = True
                self._perform_switch(
                    screen,
                    transition=transition,
                    duration=duration,
                    direction=direction,
                )
