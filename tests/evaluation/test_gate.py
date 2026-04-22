"""Structural tests for ``abdp.evaluation.Gate``, ``GateResult``, and ``GateStatus``."""

import dataclasses
import enum
from collections.abc import Iterable
from typing import Any, cast, get_type_hints

import pytest

from abdp.evaluation import Gate, GateResult, GateStatus, MetricResult


def test_gate_status_is_str_enum() -> None:
    assert issubclass(GateStatus, enum.StrEnum)


def test_gate_status_has_exactly_pass_fail_warn() -> None:
    assert {member.name for member in GateStatus} == {"PASS", "FAIL", "WARN"}


def test_gate_status_uses_lowercase_string_values() -> None:
    assert GateStatus.PASS.value == "pass"
    assert GateStatus.FAIL.value == "fail"
    assert GateStatus.WARN.value == "warn"


def test_gate_is_protocol() -> None:
    assert cast(Any, Gate)._is_protocol is True


def test_gate_is_runtime_checkable() -> None:
    class _Impl:
        gate_id: str = "g"

        def evaluate(self, metrics: Iterable[MetricResult]) -> GateResult:
            return GateResult(gate_id="g", status=GateStatus.PASS, reason="ok", details={})

    assert isinstance(_Impl(), Gate)


def test_gate_rejects_non_conforming_object_at_runtime() -> None:
    class _NotGate:
        pass

    assert not isinstance(_NotGate(), Gate)


def test_gate_declares_gate_id_and_evaluate() -> None:
    annotations = get_type_hints(Gate)
    assert annotations["gate_id"] is str
    assert callable(Gate.evaluate)


def test_gate_result_is_frozen_dataclass() -> None:
    assert dataclasses.is_dataclass(GateResult)
    params = cast(Any, GateResult).__dataclass_params__
    assert params.frozen is True


def test_gate_result_uses_slots() -> None:
    assert "__slots__" in vars(GateResult)


def test_gate_result_field_order_and_types() -> None:
    fields = dataclasses.fields(GateResult)
    assert [f.name for f in fields] == ["gate_id", "status", "reason", "details"]
    annotations = get_type_hints(GateResult)
    assert annotations["gate_id"] is str
    assert annotations["status"] is GateStatus
    assert annotations["reason"] is str


def test_gate_result_requires_all_fields() -> None:
    for field in dataclasses.fields(GateResult):
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING


def test_gate_result_is_immutable() -> None:
    result = GateResult(gate_id="g", status=GateStatus.PASS, reason="ok", details={})
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(result, "gate_id", "other")  # noqa: B010


def test_gate_result_equality_is_value_based() -> None:
    a = GateResult(gate_id="g", status=GateStatus.PASS, reason="ok", details={"k": "v"})
    b = GateResult(gate_id="g", status=GateStatus.PASS, reason="ok", details={"k": "v"})
    c = GateResult(gate_id="g", status=GateStatus.FAIL, reason="ok", details={"k": "v"})
    assert a == b
    assert a != c
