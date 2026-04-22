from __future__ import annotations

import dataclasses
from typing import Protocol, cast, get_args, get_origin, get_type_hints

from abdp.agents import AgentDecision
from abdp.scenario import ScenarioStep
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState


class _DataclassParams(Protocol):
    frozen: bool


class _SupportsCopyWith(Protocol):
    def copy_with(self, params: tuple[object, ...]) -> object: ...


def test_scenario_step_is_a_frozen_slot_backed_dataclass() -> None:
    params = cast(_DataclassParams, object.__getattribute__(ScenarioStep, "__dataclass_params__"))

    assert dataclasses.is_dataclass(ScenarioStep)
    assert params.frozen is True
    assert "__slots__" in ScenarioStep.__dict__


def test_scenario_step_declares_expected_field_names() -> None:
    fields = {field.name for field in dataclasses.fields(ScenarioStep)}

    assert fields == {"state", "decisions", "proposals"}


def test_scenario_step_specialization_resolves_type_hints() -> None:
    specialized = ScenarioStep[SegmentState, ParticipantState, ActionProposal]
    hints: dict[str, object] = get_type_hints(ScenarioStep)
    type_args = get_args(specialized)

    assert get_origin(specialized) is ScenarioStep
    assert type_args == (SegmentState, ParticipantState, ActionProposal)
    assert len(ScenarioStep.__type_params__) == 3

    state_type = cast(_SupportsCopyWith, hints["state"]).copy_with(type_args)
    assert get_origin(state_type) is SimulationState
    assert get_args(state_type) == (SegmentState, ParticipantState, ActionProposal)

    decisions_args = get_args(hints["decisions"])
    assert get_origin(hints["decisions"]) is tuple
    assert get_origin(decisions_args[0]) is AgentDecision
    assert decisions_args[1] is Ellipsis

    proposals_args = get_args(hints["proposals"])
    assert get_origin(hints["proposals"]) is tuple
    assert proposals_args[1] is Ellipsis
