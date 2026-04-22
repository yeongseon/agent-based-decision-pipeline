"""Conformance tests for the simulation state container contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import assert_type, cast
from uuid import UUID

import pytest

from abdp.core.types import JsonValue, Seed
from abdp.simulation import state as state_module
from abdp.simulation.snapshot_ref import SnapshotRef
from abdp.simulation.state import SimulationState

_SNAPSHOT_ID = UUID("00000000-0000-0000-0000-000000000001")
_SEED = Seed(7)
_STORAGE_KEY = "snapshots/abc"


def _make_snapshot_ref() -> SnapshotRef:
    return SnapshotRef(snapshot_id=_SNAPSHOT_ID, tier="bronze", storage_key=_STORAGE_KEY)


@dataclass(frozen=True, slots=True, kw_only=True)
class _Participant:
    participant_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class _Segment:
    segment_id: str
    participant_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class _Action:
    proposal_id: str
    actor_id: str
    action_key: str
    payload: JsonValue


def _make_state(
    *,
    step_index: int = 0,
    seed: Seed = _SEED,
) -> SimulationState[_Segment, _Participant, _Action]:
    participant = _Participant(participant_id="p1")
    segment = _Segment(segment_id="s1", participant_ids=("p1",))
    action = _Action(proposal_id="prop-1", actor_id="p1", action_key="advance", payload=1)
    return SimulationState[_Segment, _Participant, _Action](
        step_index=step_index,
        seed=seed,
        snapshot_ref=_make_snapshot_ref(),
        segments=(segment,),
        participants=(participant,),
        pending_actions=(action,),
    )


def test_simulation_state_module_docstring_includes_contract_anchor() -> None:
    doc = state_module.__doc__ or ""
    assert "Simulation state contract:" in doc
    assert "immutable generic container" in doc
    assert "step_index" in doc
    assert "seed" in doc
    assert "snapshot_ref" in doc
    assert "segments" in doc
    assert "participants" in doc
    assert "pending_actions" in doc
    assert "validate_seed" in doc
    assert "Element values are not runtime-validated" in doc
    assert "No cross-field validation" in doc


def test_simulation_state_module_exports_public_symbols_only() -> None:
    assert state_module.__all__ == ["SimulationState"]
    assert state_module.SimulationState is SimulationState


def test_simulation_state_class_docstring_includes_contract_anchor() -> None:
    doc = SimulationState.__doc__ or ""
    assert "SimulationState contract:" in doc
    assert "Immutable generic dataclass" in doc
    assert "Generic over segment, participant, and action types" in doc


def test_simulation_state_constructs_valid_state() -> None:
    s = _make_state()
    assert s.step_index == 0
    assert s.seed == _SEED
    assert s.snapshot_ref == _make_snapshot_ref()
    assert len(s.segments) == 1
    assert len(s.participants) == 1
    assert len(s.pending_actions) == 1


def test_simulation_state_is_frozen() -> None:
    s = _make_state()
    with pytest.raises((AttributeError, TypeError)):
        cast(object, s).__setattr__("step_index", 1)


def test_simulation_state_uses_slots() -> None:
    assert hasattr(SimulationState, "__slots__")
    assert "__dict__" not in dir(_make_state())


def test_simulation_state_is_generic_over_domain_types() -> None:
    s: SimulationState[_Segment, _Participant, _Action] = _make_state()
    assert_type(s.segments, tuple[_Segment, ...])
    assert_type(s.participants, tuple[_Participant, ...])
    assert_type(s.pending_actions, tuple[_Action, ...])


def test_simulation_state_equal_instances_compare_equal() -> None:
    assert _make_state() == _make_state()


def test_simulation_state_unequal_when_step_index_differs() -> None:
    assert _make_state(step_index=0) != _make_state(step_index=1)


def test_simulation_state_repr_includes_all_fields_in_definition_order() -> None:
    r = repr(_make_state())
    assert r.startswith("SimulationState(")
    fields_in_order = ["step_index=", "seed=", "snapshot_ref=", "segments=", "participants=", "pending_actions="]
    positions = [r.index(f) for f in fields_in_order]
    assert positions == sorted(positions)


def test_simulation_state_rejects_non_int_step_index() -> None:
    with pytest.raises(TypeError, match=r"^step_index must be int, got str$"):
        _make_state(step_index=cast(int, "0"))


def test_simulation_state_rejects_bool_step_index() -> None:
    with pytest.raises(TypeError, match=r"^step_index must be int, got bool$"):
        _make_state(step_index=cast(int, True))


def test_simulation_state_rejects_float_step_index() -> None:
    with pytest.raises(TypeError, match=r"^step_index must be int, got float$"):
        _make_state(step_index=cast(int, 0.0))


def test_simulation_state_rejects_negative_step_index() -> None:
    with pytest.raises(ValueError, match=r"^step_index must be >= 0, got -1$"):
        _make_state(step_index=-1)


def test_simulation_state_delegates_seed_validation_for_non_int_seed() -> None:
    with pytest.raises(TypeError, match=r"^Seed must be a non-bool int, got str$"):
        _make_state(seed=cast(Seed, "x"))


def test_simulation_state_delegates_seed_validation_for_bool_seed() -> None:
    with pytest.raises(TypeError, match=r"^Seed must be a non-bool int, got bool$"):
        _make_state(seed=cast(Seed, True))


def test_simulation_state_delegates_seed_validation_for_negative_seed() -> None:
    with pytest.raises(ValueError, match=r"^Seed must be >= 0"):
        _make_state(seed=cast(Seed, -1))


def test_simulation_state_delegates_seed_validation_for_seed_above_uint32_max() -> None:
    with pytest.raises(ValueError, match=r"^Seed must be <="):
        _make_state(seed=cast(Seed, 2**32))


def test_simulation_state_rejects_non_snapshot_ref_snapshot_ref() -> None:
    with pytest.raises(TypeError, match=r"^snapshot_ref must be SnapshotRef, got str$"):
        SimulationState[_Segment, _Participant, _Action](
            step_index=0,
            seed=_SEED,
            snapshot_ref=cast(SnapshotRef, "not-a-ref"),
            segments=(),
            participants=(),
            pending_actions=(),
        )


def test_simulation_state_rejects_non_tuple_segments() -> None:
    with pytest.raises(TypeError, match=r"^segments must be tuple, got list$"):
        SimulationState[_Segment, _Participant, _Action](
            step_index=0,
            seed=_SEED,
            snapshot_ref=_make_snapshot_ref(),
            segments=cast(tuple[_Segment, ...], []),
            participants=(),
            pending_actions=(),
        )


def test_simulation_state_rejects_non_tuple_participants() -> None:
    with pytest.raises(TypeError, match=r"^participants must be tuple, got list$"):
        SimulationState[_Segment, _Participant, _Action](
            step_index=0,
            seed=_SEED,
            snapshot_ref=_make_snapshot_ref(),
            segments=(),
            participants=cast(tuple[_Participant, ...], []),
            pending_actions=(),
        )


def test_simulation_state_rejects_non_tuple_pending_actions() -> None:
    with pytest.raises(TypeError, match=r"^pending_actions must be tuple, got list$"):
        SimulationState[_Segment, _Participant, _Action](
            step_index=0,
            seed=_SEED,
            snapshot_ref=_make_snapshot_ref(),
            segments=(),
            participants=(),
            pending_actions=cast(tuple[_Action, ...], []),
        )
