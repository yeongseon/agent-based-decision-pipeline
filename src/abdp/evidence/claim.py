"""``ClaimRecord`` frozen dataclass and ``make_claim_record`` factory exposed by ``abdp.evidence``.

A ``ClaimRecord`` represents a higher-level conclusion backed by one or
more :class:`~abdp.evidence.EvidenceRecord` instances. ``claim_id`` is
derived deterministically from ``statement`` and the ordered
``evidence_ids`` via a private namespace UUID, so the same claim
composition under the same seed always shares a ``claim_id``;
``confidence`` and ``metadata`` are attributes of the claim and do not
affect identity. ``confidence`` MUST be a finite ``float`` in
``[0.0, 1.0]`` and ``evidence_ids`` MUST be non-empty; both invariants
are validated in ``__post_init__``.
"""

import math
from dataclasses import dataclass
from typing import Final
from uuid import UUID

from abdp.core.ids import deterministic_uuid
from abdp.core.types import JsonObject, Seed

__all__ = ["ClaimRecord", "make_claim_record"]

_CLAIM_NAMESPACE: Final = UUID("8b4e6c20-1f3a-4b7d-9c2e-7f5d8a4b1c3e")
_NAME_SEPARATOR: Final = "\0"


@dataclass(frozen=True, slots=True)
class ClaimRecord:
    """Higher-level conclusion backed by one or more evidence records."""

    claim_id: UUID
    statement: str
    evidence_ids: tuple[UUID, ...]
    confidence: float
    metadata: JsonObject

    def __post_init__(self) -> None:
        if len(self.evidence_ids) < 1:
            raise ValueError("evidence_ids must contain at least one UUID")
        if not math.isfinite(self.confidence) or not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be finite and between 0.0 and 1.0")


def make_claim_record(
    *,
    seed: Seed,
    statement: str,
    evidence_ids: tuple[UUID, ...],
    confidence: float,
    metadata: JsonObject,
) -> ClaimRecord:
    """Build a :class:`ClaimRecord` with a deterministically derived ``claim_id``.

    ``claim_id`` is derived from ``seed``, the private claim namespace,
    and ``statement`` joined to each evidence id by NUL separators in
    the supplied order; ``confidence`` and ``metadata`` are attributes
    of the claim and do not influence identity.
    """
    parts = [statement, *(str(evidence_id) for evidence_id in evidence_ids)]
    name = _NAME_SEPARATOR.join(parts)
    claim_id = deterministic_uuid(seed, _CLAIM_NAMESPACE, name)
    return ClaimRecord(
        claim_id=claim_id,
        statement=statement,
        evidence_ids=evidence_ids,
        confidence=confidence,
        metadata=metadata,
    )
