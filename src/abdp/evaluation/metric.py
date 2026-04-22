"""``Metric`` protocol and ``MetricResult`` record exposed by ``abdp.evaluation``.

A ``Metric`` reduces a run record (whose concrete type is supplied by the
caller via the ``R`` type parameter) into a single ``MetricResult``. The
``value`` field of ``MetricResult`` MUST be JSON-serializable per
``abdp.core.types.JsonValue``; ``details`` is a JSON object carrying optional
auxiliary evidence such as per-segment breakdowns.
"""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from abdp.core.types import JsonObject, JsonValue

__all__ = ["Metric", "MetricResult"]


@dataclass(frozen=True, slots=True)
class MetricResult:
    """Outcome of evaluating a single :class:`Metric` against a run."""

    metric_id: str
    value: JsonValue
    details: JsonObject


@runtime_checkable
class Metric[R](Protocol):
    """Reduces a run record of type ``R`` into a :class:`MetricResult`."""

    metric_id: str

    def evaluate(self, run: R) -> MetricResult:
        """Return the metric's :class:`MetricResult` for ``run``."""

        ...  # pragma: no cover
