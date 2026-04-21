"""Retry contract:

- ``retry`` applies deterministic retries to regular synchronous callables.
- ``on`` defines the only exception types that may be retried and must
  contain only ``Exception`` subclasses; ``BaseException`` subclasses such
  as ``KeyboardInterrupt`` and ``SystemExit`` are rejected so that process
  control signals are never swallowed by retry logic.
- ``max_attempts`` counts total invocations including the first call and
  must be at least 1.
- ``backoff(attempt)`` returns the delay in seconds after failed attempt
  ``attempt``, where ``attempt`` starts at 1.
- Delays are applied only between attempts; never before the first call
  and never after the final failure.
- ``sleep`` is injectable for tests and receives the computed delay
  verbatim. The default uses :func:`time.sleep`.
- Exceptions not matched by ``on`` propagate immediately without sleeping.
- When the final allowed attempt fails with a matched exception, that
  exception is re-raised unchanged.
- Async functions, async generator functions, and generator functions are
  rejected at decoration time so retries never wrap mere coroutine or
  iterator construction.
"""

from __future__ import annotations

import inspect
import time
from collections.abc import Callable
from functools import wraps
from typing import Final

__all__ = ["Backoff", "retry"]

type Backoff = Callable[[int], float]
type _Sleep = Callable[[float], None]

_DEFAULT_MAX_ATTEMPTS: Final = 3
_MIN_ATTEMPTS: Final = 1

_UNSUPPORTED_CALLABLE_KINDS: Final = (
    (inspect.isasyncgenfunction, "async generator function"),
    (inspect.iscoroutinefunction, "async function"),
    (inspect.isgeneratorfunction, "generator function"),
)


def _no_backoff(_attempt: int) -> float:
    return 0.0


def _validate_config(
    on: tuple[type[Exception], ...],
    max_attempts: int,
) -> None:
    if max_attempts < _MIN_ATTEMPTS:
        raise ValueError(f"max_attempts must be at least 1, got {max_attempts}")
    if not on:
        raise ValueError("on must contain at least one exception type")
    for entry in on:
        if not (isinstance(entry, type) and issubclass(entry, Exception)):
            name = entry.__name__ if isinstance(entry, type) else type(entry).__name__
            raise TypeError(f"on entries must be subclasses of Exception, got {name}")


def _reject_unsupported_callable(func: Callable[..., object]) -> None:
    for predicate, label in _UNSUPPORTED_CALLABLE_KINDS:
        if predicate(func):
            raise TypeError(f"retry only supports regular synchronous callables; got {label} {func.__name__!r}")


def retry[**P, R](
    *,
    on: tuple[type[Exception], ...],
    max_attempts: int = _DEFAULT_MAX_ATTEMPTS,
    backoff: Backoff = _no_backoff,
    sleep: _Sleep = time.sleep,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    _validate_config(on, max_attempts)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        _reject_unsupported_callable(func)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(1, max_attempts):
                try:
                    return func(*args, **kwargs)
                except on:
                    sleep(backoff(attempt))
            return func(*args, **kwargs)

        return wrapper

    return decorator
