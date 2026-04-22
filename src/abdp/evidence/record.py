"""``EvidenceRecord`` frozen dataclass and ``make_evidence_record`` factory exposed by ``abdp.evidence``.

An ``EvidenceRecord`` is an atomic fact captured during a run. Identity is
derived deterministically from ``evidence_key`` and ``step_index`` via a
private namespace UUID, so the same fact captured under the same seed
always shares an ``evidence_id``. ``created_at`` MUST be a timezone-aware
UTC ``datetime`` and is validated in ``__post_init__``; ``payload`` MUST
be JSON-serializable per ``abdp.core.types.JsonValue`` but is not
runtime-validated.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Final
from uuid import UUID

from abdp.core.ids import deterministic_uuid
from abdp.core.types import JsonValue, Seed

__all__ = ["EvidenceRecord", "make_evidence_record"]

_EVIDENCE_NAMESPACE: Final = UUID("6f1f8a78-2c2a-4f3a-8d3a-2b1f0a9e9c01")
_NAME_SEPARATOR: Final = "\0"


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """Atomic fact captured during a run."""

    evidence_id: UUID
    evidence_key: str
    step_index: int
    agent_id: str
    payload: JsonValue
    created_at: datetime

    def __post_init__(self) -> None:
        tzinfo = self.created_at.tzinfo
        if tzinfo is None or tzinfo.utcoffset(self.created_at) != timedelta(0):
            raise ValueError("created_at must be a timezone-aware UTC datetime")


def make_evidence_record(
    *,
    seed: Seed,
    evidence_key: str,
    step_index: int,
    agent_id: str,
    payload: JsonValue,
    created_at: datetime,
) -> EvidenceRecord:
    """Build an :class:`EvidenceRecord` with a deterministically derived ``evidence_id``.

    ``evidence_id`` is derived from ``seed``, the private evidence
    namespace, and ``f"{evidence_key}\\0{step_index}"``; ``agent_id``,
    ``payload``, and ``created_at`` are metadata and do not influence
    identity.
    """

    name = f"{evidence_key}{_NAME_SEPARATOR}{step_index}"
    evidence_id = deterministic_uuid(seed, _EVIDENCE_NAMESPACE, name)
    return EvidenceRecord(
        evidence_id=evidence_id,
        evidence_key=evidence_key,
        step_index=step_index,
        agent_id=agent_id,
        payload=payload,
        created_at=created_at,
    )
