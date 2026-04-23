"""Tests for ``abdp.inspector.TraceEvent`` and ``make_trace_event``.

Locks the determinism contract:
``event_id = deterministic_uuid(seed, _TRACE_NAMESPACE, f"{run_id}\\0{seq}")``
so identity depends only on ``(seed, run_id, seq)`` while ``step_index``,
``event_type``, ``attributes``, ``timestamp_ns``, and ``parent_event_id``
are payload metadata that do not influence ``event_id``.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from typing import Any, cast, get_type_hints
from uuid import UUID

import pytest

from abdp.core.types import Seed
from abdp.inspector import TraceEvent, make_trace_event


def _event(**overrides: Any) -> TraceEvent:
    base: dict[str, Any] = {
        "event_id": UUID("00000000-0000-0000-0000-000000000001"),
        "run_id": "run-1",
        "seq": 0,
        "step_index": 0,
        "event_type": "step.begin",
        "attributes": {},
        "timestamp_ns": 0,
        "parent_event_id": None,
    }
    base.update(overrides)
    return TraceEvent(**base)


def test_trace_event_is_frozen_dataclass() -> None:
    assert dataclasses.is_dataclass(TraceEvent)
    params = cast(Any, TraceEvent).__dataclass_params__
    assert params.frozen is True


def test_trace_event_uses_slots() -> None:
    assert "__slots__" in vars(TraceEvent)


def test_trace_event_field_order_and_types() -> None:
    fields = dataclasses.fields(TraceEvent)
    assert [f.name for f in fields] == [
        "event_id",
        "run_id",
        "seq",
        "step_index",
        "event_type",
        "attributes",
        "timestamp_ns",
        "parent_event_id",
    ]
    annotations = get_type_hints(TraceEvent)
    assert annotations["event_id"] is UUID
    assert annotations["run_id"] is str
    assert annotations["seq"] is int
    assert annotations["step_index"] is int
    assert annotations["event_type"] is str
    assert annotations["timestamp_ns"] is int
    assert annotations["parent_event_id"] == UUID | None


def test_trace_event_requires_all_fields() -> None:
    for field in dataclasses.fields(TraceEvent):
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING


def test_trace_event_is_immutable() -> None:
    ev = _event()
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(ev, "event_type", "other")  # noqa: B010


def test_trace_event_equality_is_value_based() -> None:
    a = _event()
    b = _event()
    c = _event(event_type="step.end")
    assert a == b
    assert a != c


def test_trace_event_rejects_negative_seq() -> None:
    with pytest.raises(ValueError, match="seq"):
        _event(seq=-1)


def test_trace_event_rejects_negative_step_index() -> None:
    with pytest.raises(ValueError, match="step_index"):
        _event(step_index=-1)


def test_trace_event_rejects_negative_timestamp_ns() -> None:
    with pytest.raises(ValueError, match="timestamp_ns"):
        _event(timestamp_ns=-1)


def test_trace_event_rejects_empty_run_id() -> None:
    with pytest.raises(ValueError, match="run_id"):
        _event(run_id="")


def test_trace_event_rejects_empty_event_type() -> None:
    with pytest.raises(ValueError, match="event_type"):
        _event(event_type="")


def test_trace_event_attributes_only_allow_primitive_values() -> None:
    with pytest.raises(TypeError, match="attribute"):
        _event(attributes={"k": object()})


def test_trace_event_attributes_reject_non_str_keys() -> None:
    with pytest.raises(TypeError, match="attribute key"):
        _event(attributes={1: "v"})


def test_trace_event_attributes_accept_str_int_float_bool() -> None:
    ev = _event(attributes={"s": "v", "i": 1, "f": 1.5, "b": True})
    assert ev.attributes["s"] == "v"
    assert ev.attributes["i"] == 1
    assert ev.attributes["f"] == 1.5
    assert ev.attributes["b"] is True


def test_trace_event_attributes_are_a_mapping() -> None:
    ev = _event(attributes={"k": "v"})
    assert isinstance(ev.attributes, Mapping)


def test_make_trace_event_returns_trace_event() -> None:
    ev = make_trace_event(
        seed=Seed(0),
        run_id="run-1",
        seq=0,
        step_index=0,
        event_type="step.begin",
        attributes={},
        timestamp_ns=0,
        parent_event_id=None,
    )
    assert isinstance(ev, TraceEvent)
    assert isinstance(ev.event_id, UUID)


def test_make_trace_event_is_deterministic_for_same_inputs() -> None:
    args: dict[str, Any] = {
        "seed": Seed(7),
        "run_id": "run-1",
        "seq": 3,
        "step_index": 1,
        "event_type": "decision.evaluate",
        "attributes": {"agent": "a"},
        "timestamp_ns": 3,
        "parent_event_id": None,
    }
    a = make_trace_event(**args)
    b = make_trace_event(**args)
    assert a.event_id == b.event_id


def test_make_trace_event_id_changes_with_seq() -> None:
    args: dict[str, Any] = {
        "seed": Seed(0),
        "run_id": "run-1",
        "seq": 0,
        "step_index": 0,
        "event_type": "step.begin",
        "attributes": {},
        "timestamp_ns": 0,
        "parent_event_id": None,
    }
    a = make_trace_event(**args)
    b = make_trace_event(**{**args, "seq": 1})
    assert a.event_id != b.event_id


def test_make_trace_event_id_changes_with_run_id() -> None:
    args: dict[str, Any] = {
        "seed": Seed(0),
        "run_id": "run-1",
        "seq": 0,
        "step_index": 0,
        "event_type": "step.begin",
        "attributes": {},
        "timestamp_ns": 0,
        "parent_event_id": None,
    }
    a = make_trace_event(**args)
    b = make_trace_event(**{**args, "run_id": "run-2"})
    assert a.event_id != b.event_id


def test_make_trace_event_id_changes_with_seed() -> None:
    args: dict[str, Any] = {
        "run_id": "run-1",
        "seq": 0,
        "step_index": 0,
        "event_type": "step.begin",
        "attributes": {},
        "timestamp_ns": 0,
        "parent_event_id": None,
    }
    a = make_trace_event(seed=Seed(0), **args)
    b = make_trace_event(seed=Seed(1), **args)
    assert a.event_id != b.event_id


def test_make_trace_event_id_does_not_depend_on_metadata() -> None:
    args: dict[str, Any] = {
        "seed": Seed(0),
        "run_id": "run-1",
        "seq": 0,
        "step_index": 0,
        "event_type": "step.begin",
        "attributes": {},
        "timestamp_ns": 0,
        "parent_event_id": None,
    }
    a = make_trace_event(**args)
    b = make_trace_event(
        **{
            **args,
            "step_index": 99,
            "event_type": "step.end",
            "attributes": {"x": 1},
            "timestamp_ns": 12345,
            "parent_event_id": UUID("00000000-0000-0000-0000-0000000000aa"),
        }
    )
    assert a.event_id == b.event_id


def test_make_trace_event_pins_golden_vector() -> None:
    ev = make_trace_event(
        seed=Seed(42),
        run_id="scenario-x",
        seq=7,
        step_index=2,
        event_type="step.begin",
        attributes={},
        timestamp_ns=7,
        parent_event_id=None,
    )
    assert ev.event_id == UUID("05536901-00d4-56d2-bc07-b8e930292fe0")
