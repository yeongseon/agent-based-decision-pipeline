from __future__ import annotations

from typing import TypeVar, get_args, get_origin, get_protocol_members

from abdp.agents import AgentDecision


class _ValidDecision:
    def __init__(self, agent_id: str, proposals: tuple[str, ...]) -> None:
        self.agent_id = agent_id
        self.proposals = proposals


class _MissingAgentId:
    def __init__(self) -> None:
        self.proposals = ("approve",)


class _MissingProposals:
    def __init__(self) -> None:
        self.agent_id = "agent-1"


def test_agent_decision_is_generic_runtime_checkable_protocol() -> None:
    assert getattr(AgentDecision, "_is_protocol", False) is True
    assert getattr(AgentDecision, "_is_runtime_protocol", False) is True
    assert get_protocol_members(AgentDecision) == frozenset({"agent_id", "proposals"})


def test_agent_decision_declares_expected_annotations() -> None:
    annotation_namespace = AgentDecision.__annotations__
    assert annotation_namespace["agent_id"] is str

    proposals_annotation = annotation_namespace["proposals"]
    assert get_origin(proposals_annotation) is tuple
    assert get_args(proposals_annotation)[1] is Ellipsis

    proposal_type = get_args(proposals_annotation)[0]
    assert isinstance(proposal_type, TypeVar)
    assert proposal_type.__name__ == "A"


def test_agent_decision_exposes_generic_parameter_a() -> None:
    assert AgentDecision.__type_params__[0].__name__ == "A"


def test_agent_decision_runtime_checkable_accepts_minimal_valid_impl() -> None:
    assert isinstance(_ValidDecision("agent-1", ("approve", "review")), AgentDecision) is True


def test_agent_decision_runtime_checkable_rejects_missing_agent_id() -> None:
    assert isinstance(_MissingAgentId(), AgentDecision) is False


def test_agent_decision_runtime_checkable_rejects_missing_proposals() -> None:
    assert isinstance(_MissingProposals(), AgentDecision) is False
