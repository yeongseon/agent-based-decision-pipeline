"""Snapshot reference contract:

- Priority-3 role: simulation state carries lightweight pointers to snapshots without loading snapshot contents.
- ``SnapshotRef`` is an immutable reference model for locating an existing snapshot.
- Contract consists of ``snapshot_id``, ``tier``, and ``storage_key`` only.
- ``snapshot_id`` must be a ``UUID`` instance; string parsing is out of scope.
- ``tier`` must be one of ``"bronze"``, ``"silver"``, or ``"gold"``.
- ``storage_key`` must be non-empty when stripped of surrounding whitespace.
- ``from_manifest(...)`` projects only reference fields from ``SnapshotManifest`` and performs no I/O.
- ``content_hash``, ``created_at``, ``seed``, and ``parent_snapshot_id`` are intentionally excluded.
- No guarantees about persistence, storage existence, payload parsing, integrity verification, or thread safety.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self, get_args
from uuid import UUID

from abdp.data.snapshot_manifest import SnapshotManifest, SnapshotTier

__all__ = ["SnapshotRef"]

_ALLOWED_TIERS: tuple[SnapshotTier, ...] = get_args(SnapshotTier.__value__)


def _validate_uuid(field_name: str, value: object) -> None:
    if not isinstance(value, UUID):
        raise TypeError(f"{field_name} must be UUID, got {type(value).__name__}")


def _validate_tier(value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"tier must be str, got {type(value).__name__}")
    if value not in _ALLOWED_TIERS:
        raise ValueError(f"tier must be one of {_ALLOWED_TIERS!r}, got {value!r}")


def _validate_storage_key(value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"storage_key must be str, got {type(value).__name__}")
    if not value.strip():
        raise ValueError("storage_key must not be empty or whitespace")


@dataclass(frozen=True, slots=True, kw_only=True)
class SnapshotRef:
    """SnapshotRef contract:

    - Immutable dataclass record with slot-backed, keyword-only fields.
    - Represents a snapshot pointer only; it does not load, parse, or verify snapshot contents.
    - Stores reference fields exactly as provided after validation; no normalization or I/O is performed.
    - Validation is limited to basic runtime type checks and field invariants.
    - Construction is synchronous only.
    - No guarantees about storage existence, payload integrity, persistence, or thread safety.
    """

    snapshot_id: UUID
    tier: SnapshotTier
    storage_key: str

    def __post_init__(self) -> None:
        _validate_uuid("snapshot_id", self.snapshot_id)
        _validate_tier(self.tier)
        _validate_storage_key(self.storage_key)

    @classmethod
    def from_manifest(cls, manifest: SnapshotManifest) -> Self:
        return cls(
            snapshot_id=manifest.snapshot_id,
            tier=manifest.tier,
            storage_key=manifest.storage_key,
        )
