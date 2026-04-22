"""Tests for ``abdp.evidence.AuditLog``."""

import dataclasses
from datetime import UTC, datetime
from typing import Any, cast, get_type_hints
from uuid import UUID

import pytest

from abdp.core import Seed
from abdp.evaluation import EvaluationSummary, GateStatus
from abdp.evidence import AuditLog, ClaimRecord, EvidenceRecord
from abdp.scenario import ScenarioRun
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState
from abdp.simulation.snapshot_ref import SnapshotRef


def _state() -> SimulationState[SegmentState, ParticipantState, ActionProposal]:
    return SimulationState[SegmentState, ParticipantState, ActionProposal](
        step_index=0,
        seed=Seed(0),
        snapshot_ref=SnapshotRef(
            snapshot_id=UUID("00000000-0000-0000-0000-000000000001"),
            tier="bronze",
            storage_key="snapshots/run",
        ),
        segments=(),
        participants=(),
        pending_actions=(),
    )


def _run(
    scenario_key: str = "k",
    seed: Seed = Seed(0),
) -> ScenarioRun[SegmentState, ParticipantState, ActionProposal]:
    return ScenarioRun[SegmentState, ParticipantState, ActionProposal](
        scenario_key=scenario_key,
        seed=seed,
        steps=(),
        final_state=_state(),
    )


def _summary() -> EvaluationSummary:
    return EvaluationSummary(metrics=(), gates=(), overall_status=GateStatus.PASS)


def _evidence(uuid_int: int = 1) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=UUID(int=uuid_int),
        evidence_key="k",
        step_index=0,
        agent_id="agent",
        payload={"x": 1},
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _claim(uuid_int: int = 100) -> ClaimRecord:
    return ClaimRecord(
        claim_id=UUID(int=uuid_int),
        statement="s",
        evidence_ids=(UUID(int=1),),
        confidence=0.5,
        metadata={},
    )


def _audit(**overrides: Any) -> AuditLog[SegmentState, ParticipantState, ActionProposal]:
    base: dict[str, Any] = {
        "scenario_key": "k",
        "seed": Seed(0),
        "run": _run(),
        "summary": _summary(),
        "evidence": (_evidence(),),
        "claims": (_claim(),),
    }
    base.update(overrides)
    return AuditLog[SegmentState, ParticipantState, ActionProposal](**base)


def test_audit_log_is_frozen_dataclass() -> None:
    assert dataclasses.is_dataclass(AuditLog)
    params = cast(Any, AuditLog).__dataclass_params__
    assert params.frozen is True


def test_audit_log_uses_slots() -> None:
    assert "__slots__" in vars(AuditLog)


def test_audit_log_field_order() -> None:
    fields = dataclasses.fields(AuditLog)
    assert [f.name for f in fields] == [
        "scenario_key",
        "seed",
        "run",
        "summary",
        "evidence",
        "claims",
    ]


def test_audit_log_field_types_resolve() -> None:
    annotations = get_type_hints(AuditLog)
    assert annotations["scenario_key"] is str
    assert annotations["summary"] is EvaluationSummary


def test_audit_log_requires_all_fields() -> None:
    for field in dataclasses.fields(AuditLog):
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING


def test_audit_log_is_immutable() -> None:
    rec = _audit()
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(rec, "scenario_key", "other")  # noqa: B010


def test_audit_log_equality_is_value_based() -> None:
    a = _audit()
    b = _audit()
    assert a == b


def test_audit_log_preserves_evidence_order() -> None:
    e1 = _evidence(uuid_int=1)
    e2 = _evidence(uuid_int=2)
    rec = _audit(evidence=(e2, e1))
    assert rec.evidence == (e2, e1)


def test_audit_log_preserves_claims_order() -> None:
    c1 = _claim(uuid_int=100)
    c2 = _claim(uuid_int=200)
    rec = _audit(claims=(c2, c1))
    assert rec.claims == (c2, c1)


def test_audit_log_rejects_scenario_key_mismatch_with_run() -> None:
    with pytest.raises(ValueError, match="scenario_key"):
        _audit(scenario_key="other", run=_run(scenario_key="k"))


def test_audit_log_rejects_seed_mismatch_with_run() -> None:
    with pytest.raises(ValueError, match="seed"):
        _audit(seed=Seed(7), run=_run(seed=Seed(0)))


def test_audit_log_accepts_consistent_scenario_key_and_seed() -> None:
    rec = _audit(scenario_key="ok", seed=Seed(3), run=_run(scenario_key="ok", seed=Seed(3)))
    assert rec.scenario_key == "ok"
    assert rec.seed == Seed(3)
