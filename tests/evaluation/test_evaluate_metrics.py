"""Tests for ``abdp.evaluation.evaluate_metrics`` ordered helper."""

from collections.abc import Iterator
from dataclasses import dataclass, field

from abdp.evaluation import MetricResult, evaluate_metrics


@dataclass
class _RecordingMetric:
    metric_id: str
    value: int
    calls: list[object] = field(default_factory=list)

    def evaluate(self, run: object) -> MetricResult:
        self.calls.append(run)
        return MetricResult(metric_id=self.metric_id, value=self.value, details={})


def _expected(metrics: list[_RecordingMetric]) -> tuple[MetricResult, ...]:
    return tuple(MetricResult(metric_id=m.metric_id, value=m.value, details={}) for m in metrics)


def test_evaluate_metrics_returns_tuple() -> None:
    result = evaluate_metrics([], run=object())
    assert isinstance(result, tuple)


def test_evaluate_metrics_empty_input_returns_empty_tuple() -> None:
    assert evaluate_metrics([], run=object()) == ()


def test_evaluate_metrics_preserves_input_order() -> None:
    metrics = [
        _RecordingMetric(metric_id="b", value=2),
        _RecordingMetric(metric_id="a", value=1),
        _RecordingMetric(metric_id="c", value=3),
    ]
    run = object()
    assert evaluate_metrics(metrics, run=run) == _expected(metrics)


def test_evaluate_metrics_calls_each_metric_exactly_once() -> None:
    metrics = [
        _RecordingMetric(metric_id="a", value=1),
        _RecordingMetric(metric_id="b", value=2),
    ]
    run = object()
    evaluate_metrics(metrics, run=run)
    for m in metrics:
        assert m.calls == [run]


def test_evaluate_metrics_accepts_generator_input() -> None:
    metrics = [
        _RecordingMetric(metric_id="a", value=1),
        _RecordingMetric(metric_id="b", value=2),
    ]
    run = object()

    def gen() -> Iterator[_RecordingMetric]:
        yield from metrics

    assert evaluate_metrics(gen(), run=run) == _expected(metrics)


def test_evaluate_metrics_is_deterministic_across_repeated_calls() -> None:
    def make_metrics() -> list[_RecordingMetric]:
        return [
            _RecordingMetric(metric_id="a", value=1),
            _RecordingMetric(metric_id="b", value=2),
        ]

    run = object()
    first = evaluate_metrics(make_metrics(), run=run)
    second = evaluate_metrics(make_metrics(), run=run)
    assert first == second
