"""Public surface for the ``abdp.evaluation`` package.

The evaluation package owns the v0.3 metric, gate, and summary contracts.
Symbols are added to ``__all__`` issue by issue against the frozen surface
test in ``tests/evaluation/test_evaluation_public_surface.py``.
"""

from abdp.evaluation.gate import Gate, GateResult, GateStatus
from abdp.evaluation.metric import Metric, MetricResult, evaluate_metrics

globals().pop("gate", None)
globals().pop("metric", None)

__all__: tuple[str, ...] = (
    "Gate",
    "GateResult",
    "GateStatus",
    "Metric",
    "MetricResult",
    "evaluate_metrics",
)
