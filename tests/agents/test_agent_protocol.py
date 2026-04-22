from __future__ import annotations

from typing import TypeVar, get_origin, get_type_hints

from abdp.agents import Agent, AgentContext, AgentDecision
from abdp.simulation import ActionProposal, ParticipantState, SegmentState


class _ValidAgent:
    agent_id: str

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id

    def decide(
        self,
        context: AgentContext[SegmentState, ParticipantState, ActionProposal],
    ) -> AgentDecision[ActionProposal]:
        raise NotImplementedError


def test_agent_is_generic_runtime_checkable_protocol() -> None:
    assert getattr(Agent, "_is_protocol", False) is True
    assert getattr(Agent, "_is_runtime_protocol", False) is True


def test_agent_declares_expected_annotations_and_signature() -> None:
    annotation_namespace = get_type_hints(Agent)
    assert annotation_namespace["agent_id"] is str

    decide_hints = get_type_hints(Agent.decide)
    assert get_origin(decide_hints["context"]) is AgentContext
    assert get_origin(decide_hints["return"]) is AgentDecision


def test_agent_exposes_generic_parameters_for_segment_participant_and_action() -> None:
    type_params = Agent.__type_params__

    assert len(type_params) == 3
    assert all(isinstance(type_param, TypeVar) for type_param in type_params)
    assert tuple(type_param.__name__ for type_param in type_params) == ("S", "P", "A")


def test_agent_runtime_checkable_accepts_minimal_valid_impl() -> None:
    assert isinstance(_ValidAgent("agent-1"), Agent) is True
