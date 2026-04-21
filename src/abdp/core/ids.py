"""Deterministic UUID helpers.

Determinism guarantee:
    Given the same validated seed, namespace UUID, and name string,
    deterministic_uuid() returns the same UUID across runs and processes.
"""

from __future__ import annotations

from uuid import UUID, uuid5

from abdp.core.types import Seed, validate_seed

__all__ = ["deterministic_uuid", "parse_uuid"]


def deterministic_uuid(seed: Seed, namespace: UUID, name: str) -> UUID:
    validated = validate_seed(seed)
    if not isinstance(namespace, UUID):
        raise TypeError(f"namespace must be UUID, got {type(namespace).__name__}")
    if not isinstance(name, str):
        raise TypeError(f"name must be str, got {type(name).__name__}")
    return uuid5(namespace, f"{int(validated)}\0{name}")


def parse_uuid(value: str) -> UUID:
    if not isinstance(value, str):
        raise TypeError(f"UUID value must be str, got {type(value).__name__}")
    try:
        return UUID(value)
    except ValueError:
        raise ValueError(f"Invalid UUID string: {value!r}") from None
