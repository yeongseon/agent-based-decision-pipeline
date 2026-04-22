from __future__ import annotations

import dataclasses
from typing import get_args, get_origin, get_type_hints

from abdp.agents import AgentContext
from abdp.core import Seed
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState


def test_agent_context_is_a_frozen_slot_backed_dataclass() -> None:
    assert dataclasses.is_dataclass(AgentContext)
    assert AgentContext.__dataclass_params__.frozen is True
    assert "__slots__" in AgentContext.__dict__


def test_agent_context_declares_expected_fields_and_types() -> None:
    fields = {field.name: field.type for field in dataclasses.fields(AgentContext)}

    assert set(fields) == {"scenario_key", "agent_id", "step_index", "seed", "state"}
    assert fields["scenario_key"] is str
    assert fields["agent_id"] is str
    assert fields["step_index"] is int


def test_agent_context_specialization_resolves_type_hints() -> None:
    specialized = AgentContext[SegmentState, ParticipantState, ActionProposal]
    hints = get_type_hints(AgentContext)
    state_type = hints["state"].copy_with(get_args(specialized))

    assert get_origin(specialized) is AgentContext
    assert get_args(specialized) == (SegmentState, ParticipantState, ActionProposal)
    assert hints["scenario_key"] is str
    assert hints["agent_id"] is str
    assert hints["step_index"] is int
    assert hints["seed"] is Seed
    assert get_origin(state_type) is SimulationState
    assert get_args(state_type) == (SegmentState, ParticipantState, ActionProposal)
    assert len(AgentContext.__type_params__) == 3
