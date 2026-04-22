"""Tests for ``abdp.evidence.ClaimRecord`` and ``make_claim_record``."""

import dataclasses
import math
from typing import Any, cast, get_type_hints
from uuid import UUID

import pytest

from abdp.core.types import Seed
from abdp.evidence import ClaimRecord, make_claim_record


def _claim(**overrides: Any) -> ClaimRecord:
    base: dict[str, Any] = {
        "claim_id": UUID("00000000-0000-0000-0000-000000000001"),
        "statement": "s",
        "evidence_ids": (UUID("00000000-0000-0000-0000-000000000010"),),
        "confidence": 0.5,
        "metadata": {"k": "v"},
    }
    base.update(overrides)
    return ClaimRecord(**base)


def test_claim_record_is_frozen_dataclass() -> None:
    assert dataclasses.is_dataclass(ClaimRecord)
    params = cast(Any, ClaimRecord).__dataclass_params__
    assert params.frozen is True


def test_claim_record_uses_slots() -> None:
    assert "__slots__" in vars(ClaimRecord)


def test_claim_record_field_order_and_types() -> None:
    fields = dataclasses.fields(ClaimRecord)
    assert [f.name for f in fields] == [
        "claim_id",
        "statement",
        "evidence_ids",
        "confidence",
        "metadata",
    ]
    annotations = get_type_hints(ClaimRecord)
    assert annotations["claim_id"] is UUID
    assert annotations["statement"] is str
    assert annotations["confidence"] is float


def test_claim_record_requires_all_fields() -> None:
    for field in dataclasses.fields(ClaimRecord):
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING


def test_claim_record_is_immutable() -> None:
    rec = _claim()
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(rec, "statement", "other")  # noqa: B010


def test_claim_record_equality_is_value_based() -> None:
    a = _claim()
    b = _claim()
    c = _claim(statement="other")
    assert a == b
    assert a != c


def test_claim_record_rejects_empty_evidence_ids() -> None:
    with pytest.raises(ValueError, match="evidence_ids"):
        _claim(evidence_ids=())


def test_claim_record_rejects_confidence_below_zero() -> None:
    with pytest.raises(ValueError, match="confidence"):
        _claim(confidence=-0.1)


def test_claim_record_rejects_confidence_above_one() -> None:
    with pytest.raises(ValueError, match="confidence"):
        _claim(confidence=1.1)


def test_claim_record_rejects_nan_confidence() -> None:
    with pytest.raises(ValueError, match="confidence"):
        _claim(confidence=math.nan)


def test_claim_record_rejects_inf_confidence() -> None:
    with pytest.raises(ValueError, match="confidence"):
        _claim(confidence=math.inf)


def test_claim_record_accepts_zero_confidence() -> None:
    rec = _claim(confidence=0.0)
    assert rec.confidence == 0.0


def test_claim_record_accepts_one_confidence() -> None:
    rec = _claim(confidence=1.0)
    assert rec.confidence == 1.0


def test_make_claim_record_returns_claim_record() -> None:
    rec = make_claim_record(
        seed=Seed(0),
        statement="s",
        evidence_ids=(UUID("00000000-0000-0000-0000-000000000010"),),
        confidence=0.5,
        metadata={"k": "v"},
    )
    assert isinstance(rec, ClaimRecord)
    assert isinstance(rec.claim_id, UUID)


def test_make_claim_record_is_deterministic_for_same_inputs() -> None:
    args: dict[str, Any] = {
        "seed": Seed(7),
        "statement": "s",
        "evidence_ids": (UUID("00000000-0000-0000-0000-000000000010"),),
        "confidence": 0.5,
        "metadata": {"k": "v"},
    }
    a = make_claim_record(**args)
    b = make_claim_record(**args)
    assert a.claim_id == b.claim_id


def test_make_claim_record_changes_id_when_statement_changes() -> None:
    args: dict[str, Any] = {
        "seed": Seed(0),
        "statement": "s1",
        "evidence_ids": (UUID("00000000-0000-0000-0000-000000000010"),),
        "confidence": 0.5,
        "metadata": {},
    }
    a = make_claim_record(**args)
    b = make_claim_record(**{**args, "statement": "s2"})
    assert a.claim_id != b.claim_id


def test_make_claim_record_changes_id_when_evidence_ids_change() -> None:
    args: dict[str, Any] = {
        "seed": Seed(0),
        "statement": "s",
        "evidence_ids": (UUID("00000000-0000-0000-0000-000000000010"),),
        "confidence": 0.5,
        "metadata": {},
    }
    a = make_claim_record(**args)
    b = make_claim_record(**{**args, "evidence_ids": (UUID("00000000-0000-0000-0000-000000000011"),)})
    assert a.claim_id != b.claim_id


def test_make_claim_record_id_does_not_depend_on_confidence_or_metadata() -> None:
    args: dict[str, Any] = {
        "seed": Seed(0),
        "statement": "s",
        "evidence_ids": (UUID("00000000-0000-0000-0000-000000000010"),),
        "confidence": 0.5,
        "metadata": {"k": "v"},
    }
    a = make_claim_record(**args)
    b = make_claim_record(**{**args, "confidence": 0.9, "metadata": {"x": "y"}})
    assert a.claim_id == b.claim_id


def test_make_claim_record_id_changes_with_seed() -> None:
    args: dict[str, Any] = {
        "statement": "s",
        "evidence_ids": (UUID("00000000-0000-0000-0000-000000000010"),),
        "confidence": 0.5,
        "metadata": {},
    }
    a = make_claim_record(seed=Seed(0), **args)
    b = make_claim_record(seed=Seed(1), **args)
    assert a.claim_id != b.claim_id


def test_make_claim_record_changes_id_when_evidence_ids_reorder() -> None:
    args: dict[str, Any] = {
        "seed": Seed(0),
        "statement": "s",
        "evidence_ids": (
            UUID("00000000-0000-0000-0000-000000000010"),
            UUID("00000000-0000-0000-0000-000000000011"),
        ),
        "confidence": 0.5,
        "metadata": {},
    }
    a = make_claim_record(**args)
    b = make_claim_record(
        **{
            **args,
            "evidence_ids": (
                UUID("00000000-0000-0000-0000-000000000011"),
                UUID("00000000-0000-0000-0000-000000000010"),
            ),
        }
    )
    assert a.claim_id != b.claim_id
    assert rec.claim_id == UUID("00000000-0000-0000-0000-000000000000") or isinstance(rec.claim_id, UUID)
