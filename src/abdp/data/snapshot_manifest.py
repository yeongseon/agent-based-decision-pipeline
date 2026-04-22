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


def _validate_uuid(field_name: str, value: object) -> None:
    if not isinstance(value, UUID):
        raise TypeError(f"{field_name} must be UUID, got {type(value).__name__}")


def _validate_tier(value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"tier must be str, got {type(value).__name__}")
    if value not in _ALLOWED_TIERS:
        raise ValueError(f"tier must be one of {_ALLOWED_TIERS!r}, got {value!r}")


def _validate_non_empty_text(field_name: str, value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str, got {type(value).__name__}")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty or whitespace")


def _validate_created_at(value: object) -> None:
    if not isinstance(value, datetime):
        raise TypeError(f"created_at must be datetime, got {type(value).__name__}")
    offset = value.utcoffset()
    if offset is None:
        raise ValueError("created_at must be timezone-aware")
    if offset != _ZERO_OFFSET:
        raise ValueError("created_at must be UTC")


def _validate_parent_snapshot_id(parent: object, snapshot_id: UUID) -> None:
    if parent is None:
        return
    if not isinstance(parent, UUID):
        raise TypeError(f"parent_snapshot_id must be UUID or None, got {type(parent).__name__}")
    if parent == snapshot_id:
        raise ValueError("parent_snapshot_id must not equal snapshot_id")


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
        _validate_uuid("snapshot_id", self.snapshot_id)
        _validate_tier(self.tier)
        _validate_non_empty_text("storage_key", self.storage_key)
        _validate_non_empty_text("content_hash", self.content_hash)
        _validate_created_at(self.created_at)
        validate_seed(self.seed)
        _validate_parent_snapshot_id(self.parent_snapshot_id, self.snapshot_id)
