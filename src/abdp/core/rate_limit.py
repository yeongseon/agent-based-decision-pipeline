"""Fixed-window rate limiter contract:

- ``Clock`` is a callable that returns the current time as a finite real number.
- ``FixedWindowRateLimiter`` is a mutable, single-threaded fixed-window admission checker.
- Construction requires ``max_calls`` to be an ``int`` (not ``bool``) with ``max_calls >= 1``.
- Construction requires ``window_seconds`` to be a real number (not ``bool``) with
  ``window_seconds > 0`` and finite.
- Construction requires ``clock`` to be callable and does not call it.
- Windows are aligned to absolute clock boundaries with ``floor(now / window_seconds)``.
- Each window is half-open: ``[k * window_seconds, (k + 1) * window_seconds)``.
- ``allow()`` calls ``clock()`` exactly once per invocation.
- ``allow()`` returns ``True`` for the first ``max_calls`` admissions in the current window
  and ``False`` after the budget is exhausted.
- Calls that return ``False`` do not consume budget.
- At ``now == window_end``, ``allow()`` evaluates against the next window.
- If ``clock()`` returns a non-real or non-finite value, ``allow()`` raises a stable public error.
- If ``clock()`` returns a value smaller than the previous observed value, ``allow()`` raises
  ``RuntimeError("clock must be monotonic non-decreasing")`` and leaves the limiter state unchanged.
- No thread-safety, async, or distributed-coordination guarantees are provided.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from numbers import Real
from typing import Final

__all__ = ["Clock", "FixedWindowRateLimiter"]

type Clock = Callable[[], float]

_MIN_MAX_CALLS: Final[int] = 1


def _validate_max_calls(max_calls: int) -> None:
    if isinstance(max_calls, bool) or not isinstance(max_calls, int):
        raise TypeError(f"max_calls must be an int, got {type(max_calls).__name__}")
    if max_calls < _MIN_MAX_CALLS:
        raise ValueError(f"max_calls must be at least 1, got {max_calls}")


def _validate_window_seconds(window_seconds: float) -> None:
    if isinstance(window_seconds, bool) or not isinstance(window_seconds, Real):
        raise TypeError(f"window_seconds must be a real number, got {type(window_seconds).__name__}")
    if not math.isfinite(window_seconds):
        raise ValueError(f"window_seconds must be finite, got {window_seconds}")
    if window_seconds <= 0:
        raise ValueError(f"window_seconds must be positive, got {window_seconds}")


def _validate_clock(clock: Clock) -> None:
    if not callable(clock):
        raise TypeError("clock must be callable")


def _validate_clock_reading(now: object) -> float:
    if isinstance(now, bool) or not isinstance(now, Real):
        raise TypeError(f"clock must return a real number, got {type(now).__name__}")
    value = float(now)
    if not math.isfinite(value):
        raise ValueError(f"clock must return a finite number, got {value}")
    return value


class FixedWindowRateLimiter:
    def __init__(
        self,
        *,
        max_calls: int,
        window_seconds: float,
        clock: Clock = time.monotonic,
    ) -> None:
        _validate_max_calls(max_calls)
        _validate_window_seconds(window_seconds)
        _validate_clock(clock)
        self._max_calls: Final[int] = max_calls
        self._window_seconds: Final[float] = float(window_seconds)
        self._clock: Final[Clock] = clock
        self._last_now: float | None = None
        self._window_index: int | None = None
        self._used_calls: int = 0

    def allow(self) -> bool:
        now = _validate_clock_reading(self._clock())
        if self._last_now is not None and now < self._last_now:
            raise RuntimeError("clock must be monotonic non-decreasing")
        index = math.floor(now / self._window_seconds)
        if self._window_index is None or index != self._window_index:
            self._window_index = index
            self._used_calls = 0
        self._last_now = now
        if self._used_calls < self._max_calls:
            self._used_calls += 1
            return True
        return False
