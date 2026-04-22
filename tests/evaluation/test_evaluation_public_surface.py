"""Frozen public surface of the ``abdp.evaluation`` package."""

from __future__ import annotations

import abdp.evaluation
import pytest

EXPECTED_PUBLIC_NAMES: tuple[str, ...] = ()

EXPECTED_SOURCE_IDENTITY: dict[str, object] = {}


def test_evaluation_package_all_lists_exact_expected_symbols() -> None:
    assert isinstance(abdp.evaluation.__all__, tuple)
    assert all(isinstance(name, str) for name in abdp.evaluation.__all__)
    assert abdp.evaluation.__all__ == EXPECTED_PUBLIC_NAMES


@pytest.mark.parametrize("name", EXPECTED_PUBLIC_NAMES)
def test_evaluation_package_exposes_symbol_with_source_identity(name: str) -> None:
    assert getattr(abdp.evaluation, name) is EXPECTED_SOURCE_IDENTITY[name]


def test_evaluation_package_star_import_yields_exactly_the_public_surface() -> None:
    namespace: dict[str, object] = {}
    exec("from abdp.evaluation import *", namespace)
    namespace.pop("__builtins__", None)
    assert sorted(namespace.keys()) == sorted(EXPECTED_PUBLIC_NAMES)


def test_evaluation_package_namespace_exposes_only_approved_public_names() -> None:
    public_attrs = sorted(name for name in vars(abdp.evaluation) if not name.startswith("_"))
    assert public_attrs == sorted(EXPECTED_PUBLIC_NAMES)


def test_evaluation_package_has_module_docstring() -> None:
    doc = abdp.evaluation.__doc__
    assert isinstance(doc, str)
    assert doc.strip()
