"""Core manifest factory protocol contract:

- Defines the minimal core manifest-construction contract.
- Domain-neutral and generic over payload and manifest types.
- Synchronous only.
- Contract is ``create(payload) -> manifest``.
- Intended for structural typing in core; implementations live outside core.
- Runtime protocol checks are shallow: they verify attribute presence only and
  do not validate call signatures or generic type arguments.
- Exception behavior is intentionally unspecified.
- No guarantees about persistence, validation, idempotency, or thread safety.
- Does not prescribe snapshots, tiers, or any concrete manifest schema.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["ManifestFactory"]


@runtime_checkable
class ManifestFactory[PayloadT, ManifestT](Protocol):
    def create(self, payload: PayloadT) -> ManifestT: ...
