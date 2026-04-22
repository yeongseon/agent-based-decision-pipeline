"""``EvaluationSummary`` record and ``evaluate_gates`` / ``aggregate_results`` helpers exposed by ``abdp.evaluation``.

The summary stage closes the metric -> gate -> summary pipeline:
:func:`evaluate_gates` reduces metric results into gate results, and
:func:`aggregate_results` folds metrics and gate results into a single
:class:`EvaluationSummary` whose ``overall_status`` follows the
``FAIL > WARN > PASS`` precedence (empty gates yield ``PASS``).
"""

from collections.abc import Iterable
from dataclasses import dataclass

from abdp.evaluation.gate import Gate, GateResult, GateStatus
from abdp.evaluation.metric import MetricResult

__all__ = ["EvaluationSummary", "aggregate_results", "evaluate_gates"]


@dataclass(frozen=True, slots=True)
class EvaluationSummary:
    """Frozen result of an evaluation run.

    ``metrics`` and ``gates`` preserve the iteration order of their producing
    helpers (:func:`abdp.evaluation.evaluate_metrics` and
    :func:`evaluate_gates`); ``overall_status`` is the precedence-reduced
    status across ``gates``.
    """

    metrics: tuple[MetricResult, ...]
    gates: tuple[GateResult, ...]
    overall_status: GateStatus


def evaluate_gates(gates: Iterable[Gate], metrics: Iterable[MetricResult]) -> tuple[GateResult, ...]:
    """Evaluate ``gates`` against ``metrics`` and return their results in iteration order.

    ``metrics`` is materialized into a tuple once so every gate sees the same
    sequence; each gate's :meth:`Gate.evaluate` is invoked exactly once with
    that tuple. The output tuple mirrors the iteration order of ``gates``.
    The helper does not detect duplicate ``gate_id`` values.
    """

    materialized = tuple(metrics)
    return tuple(gate.evaluate(materialized) for gate in gates)


def aggregate_results(metrics: Iterable[MetricResult], gate_results: Iterable[GateResult]) -> EvaluationSummary:
    """Aggregate ``metrics`` and ``gate_results`` into an :class:`EvaluationSummary`.

    Inputs are materialized into tuples so the summary stores stable values.
    ``overall_status`` follows ``FAIL > WARN > PASS`` precedence over
    ``gate_results``; an empty ``gate_results`` yields :attr:`GateStatus.PASS`.
    """

    metrics_tuple = tuple(metrics)
    gates_tuple = tuple(gate_results)
    overall_status = _reduce_status(gates_tuple)
    return EvaluationSummary(metrics=metrics_tuple, gates=gates_tuple, overall_status=overall_status)


def _reduce_status(gate_results: tuple[GateResult, ...]) -> GateStatus:
    statuses = {result.status for result in gate_results}
    if GateStatus.FAIL in statuses:
        return GateStatus.FAIL
    if GateStatus.WARN in statuses:
        return GateStatus.WARN
    return GateStatus.PASS
