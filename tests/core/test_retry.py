"""Tests for the deterministic retry decorator (#22)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Protocol

import pytest

from abdp.core.retry import Backoff, retry


def test_retry_module_exposes_only_retry_and_backoff_publicly() -> None:
    import abdp.core.retry as module

    assert sorted(module.__all__) == ["Backoff", "retry"]


def test_retry_returns_on_first_success_without_backoff_or_sleep() -> None:
    backoff_calls: list[int] = []
    sleep_calls: list[float] = []

    def backoff(attempt: int) -> float:
        backoff_calls.append(attempt)
        return 0.1

    def sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    @retry(on=(ValueError,), max_attempts=3, backoff=backoff, sleep=sleep)
    def succeed() -> str:
        return "ok"

    assert succeed() == "ok"
    assert backoff_calls == []
    assert sleep_calls == []


def test_retry_retries_matching_subclass_exception_until_success() -> None:
    backoff_calls: list[int] = []
    sleep_calls: list[float] = []
    attempts = 0

    def backoff(attempt: int) -> float:
        backoff_calls.append(attempt)
        return float(attempt) * 0.5

    def sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    @retry(on=(LookupError,), max_attempts=4, backoff=backoff, sleep=sleep)
    def flaky() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise KeyError("transient")
        return "done"

    assert flaky() == "done"
    assert attempts == 3
    assert backoff_calls == [1, 2]
    assert sleep_calls == [0.5, 1.0]


def test_retry_reraises_last_matching_exception_after_max_attempts() -> None:
    sleep_calls: list[float] = []
    raised: list[ValueError] = []

    def sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    @retry(on=(ValueError,), max_attempts=3, backoff=lambda _attempt: 0.0, sleep=sleep)
    def always_fails() -> None:
        exc = ValueError(f"fail {len(raised)}")
        raised.append(exc)
        raise exc

    with pytest.raises(ValueError, match=r"^fail 2$") as info:
        always_fails()

    assert info.value is raised[-1]
    assert len(raised) == 3
    assert sleep_calls == [0.0, 0.0]


def test_retry_propagates_non_matching_exception_immediately() -> None:
    backoff_calls: list[int] = []
    sleep_calls: list[float] = []
    attempts = 0

    def backoff(attempt: int) -> float:
        backoff_calls.append(attempt)
        return 0.0

    def sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    @retry(on=(ValueError,), max_attempts=5, backoff=backoff, sleep=sleep)
    def wrong_kind() -> None:
        nonlocal attempts
        attempts += 1
        raise TypeError("nope")

    with pytest.raises(TypeError, match=r"^nope$"):
        wrong_kind()
    assert attempts == 1
    assert backoff_calls == []
    assert sleep_calls == []


def test_retry_propagates_later_non_matching_exception_without_extra_sleep() -> None:
    sleep_calls: list[float] = []
    attempts = 0

    def sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    @retry(on=(ValueError,), max_attempts=5, backoff=lambda _attempt: 0.25, sleep=sleep)
    def changes_kind() -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ValueError("first")
        raise TypeError("later")

    with pytest.raises(TypeError, match=r"^later$"):
        changes_kind()
    assert attempts == 2
    assert sleep_calls == [0.25]


def test_retry_with_one_attempt_never_sleeps() -> None:
    sleep_calls: list[float] = []
    attempts = 0

    def sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    @retry(on=(ValueError,), max_attempts=1, backoff=lambda _attempt: 9.0, sleep=sleep)
    def single() -> None:
        nonlocal attempts
        attempts += 1
        raise ValueError("once")

    with pytest.raises(ValueError, match=r"^once$"):
        single()
    assert attempts == 1
    assert sleep_calls == []


def test_retry_passes_through_arguments_and_preserves_metadata() -> None:
    @retry(on=(ValueError,), max_attempts=2)
    def add(a: int, b: int) -> int:
        """Add two integers."""
        return a + b

    assert add(2, 3) == 5
    assert add.__name__ == "add"
    assert add.__doc__ == "Add two integers."


def test_retry_validates_max_attempts() -> None:
    with pytest.raises(ValueError, match=r"^max_attempts must be at least 1, got 0$"):
        retry(on=(ValueError,), max_attempts=0)

    with pytest.raises(ValueError, match=r"^max_attempts must be at least 1, got -3$"):
        retry(on=(ValueError,), max_attempts=-3)


def test_retry_validates_on_is_not_empty() -> None:
    with pytest.raises(ValueError, match=r"^on must contain at least one exception type$"):
        retry(on=(), max_attempts=2)


def test_retry_rejects_base_exception_subclasses_in_on() -> None:
    with pytest.raises(
        TypeError,
        match=r"^on entries must be subclasses of Exception, got KeyboardInterrupt$",
    ):
        retry(on=(KeyboardInterrupt,), max_attempts=2)  # type: ignore[arg-type]

    with pytest.raises(
        TypeError,
        match=r"^on entries must be subclasses of Exception, got BaseException$",
    ):
        retry(on=(BaseException,), max_attempts=2)  # type: ignore[arg-type]


def test_retry_rejects_non_class_entries_in_on() -> None:
    with pytest.raises(
        TypeError,
        match=r"^on entries must be subclasses of Exception, got int$",
    ):
        retry(on=(123,), max_attempts=2)  # type: ignore[arg-type]


def test_retry_rejects_async_function() -> None:
    decorator = retry(on=(ValueError,), max_attempts=2)

    async def coro() -> None:
        return None

    with pytest.raises(
        TypeError,
        match=r"^retry only supports regular synchronous callables; got async function 'coro'$",
    ):
        decorator(coro)


def test_retry_rejects_generator_function() -> None:
    decorator = retry(on=(ValueError,), max_attempts=2)

    def gen() -> Iterator[int]:
        yield 1

    with pytest.raises(
        TypeError,
        match=r"^retry only supports regular synchronous callables; got generator function 'gen'$",
    ):
        decorator(gen)


def test_retry_rejects_async_generator_function() -> None:
    decorator = retry(on=(ValueError,), max_attempts=2)

    async def agen() -> AsyncIterator[int]:
        yield 1

    with pytest.raises(
        TypeError,
        match=r"^retry only supports regular synchronous callables; got async generator function 'agen'$",
    ):
        decorator(agen)


class _BinaryOp(Protocol):
    def __call__(self, a: int, b: int) -> int: ...


def test_retry_preserves_callable_signature_for_static_typing() -> None:
    @retry(on=(ValueError,), max_attempts=1)
    def multiply(a: int, b: int) -> int:
        return a * b

    operation: _BinaryOp = multiply
    assert operation(3, 4) == 12


def test_backoff_alias_resolves_to_callable_int_to_float() -> None:
    def linear(attempt: int) -> float:
        return float(attempt)

    backoff: Backoff = linear
    assert backoff(2) == 2.0


def test_retry_default_backoff_yields_zero_delay() -> None:
    sleep_calls: list[float] = []
    attempts = 0

    def sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    @retry(on=(ValueError,), max_attempts=3, sleep=sleep)
    def fails() -> None:
        nonlocal attempts
        attempts += 1
        raise ValueError("again")

    with pytest.raises(ValueError, match=r"^again$"):
        fails()
    assert attempts == 3
    assert sleep_calls == [0.0, 0.0]
