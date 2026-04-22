"""Tests for ``abdp.evidence.InMemoryEvidenceStore``."""

from datetime import UTC, datetime
from uuid import UUID

import pytest

from abdp.core import Seed
from abdp.evaluation import EvaluationSummary, GateStatus
from abdp.evidence import (
    AuditLog,
    ClaimRecord,
    EvidenceRecord,
    EvidenceStore,
    InMemoryEvidenceStore,
)
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


def _run() -> ScenarioRun[SegmentState, ParticipantState, ActionProposal]:
    return ScenarioRun[SegmentState, ParticipantState, ActionProposal](
        scenario_key="k",
        seed=Seed(0),
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


def _claim(uuid_int: int = 100, evidence_ids: tuple[UUID, ...] = (UUID(int=1),)) -> ClaimRecord:
    return ClaimRecord(
        claim_id=UUID(int=uuid_int),
        statement="s",
        evidence_ids=evidence_ids,
        confidence=0.5,
        metadata={},
    )


def test_in_memory_store_starts_empty() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    assert store.evidence() == ()
    assert store.claims() == ()


def test_in_memory_store_conforms_to_evidence_store_protocol() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    assert isinstance(store, EvidenceStore)


def test_in_memory_store_preserves_evidence_insertion_order() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    e1 = _evidence(uuid_int=1)
    e2 = _evidence(uuid_int=2)
    e3 = _evidence(uuid_int=3)
    store.record(e2)
    store.record(e1)
    store.record(e3)
    assert store.evidence() == (e2, e1, e3)


def test_in_memory_store_preserves_claim_insertion_order() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    store.record(_evidence(uuid_int=1))
    c1 = _claim(uuid_int=100)
    c2 = _claim(uuid_int=200)
    store.record_claim(c2)
    store.record_claim(c1)
    assert store.claims() == (c2, c1)


def test_in_memory_store_rejects_duplicate_evidence_id() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    store.record(_evidence(uuid_int=1))
    with pytest.raises(ValueError, match="00000000-0000-0000-0000-000000000001"):
        store.record(_evidence(uuid_int=1))


def test_in_memory_store_duplicate_evidence_does_not_mutate_state() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    e = _evidence(uuid_int=1)
    store.record(e)
    with pytest.raises(ValueError):
        store.record(_evidence(uuid_int=1))
    assert store.evidence() == (e,)


def test_in_memory_store_rejects_duplicate_claim_id() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    store.record(_evidence(uuid_int=1))
    store.record_claim(_claim(uuid_int=100))
    with pytest.raises(ValueError, match="00000000-0000-0000-0000-000000000064"):
        store.record_claim(_claim(uuid_int=100))


def test_in_memory_store_rejects_claim_referencing_unknown_evidence() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    store.record(_evidence(uuid_int=1))
    with pytest.raises(ValueError, match="00000000-0000-0000-0000-000000000009"):
        store.record_claim(_claim(uuid_int=100, evidence_ids=(UUID(int=1), UUID(int=9))))


def test_in_memory_store_unknown_evidence_error_preserves_claim_order() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    store.record(_evidence(uuid_int=5))
    missing_a = UUID(int=99)
    missing_b = UUID(int=7)
    with pytest.raises(ValueError) as excinfo:
        store.record_claim(
            _claim(uuid_int=100, evidence_ids=(missing_a, UUID(int=5), missing_b)),
        )
    msg = str(excinfo.value)
    assert msg.index(str(missing_a)) < msg.index(str(missing_b))


def test_in_memory_store_failed_claim_does_not_reserve_claim_id() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    store.record(_evidence(uuid_int=1))
    with pytest.raises(ValueError):
        store.record_claim(_claim(uuid_int=100, evidence_ids=(UUID(int=99),)))
    assert store.claims() == ()
    valid = _claim(uuid_int=100, evidence_ids=(UUID(int=1),))
    store.record_claim(valid)
    assert store.claims() == (valid,)


def test_in_memory_store_accepts_claim_with_all_known_evidence_ids() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    store.record(_evidence(uuid_int=1))
    store.record(_evidence(uuid_int=2))
    claim = _claim(uuid_int=100, evidence_ids=(UUID(int=2), UUID(int=1)))
    store.record_claim(claim)
    assert store.claims() == (claim,)


def test_in_memory_store_evidence_returns_snapshot_unaffected_by_later_writes() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    e1 = _evidence(uuid_int=1)
    store.record(e1)
    snapshot = store.evidence()
    store.record(_evidence(uuid_int=2))
    assert snapshot == (e1,)


def test_in_memory_store_build_audit_log_returns_insertion_ordered_bundle() -> None:
    store: InMemoryEvidenceStore[SegmentState, ParticipantState, ActionProposal] = InMemoryEvidenceStore()
    e1 = _evidence(uuid_int=1)
    e2 = _evidence(uuid_int=2)
    store.record(e1)
    store.record(e2)
    c1 = _claim(uuid_int=100, evidence_ids=(UUID(int=1),))
    c2 = _claim(uuid_int=200, evidence_ids=(UUID(int=2),))
    store.record_claim(c1)
    store.record_claim(c2)
    audit = store.build_audit_log(scenario_key="k", seed=Seed(0), run=_run(), summary=_summary())
    assert isinstance(audit, AuditLog)
    assert audit.scenario_key == "k"
    assert audit.seed == Seed(0)
    assert audit.evidence == (e1, e2)
    assert audit.claims == (c1, c2)
