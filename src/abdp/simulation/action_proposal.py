"""Action proposal protocol contract:

- Defines the minimal identity-intent-and-payload action proposal contract
  shared between decision logic and state progression across simulation domains.
- Domain-neutral and simulation-agnostic.
- Contract consists of readable ``proposal_id: str``, ``actor_id: str``,
  ``action_key: str``, and ``payload: JsonValue`` access only.
- ``proposal_id`` introduces no domain semantics beyond proposal identity.
- ``actor_id`` introduces no domain semantics beyond identifying the
  proposing actor.
- ``action_key`` is a neutral action discriminator only; it does not imply
  execution semantics, validation rules, or domain-specific action taxonomies.
- ``payload`` is a generic JSON-compatible value layer for neutral action
  parameters only; it does not imply schema, storage, transport, or
  domain-specific action types.
- Intended for structural typing in simulation; implementations live outside
  simulation.
- Runtime protocol checks are shallow: they verify attribute presence only and
  do not validate attribute types.
- The protocol does not require a stored field, a property setter, or mutation
  semantics.
- No guarantees about non-emptiness, uniqueness, persistence, serialization, or thread safety.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from abdp.core.types import JsonValue

__all__ = ["ActionProposal"]


@runtime_checkable
class ActionProposal(Protocol):
    @property
    def proposal_id(self) -> str: ...

    @property
    def actor_id(self) -> str: ...

    @property
    def action_key(self) -> str: ...

    @property
    def payload(self) -> JsonValue: ...
