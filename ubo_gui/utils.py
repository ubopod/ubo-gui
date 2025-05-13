"""Utility functions for the menu widget."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    ParamSpec,
    Protocol,
    TypeGuard,
    cast,
    overload,
)

from typing_extensions import TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar('T', infer_variance=True)


class Subscribable(Protocol, Generic[T]):
    """A callable that can be subscribed to."""

    def subscribe(
        self: Subscribable,
        callback: Callable[[T], Any],
    ) -> Callable[[], None]:
        """Subscribe to the changes."""
        ...


def is_subscribeable(value: T | Callable[[], T]) -> TypeGuard[Subscribable[T]]:
    """Check if the value is subscribable."""
    return hasattr(value, 'subscribe')


@overload
def process_subscribable_value(
    value: T | Callable[[], T],
    callback: Callable[[T], None],
) -> Callable[[], None] | None: ...
@overload
def process_subscribable_value(
    value: T | None | Callable[[], T | None],
    callback: Callable[[T | None], None],
) -> Callable[[], None] | None: ...
def process_subscribable_value(
    value: T | None | Callable[[], T],
    callback: Callable[[T], None],
) -> Callable[[], None] | None:
    """Return the attribute of the menu or item.

    in case it's a function, the return value of the function is called.
    """
    if is_subscribeable(value):
        return cast('Subscribable[T]', value).subscribe(callback)
    processed_value = cast(
        'T',
        value() if callable(value) and not isinstance(value, type) else value,
    )
    callback(processed_value)
    return None


_Args = ParamSpec('_Args')
_ReturnType = TypeVar('_ReturnType')


def mainthread_if_needed(
    func: Callable[_Args, _ReturnType],
) -> Callable[_Args, _ReturnType]:
    """Run the function in the main thread if it's not already."""
    import inspect
    import threading

    from kivy.clock import mainthread

    def func_(*args: _Args.args, **kwargs: _Args.kwargs) -> _ReturnType:
        if threading.current_thread() is threading.main_thread():
            return func(*args, **kwargs)
        return mainthread(func)(*args, **kwargs)

    func_.__signature__ = inspect.signature(func)  # pyright: ignore [reportFunctionMemberAccess]
    func_.__name__ = func.__name__
    func_.__doc__ = func.__doc__
    func_.__qualname__ = func.__qualname__
    func_.__dict__.update(func.__dict__)

    return func_
