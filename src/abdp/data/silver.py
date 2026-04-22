"""Silver snapshot contract:

- Defines the normalized snapshot contract for the silver tier.
- Domain-neutral and row-shape-agnostic.
- Contract consists of ``manifest: SnapshotManifest`` and ``rows: tuple[RowT, ...]``.
- ``manifest`` references snapshot metadata, but tier-specific validation is out of scope for
  this structural contract.
- ``rows`` must be exposed as an immutable tuple; row contents are not validated, copied, or
  further interpreted by this protocol.
- The silver tier represents normalized rows, but this contract does not define how
  normalization is performed or verified.
- Aggregation is out of scope for this tier.
- No schema enforcement, deduplication, or ordering semantics are implied for ``RowT`` values.
- Synchronous access only.
- Runtime protocol checks are shallow: they verify attribute presence only and do not validate
  attribute values or generic type arguments.
- No guarantees about persistence, serialization, storage backends, or thread safety.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from abdp.data.snapshot_manifest import SnapshotManifest

__all__ = ["SilverContract"]


@runtime_checkable
class SilverContract[RowT](Protocol):
    @property
    def manifest(self) -> SnapshotManifest: ...

    @property
    def rows(self) -> tuple[RowT, ...]: ...
