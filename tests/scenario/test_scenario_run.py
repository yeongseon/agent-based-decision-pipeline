from __future__ import annotations

import dataclasses
from typing import Protocol, cast, get_args, get_origin, get_type_hints
from uuid import UUID

from abdp.core import Seed
from abdp.scenario import ScenarioRun, ScenarioStep
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState
from abdp.simulation.snapshot_ref import SnapshotRef


class _DataclassParams(Protocol):
    frozen: bool


class _SupportsCopyWith(Protocol):
    def copy_with(self, params: tuple[object, ...]) -> object: ...


def _make_state() -> SimulationState[SegmentState, ParticipantState, ActionProposal]:
    return SimulationState[SegmentState, ParticipantState, ActionProposal](
        step_index=0,
        seed=Seed(0),
        snapshot_ref=SnapshotRef(
            snapshot_id=UUID("00000000-0000-0000-0000-000000000001"),
            tier="bronze",
            storage_key="snapshots/run",
        ),
        segments=(),
        participants=(),
        pending_actions=(),
    )


def _make_step() -> ScenarioStep[SegmentState, ParticipantState, ActionProposal]:
    return ScenarioStep[SegmentState, ParticipantState, ActionProposal](
        state=_make_state(),
        decisions=(),
        proposals=(),
    )


def test_scenario_run_is_a_frozen_slot_backed_dataclass() -> None:
    params = cast(_DataclassParams, object.__getattribute__(ScenarioRun, "__dataclass_params__"))

    assert dataclasses.is_dataclass(ScenarioRun)
    assert params.frozen is True
    assert "__slots__" in ScenarioRun.__dict__


def test_scenario_run_declares_expected_fields_and_scalar_types() -> None:
    fields = {field.name: field.type for field in dataclasses.fields(ScenarioRun)}

    assert set(fields) == {"scenario_key", "seed", "steps", "final_state"}
    assert fields["scenario_key"] is str


def test_scenario_run_specialization_resolves_type_hints() -> None:
    specialized = ScenarioRun[SegmentState, ParticipantState, ActionProposal]
    hints: dict[str, object] = get_type_hints(ScenarioRun)
    type_args = get_args(specialized)

    assert get_origin(specialized) is ScenarioRun
    assert type_args == (SegmentState, ParticipantState, ActionProposal)
    assert len(ScenarioRun.__type_params__) == 3
    assert hints["scenario_key"] is str
    assert hints["seed"] is Seed

    steps_args = get_args(hints["steps"])
    assert get_origin(hints["steps"]) is tuple
    assert get_origin(steps_args[0]) is ScenarioStep
    assert steps_args[1] is Ellipsis

    final_state_type = cast(_SupportsCopyWith, hints["final_state"]).copy_with(type_args)
    assert get_origin(final_state_type) is SimulationState
    assert get_args(final_state_type) == (SegmentState, ParticipantState, ActionProposal)


def test_scenario_run_step_count_returns_len_of_steps() -> None:
    state = _make_state()
    step = _make_step()
    run_zero = ScenarioRun[SegmentState, ParticipantState, ActionProposal](
        scenario_key="k",
        seed=Seed(0),
        steps=(),
        final_state=state,
    )
    run_two = ScenarioRun[SegmentState, ParticipantState, ActionProposal](
        scenario_key="k",
        seed=Seed(0),
        steps=(step, step),
        final_state=state,
    )

    assert run_zero.step_count == 0
    assert run_two.step_count == 2
