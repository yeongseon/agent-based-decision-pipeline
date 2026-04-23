"""Reviser protocol for deterministic review retries."""

from typing import Protocol, runtime_checkable

from abdp.review.attempt import ReviewAttempt
from abdp.simulation import ActionProposal

__all__ = ["Reviser"]


@runtime_checkable
class Reviser[A: ActionProposal](Protocol):
    """Deterministic proposal reviser for a rejected attempt."""

    def revise(self, attempt: ReviewAttempt[A]) -> tuple[A, ...]: ...  # pragma: no cover
