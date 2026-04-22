"""Structural tests for ``abdp.evidence.EvidenceStore``."""

from typing import Any, cast, get_type_hints

from abdp.core import Seed
from abdp.evaluation import EvaluationSummary
from abdp.evidence import (
    AuditLog,
    ClaimRecord,
    EvidenceRecord,
    EvidenceStore,
)
from abdp.scenario import ScenarioRun
from abdp.simulation import ActionProposal, ParticipantState, SegmentState


def test_evidence_store_is_protocol() -> None:
    assert cast(Any, EvidenceStore)._is_protocol is True


def test_evidence_store_is_runtime_checkable() -> None:
    class _Impl:
        def record(self, record: EvidenceRecord) -> None:
            return None

        def record_claim(self, claim: ClaimRecord) -> None:
            return None

        def evidence(self) -> tuple[EvidenceRecord, ...]:
            return ()

        def claims(self) -> tuple[ClaimRecord, ...]:
            return ()

        def build_audit_log(
            self,
            *,
            scenario_key: str,
            seed: Seed,
            run: ScenarioRun[SegmentState, ParticipantState, ActionProposal],
            summary: EvaluationSummary,
        ) -> AuditLog[SegmentState, ParticipantState, ActionProposal]:
            raise NotImplementedError

    assert isinstance(_Impl(), EvidenceStore)


def test_evidence_store_rejects_non_conforming_object_at_runtime() -> None:
    class _NotStore:
        pass

    assert not isinstance(_NotStore(), EvidenceStore)


def test_evidence_store_rejects_object_missing_one_method_at_runtime() -> None:
    class _PartialStore:
        def record(self, record: EvidenceRecord) -> None:
            return None

        def record_claim(self, claim: ClaimRecord) -> None:
            return None

        def evidence(self) -> tuple[EvidenceRecord, ...]:
            return ()

        def claims(self) -> tuple[ClaimRecord, ...]:
            return ()

        # build_audit_log intentionally missing

    assert not isinstance(_PartialStore(), EvidenceStore)


def test_evidence_store_declares_expected_methods() -> None:
    expected = {
        "record",
        "record_claim",
        "evidence",
        "claims",
        "build_audit_log",
    }
    for name in expected:
        assert callable(getattr(EvidenceStore, name))


def test_evidence_store_record_signature() -> None:
    annotations = get_type_hints(EvidenceStore.record)
    assert annotations["record"] is EvidenceRecord
    assert annotations["return"] is type(None)


def test_evidence_store_record_claim_signature() -> None:
    annotations = get_type_hints(EvidenceStore.record_claim)
    assert annotations["claim"] is ClaimRecord
    assert annotations["return"] is type(None)


def test_evidence_store_evidence_returns_tuple_of_records() -> None:
    annotations = get_type_hints(EvidenceStore.evidence)
    assert annotations["return"] == tuple[EvidenceRecord, ...]


def test_evidence_store_claims_returns_tuple_of_claims() -> None:
    annotations = get_type_hints(EvidenceStore.claims)
    assert annotations["return"] == tuple[ClaimRecord, ...]


def test_evidence_store_build_audit_log_signature() -> None:
    annotations = get_type_hints(EvidenceStore.build_audit_log)
    assert annotations["scenario_key"] is str
    assert annotations["seed"] is Seed
    assert annotations["summary"] is EvaluationSummary
