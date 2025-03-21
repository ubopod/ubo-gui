"""Utility functions for the menu widget."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
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
    return callable(value) and hasattr(value, 'subscribe')


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
