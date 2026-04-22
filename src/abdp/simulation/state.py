"""Simulation state contract:

- Priority-3 role: packages the immutable state surface needed by the execution layer without
  implementing transitions.
- ``SimulationState`` is an immutable generic container for a single simulation step.
- Contract consists of ``step_index``, ``seed``, ``snapshot_ref``, ``segments``,
  ``participants``, and ``pending_actions`` only.
- ``step_index`` must be an ``int`` greater than or equal to zero; ``bool`` is rejected.
- ``seed`` is validated with ``validate_seed``.
- ``snapshot_ref`` must be a ``SnapshotRef`` instance.
- ``segments``, ``participants``, and ``pending_actions`` must be tuple instances and preserve
  caller-provided ordering.
- Element values are not runtime-validated against their protocols; structural typing is enforced
  statically.
- No cross-field validation is performed for identifiers, membership consistency, uniqueness, or
  action applicability.
- No guarantees about state transitions, execution loops, persistence, serialization, or thread
  safety.
"""

from __future__ import annotations

from dataclasses import dataclass

from abdp.core.types import Seed, validate_seed
from abdp.simulation.action_proposal import ActionProposal
from abdp.simulation.participant_state import ParticipantState
from abdp.simulation.segment_state import SegmentState
from abdp.simulation.snapshot_ref import SnapshotRef

__all__ = ["SimulationState"]


def _validate_step_index(value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"step_index must be int, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"step_index must be >= 0, got {value}")


def _validate_snapshot_ref(value: object) -> None:
    if not isinstance(value, SnapshotRef):
        raise TypeError(f"snapshot_ref must be SnapshotRef, got {type(value).__name__}")


def _validate_tuple(field_name: str, value: object) -> None:
    if not isinstance(value, tuple):
        raise TypeError(f"{field_name} must be tuple, got {type(value).__name__}")


@dataclass(frozen=True, slots=True, kw_only=True)
class SimulationState[S: SegmentState, P: ParticipantState, A: ActionProposal]:
    """SimulationState contract:

    - Immutable generic dataclass record with slot-backed, keyword-only fields.
    - Brings together the reproducibility anchor, snapshot reference, segment states, participant
      states, and pending action proposals for a single simulation step.
    - Generic over segment, participant, and action types via the neutral ``SegmentState``,
      ``ParticipantState``, and ``ActionProposal`` protocol bounds.
    - Collection fields are stored exactly as ordered tuples provided; contents are not copied,
      normalized, or cross-validated.
    - Validation is limited to basic runtime type checks and field invariants.
    - Construction is synchronous only.
    - No guarantees about state transitions, execution semantics, persistence, serialization, or
      thread safety.
    """

    step_index: int
    seed: Seed
    snapshot_ref: SnapshotRef
    segments: tuple[S, ...]
    participants: tuple[P, ...]
    pending_actions: tuple[A, ...]

    def __post_init__(self) -> None:
        _validate_step_index(self.step_index)
        validate_seed(self.seed)
        _validate_snapshot_ref(self.snapshot_ref)
        _validate_tuple("segments", self.segments)
        _validate_tuple("participants", self.participants)
        _validate_tuple("pending_actions", self.pending_actions)
