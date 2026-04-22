"""Frozen public surface of the ``abdp.core`` package."""

from __future__ import annotations

import abdp.core
from abdp.core import connectors as connectors_module
from abdp.core import hashing as hashing_module
from abdp.core import ids as ids_module
from abdp.core import manifest_factory as manifest_factory_module
from abdp.core import rate_limit as rate_limit_module
from abdp.core import retry as retry_module
from abdp.core import types as types_module

EXPECTED_PUBLIC_NAMES: list[str] = [
    "Backoff",
    "Clock",
    "Connector",
    "FixedWindowRateLimiter",
    "JsonObject",
    "JsonPrimitive",
    "JsonValue",
    "ManifestFactory",
    "Seed",
    "deterministic_uuid",
    "is_json_value",
    "parse_uuid",
    "retry",
    "stable_hash",
    "validate_seed",
]

EXPECTED_SOURCE_IDENTITY: dict[str, object] = {
    "Backoff": retry_module.Backoff,
    "Clock": rate_limit_module.Clock,
    "Connector": connectors_module.Connector,
    "FixedWindowRateLimiter": rate_limit_module.FixedWindowRateLimiter,
    "JsonObject": types_module.JsonObject,
    "JsonPrimitive": types_module.JsonPrimitive,
    "JsonValue": types_module.JsonValue,
    "ManifestFactory": manifest_factory_module.ManifestFactory,
    "Seed": types_module.Seed,
    "deterministic_uuid": ids_module.deterministic_uuid,
    "is_json_value": types_module.is_json_value,
    "parse_uuid": ids_module.parse_uuid,
    "retry": retry_module.retry,
    "stable_hash": hashing_module.stable_hash,
    "validate_seed": types_module.validate_seed,
}

REPRESENTATIVE_INTERNAL_NAMES: list[str] = [
    "_validate_init",
    "_validate_clock_reading",
    "_MIN_MAX_CALLS",
    "_validate_config",
    "_UINT32_MAX",
]


def test_core_package_all_lists_exact_expected_symbols() -> None:
    assert abdp.core.__all__ == EXPECTED_PUBLIC_NAMES


def test_core_package_exposes_each_listed_symbol_with_source_identity() -> None:
    for name in EXPECTED_PUBLIC_NAMES:
        attr = getattr(abdp.core, name)
        assert attr is EXPECTED_SOURCE_IDENTITY[name]


def test_core_package_does_not_leak_representative_internal_helpers() -> None:
    for name in REPRESENTATIVE_INTERNAL_NAMES:
        assert not hasattr(abdp.core, name)


def test_core_package_star_import_yields_exactly_the_public_surface() -> None:
    namespace: dict[str, object] = {}
    exec("from abdp.core import *", namespace)
    namespace.pop("__builtins__", None)
    assert sorted(namespace.keys()) == sorted(EXPECTED_PUBLIC_NAMES)
