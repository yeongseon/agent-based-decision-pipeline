"""``EvidenceStore`` protocol and in-memory implementation exposed by ``abdp.evidence``.

An :class:`EvidenceStore` is the pluggable persistence contract used by
the simulation and evaluation pipeline to record evidence and claim
records and to assemble an :class:`abdp.evidence.AuditLog` once a
scenario run has been evaluated. The protocol is intentionally minimal:
implementations decide how to store records (in memory, on disk, in a
remote service) and how to derive deterministic ordering when
constructing an audit log. :class:`InMemoryEvidenceStore` is the
reference implementation backed by insertion-ordered dictionaries.
"""

from typing import Protocol, runtime_checkable
from uuid import UUID

from abdp.core import Seed
from abdp.evaluation import EvaluationSummary
from abdp.evidence.audit_log import AuditLog
from abdp.evidence.claim import ClaimRecord
from abdp.evidence.record import EvidenceRecord
from abdp.scenario import ScenarioRun
from abdp.simulation import ActionProposal, ParticipantState, SegmentState

__all__ = ["EvidenceStore", "InMemoryEvidenceStore"]


@runtime_checkable
class EvidenceStore[S: SegmentState, P: ParticipantState, A: ActionProposal](Protocol):
    """Pluggable persistence contract for evidence and claim records.

    Implementations MUST preserve every record passed to :meth:`record`
    and :meth:`record_claim` so that subsequent calls to :meth:`evidence`
    and :meth:`claims` can return them as tuples. Ordering, idempotency,
    and durability semantics are implementation-defined; deterministic
    ordering for audit logs is the implementation's responsibility.
    """

    def record(self, record: EvidenceRecord) -> None:
        """Persist ``record`` in the store."""

        ...  # pragma: no cover

    def record_claim(self, claim: ClaimRecord) -> None:
        """Persist ``claim`` in the store."""

        ...  # pragma: no cover

    def evidence(self) -> tuple[EvidenceRecord, ...]:
        """Return all persisted evidence records."""

        ...  # pragma: no cover

    def claims(self) -> tuple[ClaimRecord, ...]:
        """Return all persisted claim records."""

        ...  # pragma: no cover

    def build_audit_log(
        self,
        *,
        scenario_key: str,
        seed: Seed,
        run: ScenarioRun[S, P, A],
        summary: EvaluationSummary,
    ) -> AuditLog[S, P, A]:
        """Bundle stored records with ``run`` and ``summary`` into an audit log."""

        ...  # pragma: no cover


class InMemoryEvidenceStore[S: SegmentState, P: ParticipantState, A: ActionProposal]:
    """Insertion-ordered, in-memory implementation of :class:`EvidenceStore`.

    Records are kept in insertion order using ``dict`` storage, which
    provides duplicate-id detection and membership lookup in one
    structure. ``record`` and ``record_claim`` validate inputs before
    mutating state, so a rejected write leaves the store unchanged.
    Returned tuples are snapshots: subsequent writes do not affect
    previously returned tuples. Not thread-safe.
    """

    def __init__(self) -> None:
        self._evidence: dict[UUID, EvidenceRecord] = {}
        self._claims: dict[UUID, ClaimRecord] = {}

    def record(self, record: EvidenceRecord) -> None:
        if record.evidence_id in self._evidence:
            raise ValueError(f"duplicate evidence_id: {record.evidence_id}")
        self._evidence[record.evidence_id] = record

    def record_claim(self, claim: ClaimRecord) -> None:
        if claim.claim_id in self._claims:
            raise ValueError(f"duplicate claim_id: {claim.claim_id}")
        missing = tuple(eid for eid in claim.evidence_ids if eid not in self._evidence)
        if missing:
            raise ValueError(f"claim references unknown evidence_ids: {missing}")
        self._claims[claim.claim_id] = claim

    def evidence(self) -> tuple[EvidenceRecord, ...]:
        return tuple(self._evidence.values())

    def claims(self) -> tuple[ClaimRecord, ...]:
        return tuple(self._claims.values())

    def build_audit_log(
        self,
        *,
        scenario_key: str,
        seed: Seed,
        run: ScenarioRun[S, P, A],
        summary: EvaluationSummary,
    ) -> AuditLog[S, P, A]:
        return AuditLog[S, P, A](
            scenario_key=scenario_key,
            seed=seed,
            run=run,
            summary=summary,
            evidence=self.evidence(),
            claims=self.claims(),
        )
