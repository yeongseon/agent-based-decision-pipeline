from __future__ import annotations

from typing import TypeVar, get_type_hints

from abdp.agents import AgentDecision


class _ValidDecision:
    agent_id: str
    proposals: tuple[str, ...]

    def __init__(self, agent_id: str, proposals: tuple[str, ...]) -> None:
        self.agent_id = agent_id
        self.proposals = proposals


class _MissingAgentId:
    proposals: tuple[str, ...]

    def __init__(self) -> None:
        self.proposals = ("approve",)


class _MissingProposals:
    agent_id: str

    def __init__(self) -> None:
        self.agent_id = "agent-1"


def _agent_decision_annotations() -> dict[str, object]:
    return get_type_hints(AgentDecision)


def test_agent_decision_is_generic_runtime_checkable_protocol() -> None:
    assert getattr(AgentDecision, "_is_protocol", False) is True
    assert getattr(AgentDecision, "_is_runtime_protocol", False) is True
    assert set(AgentDecision.__annotations__) == {"agent_id", "proposals"}


def test_agent_decision_declares_expected_annotations() -> None:
    annotation_namespace = _agent_decision_annotations()
    assert annotation_namespace["agent_id"] is str

    proposals_annotation = annotation_namespace["proposals"]
    assert str(proposals_annotation) == "tuple[A, ...]"

    proposal_type = AgentDecision.__type_params__[0]
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
