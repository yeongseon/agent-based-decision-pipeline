"""``EvidenceStore`` protocol exposed by ``abdp.evidence``.

An :class:`EvidenceStore` is the pluggable persistence contract used by
the simulation and evaluation pipeline to record evidence and claim
records and to assemble an :class:`abdp.evidence.AuditLog` once a
scenario run has been evaluated. The protocol is intentionally minimal:
implementations decide how to store records (in memory, on disk, in a
remote service) and how to derive deterministic ordering when
constructing an audit log.
"""

from typing import Protocol, runtime_checkable

from abdp.core import Seed
from abdp.evaluation import EvaluationSummary
from abdp.evidence.audit_log import AuditLog
from abdp.evidence.claim import ClaimRecord
from abdp.evidence.record import EvidenceRecord
from abdp.scenario import ScenarioRun
from abdp.simulation import ActionProposal, ParticipantState, SegmentState

__all__ = ["EvidenceStore"]


@runtime_checkable
class EvidenceStore[S: SegmentState, P: ParticipantState, A: ActionProposal](Protocol):
    """Pluggable persistence contract for evidence and claim records."""

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
