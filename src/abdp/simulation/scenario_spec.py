"""Scenario spec protocol contract:

- Defines the minimal seed-aware scenario contract that produces an initial
  ``SimulationState`` for a deterministic simulation run.
- Domain-neutral and simulation-agnostic.
- Contract consists of readable ``scenario_key: str``, ``seed: Seed``, and
  ``build_initial_state()`` access only.
- ``scenario_key`` is a neutral scenario discriminator only; it does not imply
  registry semantics, validation rules, or domain-specific scenario taxonomies.
- ``seed`` carries the deterministic randomness source for the scenario; it
  does not imply any RNG implementation, sampling policy, or reseeding
  semantics.
- ``build_initial_state()`` returns a fully constructed ``SimulationState``
  instance for the scenario; it does not imply caching, idempotence beyond
  the seed contract, persistence, or side-effect semantics.
- Intended for structural typing in simulation; implementations live outside
  simulation.
- Runtime protocol checks are shallow: they verify attribute and method
  presence only and do not validate attribute types or method signatures.
- The protocol does not require a stored field, a property setter, or mutation semantics.
- No guarantees about scenario-key uniqueness, determinism beyond seed carriage,
  validation, persistence, serialization, or thread safety.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from abdp.core.types import Seed
from abdp.simulation.action_proposal import ActionProposal
from abdp.simulation.participant_state import ParticipantState
from abdp.simulation.segment_state import SegmentState
from abdp.simulation.state import SimulationState

__all__ = ["ScenarioSpec"]


@runtime_checkable
class ScenarioSpec[S: SegmentState, P: ParticipantState, A: ActionProposal](Protocol):
    @property
    def scenario_key(self) -> str: ...

    @property
    def seed(self) -> Seed: ...

    def build_initial_state(self) -> SimulationState[S, P, A]: ...
