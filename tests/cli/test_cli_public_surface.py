"""Frozen public surface of the ``abdp.cli`` package."""

from __future__ import annotations

import pytest

import abdp.cli
from abdp.cli.loader import LoaderError, load_audit_log_factory

EXPECTED_PUBLIC_NAMES: tuple[str, ...] = ("LoaderError", "load_audit_log_factory")
EXPECTED_SOURCE_IDENTITY: dict[str, object] = {
    "LoaderError": LoaderError,
    "load_audit_log_factory": load_audit_log_factory,
}


def test_cli_package_all_lists_exact_expected_symbols() -> None:
    assert isinstance(abdp.cli.__all__, tuple)
    assert all(isinstance(name, str) for name in abdp.cli.__all__)
    assert abdp.cli.__all__ == EXPECTED_PUBLIC_NAMES


def test_cli_package_star_import_yields_exactly_the_public_surface() -> None:
    namespace: dict[str, object] = {}
    exec("from abdp.cli import *", namespace)
    namespace.pop("__builtins__", None)
    assert sorted(namespace.keys()) == sorted(EXPECTED_PUBLIC_NAMES)


def test_cli_package_namespace_exposes_only_approved_public_names() -> None:
    public_attrs = sorted(name for name in vars(abdp.cli) if not name.startswith("_"))
    assert public_attrs == sorted(EXPECTED_PUBLIC_NAMES)


def test_cli_package_has_module_docstring() -> None:
    doc = abdp.cli.__doc__
    assert isinstance(doc, str)
    assert doc.strip()


@pytest.mark.parametrize("name", list(EXPECTED_SOURCE_IDENTITY))
def test_cli_public_symbols_resolve_to_canonical_definitions(name: str) -> None:
    assert getattr(abdp.cli, name) is EXPECTED_SOURCE_IDENTITY[name]
