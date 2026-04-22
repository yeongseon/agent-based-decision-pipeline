"""Public surface for the ``abdp.evaluation`` package.

The evaluation package owns the v0.3 metric, gate, and summary contracts.
The pipeline is :func:`evaluate_metrics` -> tuple of :class:`MetricResult`
-> :class:`Gate` -> :class:`GateResult`. Symbols are added to ``__all__``
issue by issue against the frozen surface test in
``tests/evaluation/test_evaluation_public_surface.py``.
"""

from abdp.evaluation.gate import Gate, GateResult, GateStatus
from abdp.evaluation.metric import Metric, MetricResult, evaluate_metrics
from abdp.evaluation.summary import EvaluationSummary, aggregate_results, evaluate_gates

globals().pop("gate", None)
globals().pop("metric", None)
globals().pop("summary", None)

__all__: tuple[str, ...] = (
    "EvaluationSummary",
    "Gate",
    "GateResult",
    "GateStatus",
    "Metric",
    "MetricResult",
    "aggregate_results",
    "evaluate_gates",
    "evaluate_metrics",
)
