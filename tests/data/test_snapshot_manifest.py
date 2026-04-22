from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from typing import Any, cast
from uuid import UUID

import pytest

import abdp.data
from abdp.core.hashing import stable_hash
from abdp.core.types import Seed, validate_seed
from abdp.data import snapshot_manifest as sm
from abdp.data.snapshot_manifest import SnapshotManifest, SnapshotTier

_SNAPSHOT_ID = UUID("11111111-1111-1111-1111-111111111111")
_PARENT_ID = UUID("22222222-2222-2222-2222-222222222222")
_CREATED_AT = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _make_manifest(**overrides: Any) -> SnapshotManifest:
    defaults: dict[str, Any] = {
        "snapshot_id": _SNAPSHOT_ID,
        "tier": "bronze",
        "storage_key": "snapshots/bronze/example.json",
        "content_hash": stable_hash({"value": 1}),
        "created_at": _CREATED_AT,
        "seed": validate_seed(7),
        "parent_snapshot_id": None,
    }
    defaults.update(overrides)
    return SnapshotManifest(**defaults)




def test_snapshot_manifest_module_docstring_includes_contract_anchor() -> None:
    doc = sm.__doc__ or ""
    assert "Snapshot manifest contract:" in doc
    assert "No guarantees about persistence" in doc


def test_snapshot_manifest_module_exports_public_symbols_only() -> None:
    assert sm.__all__ == ["SnapshotManifest", "SnapshotTier"]


def test_data_package_exports_snapshot_manifest_publicly() -> None:
    assert abdp.data.__all__ == ["SnapshotManifest", "SnapshotTier"]
    assert abdp.data.SnapshotManifest is SnapshotManifest
    assert abdp.data.SnapshotTier is SnapshotTier


def test_snapshot_manifest_class_docstring_includes_contract_anchor() -> None:
    doc = SnapshotManifest.__doc__ or ""
    assert "SnapshotManifest contract:" in doc
    assert "Construction is synchronous only" in doc




def test_snapshot_manifest_constructs_valid_root_record() -> None:
    manifest = _make_manifest()
    assert manifest.snapshot_id == _SNAPSHOT_ID
    assert manifest.tier == "bronze"
    assert manifest.storage_key == "snapshots/bronze/example.json"
    assert manifest.content_hash == stable_hash({"value": 1})
    assert manifest.created_at == _CREATED_AT
    assert manifest.seed == validate_seed(7)
    assert manifest.parent_snapshot_id is None


def test_snapshot_manifest_constructs_valid_child_record() -> None:
    manifest = _make_manifest(parent_snapshot_id=_PARENT_ID)
    assert manifest.parent_snapshot_id == _PARENT_ID


def test_snapshot_manifest_is_frozen() -> None:
    manifest = _make_manifest()
    with pytest.raises(FrozenInstanceError):
        cast(Any, manifest).tier = "silver"


def test_snapshot_manifest_equal_instances_compare_equal_and_have_same_hash() -> None:
    a = _make_manifest()
    b = _make_manifest()
    assert a == b
    assert hash(a) == hash(b)




@pytest.mark.parametrize("tier", ["bronze", "silver", "gold"])
def test_snapshot_manifest_accepts_each_supported_tier(tier: SnapshotTier) -> None:
    manifest = _make_manifest(tier=tier)
    assert manifest.tier == tier


def test_snapshot_manifest_rejects_non_string_tier() -> None:
    with pytest.raises(TypeError, match=r"^tier must be str, got int$"):
        _make_manifest(tier=cast(Any, 1))


def test_snapshot_manifest_rejects_unknown_tier() -> None:
    with pytest.raises(
        ValueError,
        match=r"^tier must be one of \('bronze', 'silver', 'gold'\), got 'platinum'$",
    ):
        _make_manifest(tier=cast(Any, "platinum"))




def test_snapshot_manifest_rejects_non_uuid_snapshot_id() -> None:
    with pytest.raises(TypeError, match=r"^snapshot_id must be UUID, got str$"):
        _make_manifest(snapshot_id=cast(Any, str(_SNAPSHOT_ID)))




def test_snapshot_manifest_rejects_non_string_storage_key() -> None:
    with pytest.raises(TypeError, match=r"^storage_key must be str, got int$"):
        _make_manifest(storage_key=cast(Any, 1))


def test_snapshot_manifest_rejects_empty_storage_key() -> None:
    with pytest.raises(ValueError, match=r"^storage_key must not be empty or whitespace$"):
        _make_manifest(storage_key="")


def test_snapshot_manifest_rejects_whitespace_only_storage_key() -> None:
    with pytest.raises(ValueError, match=r"^storage_key must not be empty or whitespace$"):
        _make_manifest(storage_key="   ")




def test_snapshot_manifest_rejects_non_string_content_hash() -> None:
    with pytest.raises(TypeError, match=r"^content_hash must be str, got int$"):
        _make_manifest(content_hash=cast(Any, 1))


def test_snapshot_manifest_rejects_empty_content_hash() -> None:
    with pytest.raises(ValueError, match=r"^content_hash must not be empty or whitespace$"):
        _make_manifest(content_hash="")


def test_snapshot_manifest_rejects_whitespace_only_content_hash() -> None:
    with pytest.raises(ValueError, match=r"^content_hash must not be empty or whitespace$"):
        _make_manifest(content_hash="   ")




def test_snapshot_manifest_rejects_non_datetime_created_at() -> None:
    with pytest.raises(TypeError, match=r"^created_at must be datetime, got str$"):
        _make_manifest(created_at=cast(Any, "2024-01-01T00:00:00Z"))


def test_snapshot_manifest_rejects_naive_created_at() -> None:
    with pytest.raises(ValueError, match=r"^created_at must be timezone-aware$"):
        _make_manifest(created_at=datetime(2024, 1, 1))  # noqa: DTZ001


def test_snapshot_manifest_rejects_non_utc_created_at() -> None:
    non_utc = datetime(2024, 1, 1, tzinfo=timezone(timedelta(hours=9)))
    with pytest.raises(ValueError, match=r"^created_at must be UTC$"):
        _make_manifest(created_at=non_utc)




def test_snapshot_manifest_delegates_seed_validation_for_non_integer_seed() -> None:
    with pytest.raises(TypeError, match=r"^Seed must be a non-bool int, got str$"):
        _make_manifest(seed=cast(Seed, "1"))


def test_snapshot_manifest_delegates_seed_validation_for_negative_seed() -> None:
    with pytest.raises(ValueError, match=r"^Seed must be >= 0, got -1$"):
        _make_manifest(seed=cast(Seed, -1))


def test_snapshot_manifest_delegates_seed_validation_for_seed_above_uint32_max() -> None:
    with pytest.raises(ValueError, match=r"^Seed must be <= 4294967295, got 4294967296$"):
        _make_manifest(seed=cast(Seed, 2**32))


def test_snapshot_manifest_delegates_seed_validation_for_bool_seed() -> None:
    with pytest.raises(TypeError, match=r"^Seed must be a non-bool int, got bool$"):
        _make_manifest(seed=cast(Seed, True))




def test_snapshot_manifest_rejects_non_uuid_parent_snapshot_id() -> None:
    with pytest.raises(TypeError, match=r"^parent_snapshot_id must be UUID or None, got str$"):
        _make_manifest(parent_snapshot_id=cast(Any, str(_PARENT_ID)))


def test_snapshot_manifest_rejects_parent_snapshot_id_matching_snapshot_id() -> None:
    with pytest.raises(ValueError, match=r"^parent_snapshot_id must not equal snapshot_id$"):
        _make_manifest(parent_snapshot_id=_SNAPSHOT_ID)
