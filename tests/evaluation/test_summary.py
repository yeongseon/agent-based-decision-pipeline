"""Structural and behavioral tests for ``abdp.evaluation`` summary stage."""

import dataclasses
from typing import Any, cast, get_type_hints

from abdp.evaluation import (
    EvaluationSummary,
    Gate,
    GateResult,
    GateStatus,
    MetricResult,
    aggregate_results,
    evaluate_gates,
)


def _metric(metric_id: str = "m") -> MetricResult:
    return MetricResult(metric_id=metric_id, value=1, details={})


def _gate_result(gate_id: str = "g", status: GateStatus = GateStatus.PASS) -> GateResult:
    return GateResult(gate_id=gate_id, status=status, reason="ok", details={})


class _StaticGate:
    def __init__(self, gate_id: str, status: GateStatus = GateStatus.PASS) -> None:
        self.gate_id = gate_id
        self._status = status
        self.calls = 0

    def evaluate(self, metrics: object) -> GateResult:
        self.calls += 1
        return GateResult(gate_id=self.gate_id, status=self._status, reason="ok", details={})


def test_evaluation_summary_is_frozen_dataclass() -> None:
    assert dataclasses.is_dataclass(EvaluationSummary)
    params = cast(Any, EvaluationSummary).__dataclass_params__
    assert params.frozen is True


def test_evaluation_summary_uses_slots() -> None:
    assert "__slots__" in vars(EvaluationSummary)


def test_evaluation_summary_field_order_and_types() -> None:
    fields = dataclasses.fields(EvaluationSummary)
    assert [f.name for f in fields] == ["metrics", "gates", "overall_status"]
    annotations = get_type_hints(EvaluationSummary)
    assert annotations["overall_status"] is GateStatus


def test_evaluation_summary_requires_all_fields() -> None:
    for field in dataclasses.fields(EvaluationSummary):
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING


def test_evaluate_gates_returns_tuple_in_input_order() -> None:
    g1 = _StaticGate("a")
    g2 = _StaticGate("b")
    g3 = _StaticGate("c")
    results = evaluate_gates([g1, g2, g3], [])
    assert isinstance(results, tuple)
    assert [r.gate_id for r in results] == ["a", "b", "c"]


def test_evaluate_gates_calls_each_gate_exactly_once() -> None:
    g1 = _StaticGate("a")
    g2 = _StaticGate("b")
    evaluate_gates([g1, g2], [])
    assert g1.calls == 1
    assert g2.calls == 1


def test_evaluate_gates_materializes_metrics_iterable_for_reuse() -> None:
    metrics_iter = iter([_metric("m1"), _metric("m2")])

    seen: list[tuple[MetricResult, ...]] = []

    class _Recorder:
        gate_id = "r"

        def evaluate(self, metrics: Any) -> GateResult:
            seen.append(tuple(metrics))
            return _gate_result(self.gate_id)

    g1 = _Recorder()
    g2 = _Recorder()
    evaluate_gates([g1, g2], metrics_iter)
    assert len(seen) == 2
    assert seen[0] == seen[1]
    assert len(seen[0]) == 2


def test_evaluate_gates_accepts_iterable_of_gates() -> None:
    def gates_iter() -> Any:
        yield _StaticGate("only")

    results = evaluate_gates(gates_iter(), [])
    assert [r.gate_id for r in results] == ["only"]


def test_evaluate_gates_accepts_empty_inputs() -> None:
    assert evaluate_gates([], []) == ()


def test_evaluate_gates_runtime_signature_satisfies_gate_protocol() -> None:
    g = _StaticGate("x")
    assert isinstance(g, Gate)


def test_aggregate_results_returns_evaluation_summary() -> None:
    summary = aggregate_results([_metric("m1")], [_gate_result("g1")])
    assert isinstance(summary, EvaluationSummary)


def test_aggregate_results_materializes_inputs_to_tuples() -> None:
    summary = aggregate_results(iter([_metric("m1")]), iter([_gate_result("g1")]))
    assert isinstance(summary.metrics, tuple)
    assert isinstance(summary.gates, tuple)
    assert summary.metrics == (_metric("m1"),)
    assert summary.gates == (_gate_result("g1"),)


def test_aggregate_results_preserves_input_order() -> None:
    metrics = [_metric("m1"), _metric("m2"), _metric("m3")]
    gates = [_gate_result("g1"), _gate_result("g2")]
    summary = aggregate_results(metrics, gates)
    assert [m.metric_id for m in summary.metrics] == ["m1", "m2", "m3"]
    assert [g.gate_id for g in summary.gates] == ["g1", "g2"]


def test_aggregate_results_empty_gates_yields_pass() -> None:
    summary = aggregate_results([], [])
    assert summary.overall_status is GateStatus.PASS


def test_aggregate_results_all_pass_yields_pass() -> None:
    summary = aggregate_results(
        [],
        [_gate_result("g1", GateStatus.PASS), _gate_result("g2", GateStatus.PASS)],
    )
    assert summary.overall_status is GateStatus.PASS


def test_aggregate_results_warn_outranks_pass() -> None:
    summary = aggregate_results(
        [],
        [_gate_result("g1", GateStatus.PASS), _gate_result("g2", GateStatus.WARN)],
    )
    assert summary.overall_status is GateStatus.WARN


def test_aggregate_results_fail_outranks_warn_and_pass() -> None:
    summary = aggregate_results(
        [],
        [
            _gate_result("g1", GateStatus.PASS),
            _gate_result("g2", GateStatus.WARN),
            _gate_result("g3", GateStatus.FAIL),
        ],
    )
    assert summary.overall_status is GateStatus.FAIL


def test_aggregate_results_fail_alone_yields_fail() -> None:
    summary = aggregate_results([], [_gate_result("g1", GateStatus.FAIL)])
    assert summary.overall_status is GateStatus.FAIL
