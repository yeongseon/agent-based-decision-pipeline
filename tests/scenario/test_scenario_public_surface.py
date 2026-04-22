from __future__ import annotations

import importlib
import inspect
import sys
from types import ModuleType

from abdp.scenario.resolver import ActionResolver

_APPROVED_PUBLIC_NAMES = ("ActionResolver",)


def _import_fresh_scenario_package() -> ModuleType:
    sys.modules.pop("abdp.scenario", None)
    return importlib.import_module("abdp.scenario")


def _public_names(module: ModuleType) -> list[str]:
    return [name for name, _ in inspect.getmembers(module) if not name.startswith("_")]


def test_scenario_package_dunder_all_matches_approved_public_surface() -> None:
    pkg = _import_fresh_scenario_package()
    assert pkg.__all__ == _APPROVED_PUBLIC_NAMES


def test_scenario_package_public_surface_matches_dunder_all() -> None:
    pkg = _import_fresh_scenario_package()
    assert tuple(_public_names(pkg)) == _APPROVED_PUBLIC_NAMES
    assert pkg.ActionResolver is ActionResolver
