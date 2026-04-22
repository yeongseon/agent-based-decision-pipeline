"""Segment state protocol contract:

- Defines the minimal identity-and-membership segment contract shared across simulation domains.
- Domain-neutral and simulation-agnostic.
- Contract consists of readable ``segment_id: str`` and ``participant_ids: tuple[str, ...]`` access only.
- ``segment_id`` introduces no domain semantics beyond segment identity.
- ``participant_ids`` is an immutable tuple of participant identifiers for generic grouping only;
  it does not imply scoring, transitions, or domain-specific grouping logic.
- Intended for structural typing in simulation; implementations live outside simulation.
- Runtime protocol checks are shallow: they verify attribute presence only and do not validate attribute types.
- The protocol does not require a stored field, a property setter, or mutation semantics.
- No guarantees about uniqueness, non-emptiness, persistence, serialization, or thread safety.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["SegmentState"]


@runtime_checkable
class SegmentState(Protocol):
    @property
    def segment_id(self) -> str: ...
    @property
    def participant_ids(self) -> tuple[str, ...]: ...
