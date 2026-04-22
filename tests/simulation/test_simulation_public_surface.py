"""Freeze the public surface for abdp.simulation."""

from __future__ import annotations

import importlib
import inspect
import sys
from types import ModuleType

from abdp.simulation.participant_state import ParticipantState
from abdp.simulation.snapshot_ref import SnapshotRef

_APPROVED_PUBLIC_NAMES = ["ParticipantState", "SnapshotRef"]


def _import_fresh_simulation_package() -> ModuleType:
    sys.modules.pop("abdp.simulation", None)
    return importlib.import_module("abdp.simulation")


def _public_names(module: ModuleType) -> list[str]:
    return [name for name, _ in inspect.getmembers(module) if not name.startswith("_")]


def test_simulation_package_dunder_all_matches_approved_public_surface() -> None:
    pkg = _import_fresh_simulation_package()
    assert pkg.__all__ == _APPROVED_PUBLIC_NAMES


def test_simulation_package_public_surface_matches_dunder_all() -> None:
    pkg = _import_fresh_simulation_package()
    assert _public_names(pkg) == _APPROVED_PUBLIC_NAMES
    assert pkg.ParticipantState is ParticipantState
    assert pkg.SnapshotRef is SnapshotRef
