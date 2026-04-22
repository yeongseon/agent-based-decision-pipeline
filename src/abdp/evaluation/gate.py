"""``Gate`` protocol, ``GateResult`` record, and ``GateStatus`` enum exposed by ``abdp.evaluation``.

A ``Gate`` reduces an iterable of :class:`MetricResult` (typically produced by
:func:`evaluate_metrics`) into a single :class:`GateResult`. The
``GateResult.details`` field MUST be JSON-serializable per
``abdp.core.types.JsonValue``; ``GateStatus`` values are lowercase strings
(``"pass"``/``"fail"``/``"warn"``) so a ``GateResult`` round-trips cleanly
through JSON. The dataclass itself does not enforce JSON-validity so that
``GateResult`` stays cheap to build inside hot evaluation loops.
"""

import enum
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from abdp.core.types import JsonObject
from abdp.evaluation.metric import MetricResult

__all__ = ["Gate", "GateResult", "GateStatus"]


class GateStatus(enum.StrEnum):
    """Outcome category emitted by a :class:`Gate`.

    Values are lowercase strings to keep :class:`GateResult` JSON-friendly.
    """

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


@dataclass(frozen=True, slots=True)
class GateResult:
    """Outcome of evaluating a single :class:`Gate` against metric results.

    ``details`` MUST be JSON-serializable. ``reason`` is a free-form
    human-readable string explaining ``status``.
    """

    gate_id: str
    status: GateStatus
    reason: str
    details: JsonObject


@runtime_checkable
class Gate(Protocol):
    """Reduces an iterable of :class:`MetricResult` into a :class:`GateResult`."""

    gate_id: str

    def evaluate(self, metrics: Iterable[MetricResult]) -> GateResult:
        """Return the gate's :class:`GateResult` for ``metrics``."""

        ...  # pragma: no cover
