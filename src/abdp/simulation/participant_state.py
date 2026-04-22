"""Participant state protocol contract:

- Defines the minimal identity-only participant contract shared across simulation domains.
- Domain-neutral and simulation-agnostic.
- Contract consists of readable ``participant_id: str`` access only.
- ``participant_id`` introduces no domain semantics beyond participant identity.
- Intended for structural typing in simulation; implementations live outside simulation.
- Runtime protocol checks are shallow: they verify attribute presence only and do not validate attribute types.
- The protocol does not require a stored field, a property setter, or mutation semantics.
- No guarantees about persistence, serialization, or thread safety.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["ParticipantState"]


@runtime_checkable
class ParticipantState(Protocol):
    @property
    def participant_id(self) -> str: ...
