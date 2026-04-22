"""Snapshot manifest contract:

- ``SnapshotTier`` is the closed set of supported tiers: ``"bronze"``, ``"silver"``, and ``"gold"``.
- ``SnapshotManifest`` is an immutable record for snapshot manifest metadata.
- Construction is synchronous only.
- ``snapshot_id`` and ``parent_snapshot_id`` must be ``UUID`` instances; string parsing is out of scope.
- ``storage_key`` and ``content_hash`` must be non-empty when stripped of surrounding whitespace.
- ``created_at`` must be a timezone-aware UTC ``datetime``.
- ``seed`` is validated with ``validate_seed``.
- ``parent_snapshot_id`` may be ``None`` and otherwise must differ from ``snapshot_id``.
- No guarantees about persistence, serialization, storage backends, or thread safety.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal, get_args
from uuid import UUID

from abdp.core.types import Seed, validate_seed

__all__ = ["SnapshotManifest", "SnapshotTier"]

type SnapshotTier = Literal["bronze", "silver", "gold"]

_ALLOWED_TIERS: tuple[SnapshotTier, ...] = get_args(SnapshotTier.__value__)
_ZERO_OFFSET = timedelta(0)


@dataclass(frozen=True, slots=True, kw_only=True)
class SnapshotManifest:
    """SnapshotManifest contract:

    - Immutable dataclass record with slot-backed, keyword-only fields.
    - Stores manifest metadata exactly as provided after validation; no parsing, normalization, or I/O is performed.
    - Validation is limited to basic runtime type checks and field invariants.
    - Construction is synchronous only.
    - No guarantees about persistence or thread safety.
    """

    snapshot_id: UUID
    tier: SnapshotTier
    storage_key: str
    content_hash: str
    created_at: datetime
    seed: Seed
    parent_snapshot_id: UUID | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.snapshot_id, UUID):
            raise TypeError(f"snapshot_id must be UUID, got {type(self.snapshot_id).__name__}")

        if not isinstance(self.tier, str):
            raise TypeError(f"tier must be str, got {type(self.tier).__name__}")
        if self.tier not in _ALLOWED_TIERS:
            raise ValueError(f"tier must be one of {_ALLOWED_TIERS!r}, got {self.tier!r}")

        if not isinstance(self.storage_key, str):
            raise TypeError(f"storage_key must be str, got {type(self.storage_key).__name__}")
        if not self.storage_key.strip():
            raise ValueError("storage_key must not be empty or whitespace")

        if not isinstance(self.content_hash, str):
            raise TypeError(f"content_hash must be str, got {type(self.content_hash).__name__}")
        if not self.content_hash.strip():
            raise ValueError("content_hash must not be empty or whitespace")

        if not isinstance(self.created_at, datetime):
            raise TypeError(f"created_at must be datetime, got {type(self.created_at).__name__}")
        offset = self.created_at.utcoffset()
        if offset is None:
            raise ValueError("created_at must be timezone-aware")
        if offset != _ZERO_OFFSET:
            raise ValueError("created_at must be UTC")

        validate_seed(self.seed)

        if self.parent_snapshot_id is not None and not isinstance(self.parent_snapshot_id, UUID):
            raise TypeError(f"parent_snapshot_id must be UUID or None, got {type(self.parent_snapshot_id).__name__}")
        if self.parent_snapshot_id is not None and self.parent_snapshot_id == self.snapshot_id:
            raise ValueError("parent_snapshot_id must not equal snapshot_id")
