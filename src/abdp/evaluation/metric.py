"""``Metric`` protocol and ``MetricResult`` record exposed by ``abdp.evaluation``.

A ``Metric`` reduces a run record (whose concrete type is supplied by the
caller via the ``R`` type parameter) into a single ``MetricResult``. The
``value`` field of ``MetricResult`` MUST be JSON-serializable per
``abdp.core.types.JsonValue``; ``details`` is a JSON object carrying optional
auxiliary evidence such as per-segment breakdowns.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from abdp.core.types import JsonObject, JsonValue

__all__ = ["Metric", "MetricResult", "evaluate_metrics"]


@dataclass(frozen=True, slots=True)
class MetricResult:
    """Outcome of evaluating a single :class:`Metric` against a run.

    ``value`` and ``details`` MUST be JSON-serializable. Callers can verify
    a candidate ``value`` with :func:`abdp.core.types.is_json_value` before
    constructing the result; the dataclass itself does not enforce this so
    that ``MetricResult`` stays cheap to build inside hot evaluation loops.
    """

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


def evaluate_metrics[R](metrics: Iterable[Metric[R]], run: R) -> tuple[MetricResult, ...]:
    """Evaluate ``metrics`` against ``run`` and return their results in iteration order.

    Each metric's :meth:`Metric.evaluate` is invoked exactly once with ``run``,
    in the order produced by iterating ``metrics``. The output tuple mirrors
    that order, so results are deterministic when both the iterable and each
    metric's ``evaluate`` are deterministic for the same ``run``. The helper
    does not detect duplicate ``metric_id`` values.
    """

    return tuple(metric.evaluate(run) for metric in metrics)
