"""Public surface for the ``abdp.evidence`` package.

The evidence package owns the evidence record, claim record, audit log,
and store contracts. :class:`EvidenceRecord` / :func:`make_evidence_record`
and :class:`ClaimRecord` / :func:`make_claim_record` provide deterministic
identity for atomic facts and conclusions; :class:`AuditLog` aggregates a
scenario run with its evaluation summary, evidence, and claims;
:class:`EvidenceStore` is the pluggable persistence contract; and
:class:`InMemoryEvidenceStore` is the reference in-memory implementation.
Further exports are added to ``__all__`` issue by issue against the
frozen surface test in ``tests/evidence/test_evidence_public_surface.py``.
"""

from abdp.evidence.audit_log import AuditLog
from abdp.evidence.claim import ClaimRecord, make_claim_record
from abdp.evidence.record import EvidenceRecord, make_evidence_record
from abdp.evidence.store import EvidenceStore, InMemoryEvidenceStore

globals().pop("audit_log", None)
globals().pop("claim", None)
globals().pop("record", None)
globals().pop("store", None)

__all__: tuple[str, ...] = (
    "AuditLog",
    "ClaimRecord",
    "EvidenceRecord",
    "EvidenceStore",
    "InMemoryEvidenceStore",
    "make_claim_record",
    "make_evidence_record",
)
