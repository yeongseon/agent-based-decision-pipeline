"""Conformance tests for the bronze snapshot protocol contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import assert_type
from uuid import UUID

import abdp.data
from abdp.core.hashing import stable_hash
from abdp.core.types import validate_seed
from abdp.data import bronze
from abdp.data.bronze import BronzeContract
from abdp.data.snapshot_manifest import SnapshotManifest

_SNAPSHOT_ID = UUID("11111111-1111-1111-1111-111111111111")
_CREATED_AT = datetime(2024, 1, 1, tzinfo=UTC)
_CONTENT_HASH = stable_hash({"value": 1})
_SEED = validate_seed(7)


def _make_manifest() -> SnapshotManifest:
    return SnapshotManifest(
        snapshot_id=_SNAPSHOT_ID,
        tier="bronze",
        storage_key="snapshots/bronze/example.json",
        content_hash=_CONTENT_HASH,
        created_at=_CREATED_AT,
        seed=_SEED,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class _ValidBronzeRows:
    manifest: SnapshotManifest
    rows: tuple[dict[str, int], ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class _MissingManifest:
    rows: tuple[dict[str, int], ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class _MissingRows:
    manifest: SnapshotManifest


def test_bronze_module_docstring_is_anchored_on_line_one() -> None:
    assert bronze.__file__ is not None
    first_line = Path(bronze.__file__).read_text(encoding="utf-8").splitlines()[0]
    assert first_line == '"""Bronze snapshot contract:'


def test_bronze_module_docstring_includes_contract_guards() -> None:
    doc = bronze.__doc__ or ""
    assert "Bronze snapshot contract:" in doc
    assert "No schema enforcement" in doc
    assert "Runtime protocol checks are shallow" in doc


def test_bronze_module_exports_public_symbols_only() -> None:
    assert bronze.__all__ == ["BronzeContract"]
    assert bronze.BronzeContract is BronzeContract


def test_data_package_exports_bronze_contract_publicly() -> None:
    assert abdp.data.__all__ == ["BronzeContract", "SnapshotManifest", "SnapshotTier"]
    assert abdp.data.BronzeContract is BronzeContract


def test_bronze_contract_is_protocol() -> None:
    assert getattr(BronzeContract, "_is_protocol", False) is True


def test_bronze_contract_is_runtime_checkable_and_accepts_minimal_structural_impl() -> None:
    dummy = _ValidBronzeRows(
        manifest=_make_manifest(),
        rows=({"agent_id": 1}, {"agent_id": 2}),
    )

    assert isinstance(dummy, BronzeContract) is True

    contract: BronzeContract[dict[str, int]] = dummy
    assert_type(contract, BronzeContract[dict[str, int]])
    assert_type(contract.manifest, SnapshotManifest)
    assert_type(contract.rows, tuple[dict[str, int], ...])
    assert contract.manifest.tier == "bronze"
    assert contract.rows == ({"agent_id": 1}, {"agent_id": 2})


def test_bronze_contract_runtime_check_rejects_missing_manifest() -> None:
    assert isinstance(_MissingManifest(rows=({"agent_id": 1},)), BronzeContract) is False


def test_bronze_contract_runtime_check_rejects_missing_rows() -> None:
    assert isinstance(_MissingRows(manifest=_make_manifest()), BronzeContract) is False
