"""Contract tests for the SnapshotRef reference model."""

from __future__ import annotations

import dataclasses
import importlib
import inspect
import sys
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from types import ModuleType
from typing import assert_type, cast
from uuid import UUID

import pytest

from abdp.core.hashing import stable_hash
from abdp.core.types import Seed, validate_seed
from abdp.data.snapshot_manifest import SnapshotManifest, SnapshotTier
from abdp.simulation import snapshot_ref as sr
from abdp.simulation.snapshot_ref import SnapshotRef

_SNAPSHOT_ID = UUID("11111111-1111-1111-1111-111111111111")
_OTHER_SNAPSHOT_ID = UUID("33333333-3333-3333-3333-333333333333")
_CREATED_AT = datetime(2024, 1, 1, tzinfo=UTC)
_DEFAULT_CONTENT_HASH = stable_hash({"value": 1})
_DEFAULT_SEED = validate_seed(7)
_STORAGE_KEY = "snapshots/bronze/example.json"
_OTHER_STORAGE_KEY = "snapshots/bronze/other.json"

_APPROVED_PUBLIC_NAMES = ["SnapshotRef"]


def _make_manifest(
    *,
    snapshot_id: UUID = _SNAPSHOT_ID,
    tier: SnapshotTier = "bronze",
    storage_key: str = _STORAGE_KEY,
    content_hash: str = _DEFAULT_CONTENT_HASH,
    created_at: datetime = _CREATED_AT,
    seed: Seed = _DEFAULT_SEED,
    parent_snapshot_id: UUID | None = None,
) -> SnapshotManifest:
    return SnapshotManifest(
        snapshot_id=snapshot_id,
        tier=tier,
        storage_key=storage_key,
        content_hash=content_hash,
        created_at=created_at,
        seed=seed,
        parent_snapshot_id=parent_snapshot_id,
    )


def _make_ref(
    *,
    snapshot_id: UUID = _SNAPSHOT_ID,
    tier: SnapshotTier = "bronze",
    storage_key: str = _STORAGE_KEY,
) -> SnapshotRef:
    return SnapshotRef(snapshot_id=snapshot_id, tier=tier, storage_key=storage_key)


def _import_fresh_simulation_package() -> ModuleType:
    sys.modules.pop("abdp.simulation", None)
    return importlib.import_module("abdp.simulation")


def _public_names(module: ModuleType) -> list[str]:
    return [name for name, _ in inspect.getmembers(module) if not name.startswith("_")]


def test_snapshot_ref_module_docstring_includes_contract_anchor() -> None:
    doc = sr.__doc__ or ""
    assert "Snapshot reference contract:" in doc
    assert "Priority-3 role" in doc
    assert "No guarantees about persistence" in doc


def test_snapshot_ref_module_exports_public_symbols_only() -> None:
    assert sr.__all__ == ["SnapshotRef"]
    assert sr.SnapshotRef is SnapshotRef


def test_simulation_package_dunder_all_matches_approved_public_surface() -> None:
    pkg = _import_fresh_simulation_package()
    assert pkg.__all__ == _APPROVED_PUBLIC_NAMES


def test_simulation_package_public_surface_matches_dunder_all() -> None:
    pkg = _import_fresh_simulation_package()
    assert _public_names(pkg) == _APPROVED_PUBLIC_NAMES
    assert pkg.SnapshotRef is SnapshotRef


def test_snapshot_ref_class_docstring_includes_contract_anchor() -> None:
    doc = SnapshotRef.__doc__ or ""
    assert "SnapshotRef contract:" in doc
    assert "does not load, parse, or verify snapshot contents" in doc


def test_snapshot_ref_constructs_valid_reference() -> None:
    ref = _make_ref()
    assert ref.snapshot_id == _SNAPSHOT_ID
    assert ref.tier == "bronze"
    assert ref.storage_key == _STORAGE_KEY


def test_snapshot_ref_from_manifest_preserves_reference_fields_only() -> None:
    manifest = _make_manifest(tier="silver")
    ref = SnapshotRef.from_manifest(manifest)
    assert ref.snapshot_id == manifest.snapshot_id
    assert ref.tier == manifest.tier
    assert ref.storage_key == manifest.storage_key


def test_snapshot_ref_field_set_excludes_non_reference_manifest_metadata() -> None:
    field_names = {field.name for field in dataclasses.fields(SnapshotRef)}
    assert field_names == {"snapshot_id", "tier", "storage_key"}


def test_snapshot_ref_from_manifest_returns_snapshot_ref() -> None:
    manifest = _make_manifest()
    ref = SnapshotRef.from_manifest(manifest)
    assert_type(ref, SnapshotRef)
    assert isinstance(ref, SnapshotRef)


def test_snapshot_ref_is_frozen() -> None:
    ref = _make_ref()
    with pytest.raises(FrozenInstanceError):
        setattr(ref, "tier", "silver")  # noqa: B010


def test_snapshot_ref_equal_instances_compare_equal_and_have_same_hash() -> None:
    a = _make_ref()
    b = _make_ref()
    assert a == b
    assert hash(a) == hash(b)


def test_snapshot_ref_equality_is_structural_not_snapshot_id_only() -> None:
    base = _make_ref()
    different_tier = _make_ref(tier="silver")
    different_storage_key = _make_ref(storage_key=_OTHER_STORAGE_KEY)
    assert base != different_tier
    assert base != different_storage_key


def test_snapshot_ref_is_hashable() -> None:
    a = _make_ref()
    b = _make_ref()
    different = _make_ref(snapshot_id=_OTHER_SNAPSHOT_ID)
    collected = {a, b}
    assert collected == {a}
    collected.add(different)
    assert len(collected) == 2


def test_snapshot_ref_rejects_non_uuid_snapshot_id() -> None:
    with pytest.raises(TypeError, match=r"^snapshot_id must be UUID, got str$"):
        _make_ref(snapshot_id=cast(UUID, str(_SNAPSHOT_ID)))


def test_snapshot_ref_rejects_non_string_tier() -> None:
    with pytest.raises(TypeError, match=r"^tier must be str, got int$"):
        _make_ref(tier=cast(SnapshotTier, 1))


def test_snapshot_ref_rejects_unknown_tier() -> None:
    with pytest.raises(
        ValueError,
        match=r"^tier must be one of \('bronze', 'silver', 'gold'\), got 'platinum'$",
    ):
        _make_ref(tier=cast(SnapshotTier, "platinum"))


def test_snapshot_ref_rejects_non_string_storage_key() -> None:
    with pytest.raises(TypeError, match=r"^storage_key must be str, got int$"):
        _make_ref(storage_key=cast(str, 1))


def test_snapshot_ref_rejects_empty_storage_key() -> None:
    with pytest.raises(ValueError, match=r"^storage_key must not be empty or whitespace$"):
        _make_ref(storage_key="")


def test_snapshot_ref_rejects_whitespace_only_storage_key() -> None:
    with pytest.raises(ValueError, match=r"^storage_key must not be empty or whitespace$"):
        _make_ref(storage_key="   ")
