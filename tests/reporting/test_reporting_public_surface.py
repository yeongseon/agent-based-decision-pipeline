"""Frozen public surface of the ``abdp.reporting`` package."""

from __future__ import annotations

import pytest

import abdp.reporting
from abdp.reporting.json_renderer import render_json_report
from abdp.reporting.markdown_renderer import render_markdown_report

EXPECTED_PUBLIC_NAMES: tuple[str, ...] = ("render_json_report", "render_markdown_report")
EXPECTED_SOURCE_IDENTITY: dict[str, object] = {
    "render_json_report": render_json_report,
    "render_markdown_report": render_markdown_report,
}


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


@pytest.mark.parametrize("name", list(EXPECTED_SOURCE_IDENTITY))
def test_reporting_public_symbols_resolve_to_canonical_definitions(name: str) -> None:
    assert getattr(abdp.reporting, name) is EXPECTED_SOURCE_IDENTITY[name]
