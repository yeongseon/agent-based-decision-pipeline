"""Data storage protocol contract:

- Defines the minimal byte-oriented storage contract.
- Domain-neutral and backend-agnostic.
- Synchronous only.
- Contract consists of ``write_bytes(key, data)``, ``read_bytes(key) -> bytes``,
  and ``exists(key) -> bool``.
- Intended for structural typing in data; implementations live outside data.
- Runtime protocol checks are shallow: they verify attribute presence only and
  do not validate call signatures or generic type arguments.
- Exception behavior is intentionally unspecified.
- No guarantees about overwrite behavior, atomicity, durability, or thread safety.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["StorageProtocol"]


@runtime_checkable
class StorageProtocol(Protocol):
    def write_bytes(self, key: str, data: bytes) -> None: ...
    def read_bytes(self, key: str) -> bytes: ...
    def exists(self, key: str) -> bool: ...
