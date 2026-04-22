"""Structural tests for ``abdp.evaluation.Metric`` and ``MetricResult``."""

import dataclasses
from typing import Any, cast, get_type_hints

import pytest

from abdp.evaluation import Metric, MetricResult


def test_metric_is_protocol() -> None:
    assert cast(Any, Metric)._is_protocol is True


def test_metric_is_runtime_checkable() -> None:
    class _Impl:
        agent_id: str = "ignored"
        metric_id: str = "m"

        def evaluate(self, run: object) -> MetricResult:
            return MetricResult(metric_id="m", value=0, details={})

    assert isinstance(_Impl(), Metric)


def test_metric_rejects_non_conforming_object_at_runtime() -> None:
    class _NotMetric:
        pass

    assert not isinstance(_NotMetric(), Metric)


def test_metric_declares_metric_id_and_evaluate() -> None:
    annotations = get_type_hints(Metric)
    assert annotations["metric_id"] is str
    assert callable(Metric.evaluate)


def test_metric_result_is_frozen_dataclass() -> None:
    assert dataclasses.is_dataclass(MetricResult)
    params = cast(Any, MetricResult).__dataclass_params__
    assert params.frozen is True


def test_metric_result_uses_slots() -> None:
    assert "__slots__" in vars(MetricResult)


def test_metric_result_field_order_and_types() -> None:
    fields = dataclasses.fields(MetricResult)
    assert [f.name for f in fields] == ["metric_id", "value", "details"]
    annotations = get_type_hints(MetricResult)
    assert annotations["metric_id"] is str


def test_metric_result_requires_all_fields() -> None:
    for field in dataclasses.fields(MetricResult):
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING


def test_metric_result_is_immutable() -> None:
    result = MetricResult(metric_id="m", value=1, details={})
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(result, "metric_id", "other")  # noqa: B010


def test_metric_result_equality_is_value_based() -> None:
    a = MetricResult(metric_id="m", value=1, details={"k": "v"})
    b = MetricResult(metric_id="m", value=1, details={"k": "v"})
    c = MetricResult(metric_id="m", value=2, details={"k": "v"})
    assert a == b
    assert a != c
