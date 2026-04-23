"""Review attempt records for deterministic correction loops."""

import math
from dataclasses import dataclass

from abdp.scenario import ScenarioStep

__all__ = ["ReviewAttempt", "ReviewDecision", "ReviewTrace"]


def _validate_index(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be int, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")


@dataclass(frozen=True, slots=True)
class ReviewDecision:
    """Critic output for one review attempt."""

    score: float
    critique: str

    def __post_init__(self) -> None:
        if not math.isfinite(self.score) or not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be finite and between 0.0 and 1.0")


@dataclass(frozen=True, slots=True)
class ReviewAttempt[A]:
    """Materialized review attempt for one logical step."""

    step_index: int
    attempt_no: int
    step: ScenarioStep
    decision: ReviewDecision
    accepted: bool

    def __post_init__(self) -> None:
        _validate_index("step_index", self.step_index)
        _validate_index("attempt_no", self.attempt_no)
        if self.step_index != self.step.state.step_index:
            raise ValueError("step_index must match step.state.step_index")


@dataclass(frozen=True, slots=True)
class ReviewTrace:
    """Deterministic collection of review attempts for a run."""

    attempts: tuple[ReviewAttempt, ...]
