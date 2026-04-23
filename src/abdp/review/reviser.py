"""Reviser protocol for deterministic review retries."""

from typing import Protocol, runtime_checkable

from abdp.review.attempt import ReviewAttempt

__all__ = ["Reviser"]


@runtime_checkable
class Reviser[A](Protocol):
    """Deterministic proposal reviser for a rejected attempt."""

    def revise(self, attempt: ReviewAttempt[A]) -> tuple[A, ...]: ...  # pragma: no cover
