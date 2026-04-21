"""Stable hashing helpers for JSON-like values.

Stable hashing contract:
    stable_hash() hashes canonical JSON content for deterministic comparison.
    It is for content hashing only, not for security signing, authentication,
    or encryption.
    Canonicalization sorts object keys, preserves array order, emits compact
    JSON, and hashes the UTF-8 bytes of that canonical serialization using
    ``_HASH_ALGORITHM``.
    No numeric normalization is performed, so values such as 1 and 1.0 hash
    differently.
"""

from __future__ import annotations

import hashlib
import json
from typing import Final

from abdp.core.types import JsonValue, is_json_value

__all__ = ["stable_hash"]

_HASH_ALGORITHM: Final = "sha256"


def _canonical_json_bytes(value: JsonValue) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,  # pragma: no mutate
        separators=(",", ":"),
        allow_nan=False,  # pragma: no mutate
    ).encode("utf-8")  # pragma: no mutate


def stable_hash(value: JsonValue) -> str:
    if not is_json_value(value):
        raise TypeError(f"value must be JSON-compatible, got {type(value).__name__}")
    return hashlib.new(_HASH_ALGORITHM, _canonical_json_bytes(value)).hexdigest()
