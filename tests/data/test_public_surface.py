"""Freeze the public surface for abdp.data."""

from __future__ import annotations

import importlib
import inspect
import sys
from types import ModuleType

_APPROVED_PUBLIC_NAMES = [
    "BronzeContract",
    "GoldContract",
    "SilverContract",
    "SnapshotManifest",
    "SnapshotTier",
]


def _import_fresh_data_package() -> ModuleType:
    sys.modules.pop("abdp.data", None)
    return importlib.import_module("abdp.data")


def _public_names(module: ModuleType) -> list[str]:
    return [name for name, _ in inspect.getmembers(module) if not name.startswith("_")]


def test_data_package_dunder_all_matches_approved_public_surface() -> None:
    data = _import_fresh_data_package()
    assert data.__all__ == _APPROVED_PUBLIC_NAMES


def test_data_package_public_surface_matches_dunder_all() -> None:
    data = _import_fresh_data_package()
    assert _public_names(data) == _APPROVED_PUBLIC_NAMES
