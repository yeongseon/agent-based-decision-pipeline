"""Frozen public surface of the ``abdp.reporting`` package."""

from __future__ import annotations

import abdp.reporting

EXPECTED_PUBLIC_NAMES: tuple[str, ...] = ()


def test_reporting_package_all_lists_exact_expected_symbols() -> None:
    assert isinstance(abdp.reporting.__all__, tuple)
    assert all(isinstance(name, str) for name in abdp.reporting.__all__)
    assert abdp.reporting.__all__ == EXPECTED_PUBLIC_NAMES


def test_reporting_package_star_import_yields_exactly_the_public_surface() -> None:
    namespace: dict[str, object] = {}
    exec("from abdp.reporting import *", namespace)
    namespace.pop("__builtins__", None)
    assert sorted(namespace.keys()) == sorted(EXPECTED_PUBLIC_NAMES)


def test_reporting_package_namespace_exposes_only_approved_public_names() -> None:
    public_attrs = sorted(name for name in vars(abdp.reporting) if not name.startswith("_"))
    assert public_attrs == sorted(EXPECTED_PUBLIC_NAMES)


def test_reporting_package_has_module_docstring() -> None:
    doc = abdp.reporting.__doc__
    assert isinstance(doc, str)
    assert doc.strip()
