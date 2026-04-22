"""Public surface for the ``abdp.evidence`` package.

The evidence package owns the evidence record, claim record, audit log,
and store contracts. Exports are added to ``__all__`` issue by issue
against the frozen surface test in
``tests/evidence/test_evidence_public_surface.py``.
"""

from abdp.evidence.record import EvidenceRecord, make_evidence_record

globals().pop("record", None)

__all__: tuple[str, ...] = ("EvidenceRecord", "make_evidence_record")
