"""Tests for the fixed-window rate limiter (#23)."""

from __future__ import annotations

import inspect
import math
from typing import cast

import pytest
from hypothesis import given, strategies as st

from abdp.core.rate_limit import Clock, FixedWindowRateLimiter


def test_rate_limit_module_exports_clock_and_fixed_window_rate_limiter() -> None:
    import abdp.core.rate_limit as module

    assert sorted(module.__all__) == ["Clock", "FixedWindowRateLimiter"]


def test_fixed_window_rate_limiter_init_is_keyword_only() -> None:
    sig = inspect.signature(FixedWindowRateLimiter)
    for name, param in sig.parameters.items():
        assert param.kind is inspect.Parameter.KEYWORD_ONLY, (
            f"parameter {name!r} must be keyword-only, got {param.kind}"
        )


def test_allow_returns_true_up_to_max_calls_then_false_within_one_window() -> None:
    times = iter([0.1, 0.2, 0.3, 0.4, 0.5])
    limiter = FixedWindowRateLimiter(max_calls=3, window_seconds=1.0, clock=lambda: next(times))
    assert limiter.allow() is True
    assert limiter.allow() is True
    assert limiter.allow() is True
    assert limiter.allow() is False
    assert limiter.allow() is False


def test_allow_resets_when_time_enters_next_aligned_window() -> None:
    times = iter([0.1, 0.5, 1.0, 1.5])
    limiter = FixedWindowRateLimiter(max_calls=2, window_seconds=1.0, clock=lambda: next(times))
    assert limiter.allow() is True
    assert limiter.allow() is True
    assert limiter.allow() is True
    assert limiter.allow() is True


def test_allow_treats_exact_window_end_as_next_window() -> None:
    times = iter([0.0, 1.0])
    limiter = FixedWindowRateLimiter(max_calls=1, window_seconds=1.0, clock=lambda: next(times))
    assert limiter.allow() is True
    assert limiter.allow() is True


def test_allow_uses_floor_aligned_windows_for_negative_times() -> None:
    times = iter([-0.5, -0.1, 0.0])
    limiter = FixedWindowRateLimiter(max_calls=1, window_seconds=1.0, clock=lambda: next(times))
    assert limiter.allow() is True
    assert limiter.allow() is False
    assert limiter.allow() is True


def test_constructor_rejects_non_int_max_calls() -> None:
    with pytest.raises(TypeError, match=r"^max_calls must be an int, got float$"):
        FixedWindowRateLimiter(max_calls=cast(int, 1.5), window_seconds=1.0)
    with pytest.raises(TypeError, match=r"^max_calls must be an int, got str$"):
        FixedWindowRateLimiter(max_calls=cast(int, "3"), window_seconds=1.0)


def test_constructor_rejects_bool_max_calls() -> None:
    with pytest.raises(TypeError, match=r"^max_calls must be an int, got bool$"):
        FixedWindowRateLimiter(max_calls=cast(int, True), window_seconds=1.0)
    with pytest.raises(TypeError, match=r"^max_calls must be an int, got bool$"):
        FixedWindowRateLimiter(max_calls=cast(int, False), window_seconds=1.0)


def test_constructor_rejects_max_calls_less_than_one() -> None:
    with pytest.raises(ValueError, match=r"^max_calls must be at least 1, got 0$"):
        FixedWindowRateLimiter(max_calls=0, window_seconds=1.0)
    with pytest.raises(ValueError, match=r"^max_calls must be at least 1, got -3$"):
        FixedWindowRateLimiter(max_calls=-3, window_seconds=1.0)


def test_constructor_rejects_non_real_window_seconds() -> None:
    with pytest.raises(TypeError, match=r"^window_seconds must be a real number, got str$"):
        FixedWindowRateLimiter(max_calls=1, window_seconds=cast(float, "1.0"))
    with pytest.raises(TypeError, match=r"^window_seconds must be a real number, got NoneType$"):
        FixedWindowRateLimiter(max_calls=1, window_seconds=cast(float, None))


def test_constructor_rejects_bool_window_seconds() -> None:
    with pytest.raises(TypeError, match=r"^window_seconds must be a real number, got bool$"):
        FixedWindowRateLimiter(max_calls=1, window_seconds=cast(float, True))
    with pytest.raises(TypeError, match=r"^window_seconds must be a real number, got bool$"):
        FixedWindowRateLimiter(max_calls=1, window_seconds=cast(float, False))


def test_constructor_rejects_non_positive_window_seconds() -> None:
    with pytest.raises(ValueError, match=r"^window_seconds must be positive, got 0\.0$"):
        FixedWindowRateLimiter(max_calls=1, window_seconds=0.0)
    with pytest.raises(ValueError, match=r"^window_seconds must be positive, got -1\.5$"):
        FixedWindowRateLimiter(max_calls=1, window_seconds=-1.5)


def test_constructor_rejects_non_finite_window_seconds() -> None:
    with pytest.raises(ValueError, match=r"^window_seconds must be finite, got nan$"):
        FixedWindowRateLimiter(max_calls=1, window_seconds=math.nan)
    with pytest.raises(ValueError, match=r"^window_seconds must be finite, got inf$"):
        FixedWindowRateLimiter(max_calls=1, window_seconds=math.inf)


def test_constructor_rejects_non_callable_clock() -> None:
    with pytest.raises(TypeError, match=r"^clock must be callable$"):
        FixedWindowRateLimiter(max_calls=1, window_seconds=1.0, clock=cast(Clock, 42))


def test_constructor_does_not_call_clock() -> None:
    calls: list[None] = []

    def clock() -> float:
        calls.append(None)
        return 0.0

    FixedWindowRateLimiter(max_calls=1, window_seconds=1.0, clock=clock)
    assert calls == []


def test_allow_calls_clock_once_per_invocation() -> None:
    calls: list[None] = []

    def clock() -> float:
        calls.append(None)
        return float(len(calls))

    limiter = FixedWindowRateLimiter(max_calls=2, window_seconds=10.0, clock=clock)
    limiter.allow()
    limiter.allow()
    limiter.allow()
    assert len(calls) == 3


def test_allow_rejects_non_real_clock_reading() -> None:
    limiter = FixedWindowRateLimiter(
        max_calls=1,
        window_seconds=1.0,
        clock=cast(Clock, lambda: "not a number"),
    )
    with pytest.raises(TypeError, match=r"^clock must return a real number, got str$"):
        limiter.allow()


def test_allow_rejects_non_finite_clock_reading() -> None:
    limiter = FixedWindowRateLimiter(max_calls=1, window_seconds=1.0, clock=lambda: math.nan)
    with pytest.raises(ValueError, match=r"^clock must return a finite number, got nan$"):
        limiter.allow()
    limiter_inf = FixedWindowRateLimiter(max_calls=1, window_seconds=1.0, clock=lambda: math.inf)
    with pytest.raises(ValueError, match=r"^clock must return a finite number, got inf$"):
        limiter_inf.allow()


def test_allow_raises_when_clock_moves_backwards_and_preserves_state() -> None:
    times = iter([5.0, 4.0, 5.5])
    limiter = FixedWindowRateLimiter(max_calls=2, window_seconds=10.0, clock=lambda: next(times))
    assert limiter.allow() is True
    with pytest.raises(RuntimeError, match=r"^clock must be monotonic non-decreasing$"):
        limiter.allow()
    assert limiter.allow() is True


def _oracle_allow(
    max_calls: int,
    window_seconds: float,
    times: list[int],
) -> list[bool]:
    expected: list[bool] = []
    last_window: int | None = None
    used = 0
    for now in times:
        idx = math.floor(now / window_seconds)
        if last_window is None or idx != last_window:
            last_window = idx
            used = 0
        if used < max_calls:
            expected.append(True)
            used += 1
        else:
            expected.append(False)
    return expected


@given(
    max_calls=st.integers(min_value=1, max_value=5),
    window_seconds_int=st.integers(min_value=1, max_value=10),
    times=st.lists(st.integers(min_value=0, max_value=200), min_size=1, max_size=50).map(sorted),
)
def test_property_allow_matches_fixed_window_oracle_for_monotonic_clock_values(
    max_calls: int,
    window_seconds_int: int,
    times: list[int],
) -> None:
    window_seconds = float(window_seconds_int)
    iterator = iter(float(t) for t in times)
    limiter = FixedWindowRateLimiter(
        max_calls=max_calls,
        window_seconds=window_seconds,
        clock=lambda: next(iterator),
    )
    actual = [limiter.allow() for _ in times]
    expected = _oracle_allow(max_calls, window_seconds, times)
    assert actual == expected
