"""Conformance tests for the silver snapshot protocol contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import assert_type
from uuid import UUID

import abdp.data
from abdp.core.hashing import stable_hash
from abdp.core.types import validate_seed
from abdp.data import silver
from abdp.data.silver import SilverContract
from abdp.data.snapshot_manifest import SnapshotManifest

_SNAPSHOT_ID = UUID("11111111-1111-1111-1111-111111111111")
_CREATED_AT = datetime(2024, 1, 1, tzinfo=UTC)
_CONTENT_HASH = stable_hash({"value": 1})
_SEED = validate_seed(7)


def _make_manifest() -> SnapshotManifest:
    return SnapshotManifest(
        snapshot_id=_SNAPSHOT_ID,
        tier="silver",
        storage_key="snapshots/silver/example.json",
        content_hash=_CONTENT_HASH,
        created_at=_CREATED_AT,
        seed=_SEED,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class _ValidSilverRows:
    manifest: SnapshotManifest
    rows: tuple[dict[str, int], ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class _MissingManifest:
    rows: tuple[dict[str, int], ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class _MissingRows:
    manifest: SnapshotManifest


def test_silver_module_docstring_is_anchored_on_line_one() -> None:
    assert silver.__file__ is not None
    first_line = Path(silver.__file__).read_text(encoding="utf-8").splitlines()[0]
    assert first_line == '"""Silver snapshot contract:'


def test_silver_module_docstring_includes_contract_guards() -> None:
    doc = silver.__doc__ or ""
    assert "Silver snapshot contract:" in doc
    assert "Defines the normalized snapshot contract for the silver tier." in doc
    assert "Aggregation is out of scope for this tier." in doc
    assert "Runtime protocol checks are shallow" in doc


def test_silver_module_exports_public_symbols_only() -> None:
    assert silver.__all__ == ["SilverContract"]
    assert silver.SilverContract is SilverContract


def test_data_package_exports_silver_contract_publicly() -> None:
    assert abdp.data.__all__ == [
        "BronzeContract",
        "SilverContract",
        "SnapshotManifest",
        "SnapshotTier",
    ]
    assert abdp.data.SilverContract is SilverContract


def test_silver_contract_is_protocol() -> None:
    assert getattr(SilverContract, "_is_protocol", False) is True


def test_silver_contract_is_runtime_checkable_and_accepts_minimal_structural_impl() -> None:
    dummy = _ValidSilverRows(
        manifest=_make_manifest(),
        rows=({"agent_id": 1}, {"agent_id": 2}),
    )

    assert isinstance(dummy, SilverContract) is True

    contract: SilverContract[dict[str, int]] = dummy
    assert_type(contract, SilverContract[dict[str, int]])
    assert_type(contract.manifest, SnapshotManifest)
    assert_type(contract.rows, tuple[dict[str, int], ...])
    assert contract.manifest.tier == "silver"
    assert contract.rows == ({"agent_id": 1}, {"agent_id": 2})


def test_silver_contract_runtime_check_rejects_missing_manifest() -> None:
    assert isinstance(_MissingManifest(rows=({"agent_id": 1},)), SilverContract) is False


def test_silver_contract_runtime_check_rejects_missing_rows() -> None:
    assert isinstance(_MissingRows(manifest=_make_manifest()), SilverContract) is False
