"""Public surface of the ``abdp.core`` package.

Exposes the deterministic, domain-neutral building blocks of the framework:
JSON value types and seed validation, deterministic identifiers, stable
hashing, deterministic retry, fixed-window rate limiting, the connector
protocol, and the manifest factory protocol.
"""

from __future__ import annotations

from abdp.core.connectors import Connector
from abdp.core.hashing import stable_hash
from abdp.core.ids import deterministic_uuid, parse_uuid
from abdp.core.manifest_factory import ManifestFactory
from abdp.core.rate_limit import Clock, FixedWindowRateLimiter
from abdp.core.retry import Backoff, retry
from abdp.core.types import (
    JsonObject,
    JsonPrimitive,
    JsonValue,
    Seed,
    is_json_value,
    validate_seed,
)

__all__ = [
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
