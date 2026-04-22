"""Conformance tests for the core manifest factory protocol contract."""

from __future__ import annotations

from typing import assert_type

from abdp.core import manifest_factory
from abdp.core.manifest_factory import ManifestFactory


class _ValidFactory:
    def create(self, payload: dict[str, int]) -> tuple[str, dict[str, int]]:
        return ("manifest", payload)


class _MissingCreate:
    pass


def test_manifest_factory_module_exports_manifest_factory() -> None:
    assert manifest_factory.__all__ == ["ManifestFactory"]
    assert manifest_factory.ManifestFactory is ManifestFactory


def test_manifest_factory_is_protocol() -> None:
    assert getattr(ManifestFactory, "_is_protocol", False) is True


def test_manifest_factory_is_runtime_checkable_and_accepts_minimal_structural_impl() -> None:
    dummy = _ValidFactory()
    assert isinstance(dummy, ManifestFactory) is True
    factory: ManifestFactory[dict[str, int], tuple[str, dict[str, int]]] = dummy
    result = factory.create({"a": 1})
    assert_type(result, tuple[str, dict[str, int]])
    assert result == ("manifest", {"a": 1})


def test_manifest_factory_runtime_check_rejects_missing_create() -> None:
    assert isinstance(_MissingCreate(), ManifestFactory) is False
