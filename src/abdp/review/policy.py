"""Correction policy for deterministic review loops."""

import math
from dataclasses import dataclass
from typing import Literal

__all__ = ["CorrectionMode", "CorrectionPolicy"]

type CorrectionMode = Literal["rollback", "revise", "stop"]


def _validate_max_retries(value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"max_retries must be int, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"max_retries must be >= 0, got {value}")


def _validate_min_score(value: float) -> None:
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError("min_score must be finite and between 0.0 and 1.0")


@dataclass(frozen=True, slots=True)
class CorrectionPolicy:
    """Deterministic retry policy for ``ReviewLoopRunner``."""

    max_retries: int
    min_score: float
    on_fail: "Literal['rollback', 'revise', 'stop']"

    def __post_init__(self) -> None:
        _validate_max_retries(self.max_retries)
        _validate_min_score(self.min_score)
        if self.on_fail not in {"rollback", "revise", "stop"}:
            raise ValueError(f"unsupported on_fail mode: {self.on_fail}")
