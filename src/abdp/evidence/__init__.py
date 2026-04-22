"""Public surface for the ``abdp.evidence`` package.

The evidence package owns the evidence record, claim record, audit log,
and store contracts. The evidence record stage is the first concrete
export: :class:`EvidenceRecord` and :func:`make_evidence_record` provide
deterministic identity for atomic facts captured during a run. Further
exports are added to ``__all__`` issue by issue against the frozen
surface test in ``tests/evidence/test_evidence_public_surface.py``.
"""

from abdp.evidence.record import EvidenceRecord, make_evidence_record

globals().pop("record", None)

__all__: tuple[str, ...] = ("EvidenceRecord", "make_evidence_record")
