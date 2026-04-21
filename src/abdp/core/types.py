"""Shared core value types.

Seed is the reproducibility anchor for randomness across the framework.
This module also defines JSON-like value aliases and a runtime guard.
"""

from __future__ import annotations

import math
from typing import NewType, TypeGuard

__all__ = [
    "JsonObject",
    "JsonPrimitive",
    "JsonValue",
    "Seed",
    "is_json_value",
    "validate_seed",
]

_UINT32_MAX = 2**32 - 1

Seed = NewType("Seed", int)

type JsonPrimitive = None | bool | int | float | str
type JsonObject = dict[str, JsonValue]
type JsonValue = JsonPrimitive | JsonObject | list[JsonValue]


def validate_seed(value: object) -> Seed:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"Seed must be a non-bool int, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"Seed must be >= 0, got {value}")
    if value > _UINT32_MAX:
        raise ValueError(f"Seed must be <= {_UINT32_MAX}, got {value}")
    return Seed(value)


def is_json_value(obj: object) -> TypeGuard[JsonValue]:
    return _is_json_value(obj, set())


def _is_json_value(obj: object, ancestors: set[int]) -> bool:
    if obj is None:
        return True
    if isinstance(obj, bool):
        return True
    if isinstance(obj, str):
        return True
    if isinstance(obj, int):
        return True
    if isinstance(obj, float):
        return math.isfinite(obj)
    if isinstance(obj, list):
        obj_id = id(obj)
        if obj_id in ancestors:
            return False
        ancestors.add(obj_id)
        try:
            return all(_is_json_value(item, ancestors) for item in obj)
        finally:
            ancestors.discard(obj_id)
    if isinstance(obj, dict):
        obj_id = id(obj)
        if obj_id in ancestors:
            return False
        ancestors.add(obj_id)
        try:
            return all(isinstance(key, str) and _is_json_value(value, ancestors) for key, value in obj.items())
        finally:
            ancestors.discard(obj_id)
    return False
