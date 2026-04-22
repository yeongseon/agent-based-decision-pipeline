"""Tests for ``abdp.evidence.EvidenceRecord`` and ``make_evidence_record``."""

import dataclasses
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast, get_type_hints
from uuid import UUID

import pytest

from abdp.core.types import Seed
from abdp.evidence import EvidenceRecord, make_evidence_record


def _record(**overrides: Any) -> EvidenceRecord:
    base: dict[str, Any] = {
        "evidence_id": UUID("00000000-0000-0000-0000-000000000001"),
        "evidence_key": "k",
        "step_index": 0,
        "agent_id": "agent",
        "payload": {"x": 1},
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return EvidenceRecord(**base)


def test_evidence_record_is_frozen_dataclass() -> None:
    assert dataclasses.is_dataclass(EvidenceRecord)
    params = cast(Any, EvidenceRecord).__dataclass_params__
    assert params.frozen is True


def test_evidence_record_uses_slots() -> None:
    assert "__slots__" in vars(EvidenceRecord)


def test_evidence_record_field_order_and_types() -> None:
    fields = dataclasses.fields(EvidenceRecord)
    assert [f.name for f in fields] == [
        "evidence_id",
        "evidence_key",
        "step_index",
        "agent_id",
        "payload",
        "created_at",
    ]
    annotations = get_type_hints(EvidenceRecord)
    assert annotations["evidence_id"] is UUID
    assert annotations["evidence_key"] is str
    assert annotations["step_index"] is int
    assert annotations["agent_id"] is str
    assert annotations["created_at"] is datetime


def test_evidence_record_requires_all_fields() -> None:
    for field in dataclasses.fields(EvidenceRecord):
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING


def test_evidence_record_is_immutable() -> None:
    rec = _record()
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(rec, "evidence_key", "other")  # noqa: B010


def test_evidence_record_equality_is_value_based() -> None:
    a = _record()
    b = _record()
    c = _record(evidence_key="other")
    assert a == b
    assert a != c


def test_evidence_record_rejects_naive_datetime() -> None:
    with pytest.raises(ValueError, match="UTC"):
        _record(created_at=datetime(2026, 1, 1))


def test_evidence_record_rejects_non_utc_timezone() -> None:
    with pytest.raises(ValueError, match="UTC"):
        _record(created_at=datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=9))))


def test_evidence_record_accepts_utc_datetime() -> None:
    rec = _record(created_at=datetime(2026, 1, 1, tzinfo=UTC))
    assert rec.created_at.tzinfo is UTC


def test_make_evidence_record_returns_evidence_record() -> None:
    rec = make_evidence_record(
        seed=Seed(0),
        evidence_key="k",
        step_index=0,
        agent_id="agent",
        payload={"x": 1},
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    assert isinstance(rec, EvidenceRecord)
    assert isinstance(rec.evidence_id, UUID)


def test_make_evidence_record_is_deterministic_for_same_inputs() -> None:
    args: dict[str, Any] = {
        "seed": Seed(7),
        "evidence_key": "k",
        "step_index": 3,
        "agent_id": "agent",
        "payload": {"x": 1},
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    a = make_evidence_record(**args)
    b = make_evidence_record(**args)
    assert a.evidence_id == b.evidence_id


def test_make_evidence_record_changes_id_when_evidence_key_changes() -> None:
    args: dict[str, Any] = {
        "seed": Seed(0),
        "evidence_key": "k1",
        "step_index": 0,
        "agent_id": "agent",
        "payload": {"x": 1},
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    a = make_evidence_record(**args)
    b = make_evidence_record(**{**args, "evidence_key": "k2"})
    assert a.evidence_id != b.evidence_id


def test_make_evidence_record_changes_id_when_step_index_changes() -> None:
    args: dict[str, Any] = {
        "seed": Seed(0),
        "evidence_key": "k",
        "step_index": 0,
        "agent_id": "agent",
        "payload": {"x": 1},
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    a = make_evidence_record(**args)
    b = make_evidence_record(**{**args, "step_index": 1})
    assert a.evidence_id != b.evidence_id


def test_make_evidence_record_id_does_not_depend_on_agent_id() -> None:
    args: dict[str, Any] = {
        "seed": Seed(0),
        "evidence_key": "k",
        "step_index": 0,
        "agent_id": "agent_a",
        "payload": {"x": 1},
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    a = make_evidence_record(**args)
    b = make_evidence_record(**{**args, "agent_id": "agent_b"})
    assert a.evidence_id == b.evidence_id


def test_make_evidence_record_id_does_not_depend_on_payload_or_created_at() -> None:
    args: dict[str, Any] = {
        "seed": Seed(0),
        "evidence_key": "k",
        "step_index": 0,
        "agent_id": "agent",
        "payload": {"x": 1},
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    a = make_evidence_record(**args)
    b = make_evidence_record(**{**args, "payload": {"x": 2}, "created_at": datetime(2026, 6, 1, tzinfo=UTC)})
    assert a.evidence_id == b.evidence_id


def test_make_evidence_record_id_changes_with_seed() -> None:
    args: dict[str, Any] = {
        "evidence_key": "k",
        "step_index": 0,
        "agent_id": "agent",
        "payload": {"x": 1},
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    a = make_evidence_record(seed=Seed(0), **args)
    b = make_evidence_record(seed=Seed(1), **args)
    assert a.evidence_id != b.evidence_id
