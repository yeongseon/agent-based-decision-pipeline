"""Conformance tests for the action proposal protocol contract."""

from __future__ import annotations

from typing import assert_type

from abdp.core.types import JsonValue
from abdp.simulation import action_proposal
from abdp.simulation.action_proposal import ActionProposal


class _ValidImpl:
    def __init__(
        self,
        proposal_id: str,
        actor_id: str,
        action_key: str,
        payload: JsonValue,
    ) -> None:
        self.proposal_id = proposal_id
        self.actor_id = actor_id
        self.action_key = action_key
        self.payload = payload


class _MissingProposalId:
    def __init__(self) -> None:
        self.actor_id = "agent-1"
        self.action_key = "advance"
        self.payload: JsonValue = {"step": 1}


class _MissingActorId:
    def __init__(self) -> None:
        self.proposal_id = "prop-1"
        self.action_key = "advance"
        self.payload: JsonValue = {"step": 1}


class _MissingActionKey:
    def __init__(self) -> None:
        self.proposal_id = "prop-1"
        self.actor_id = "agent-1"
        self.payload: JsonValue = {"step": 1}


class _MissingPayload:
    def __init__(self) -> None:
        self.proposal_id = "prop-1"
        self.actor_id = "agent-1"
        self.action_key = "advance"


def _public_protocol_members(proto: type) -> set[str]:
    return {
        name
        for name, value in proto.__dict__.items()
        if not name.startswith("_") and (callable(value) or isinstance(value, property))
    }


def test_action_proposal_module_docstring_includes_contract_anchor() -> None:
    doc = action_proposal.__doc__ or ""
    assert "Action proposal protocol contract:" in doc
    assert "identity-intent-and-payload" in doc
    assert "decision logic and state progression" in doc
    assert "proposal_id: str" in doc
    assert "actor_id: str" in doc
    assert "action_key: str" in doc
    assert "payload: JsonValue" in doc
    assert "Runtime protocol checks are shallow" in doc
    assert ("No guarantees about non-emptiness, uniqueness, persistence, serialization, or thread safety") in doc


def test_action_proposal_module_exports_public_symbols_only() -> None:
    assert action_proposal.__all__ == ["ActionProposal"]
    assert action_proposal.ActionProposal is ActionProposal


def test_action_proposal_is_protocol() -> None:
    assert getattr(ActionProposal, "_is_protocol", False) is True


def test_action_proposal_class_docstring_is_omitted_for_pure_protocol_exemplar() -> None:
    assert ActionProposal.__doc__ is None


def test_action_proposal_runtime_checkable_accepts_minimal_valid_impl() -> None:
    payload: JsonValue = {"target": "segment-2", "params": [1, True, None]}
    instance = _ValidImpl("prop-1", "agent-1", "advance", payload)
    assert isinstance(instance, ActionProposal) is True
    proposal: ActionProposal = instance
    assert_type(proposal.proposal_id, str)
    assert_type(proposal.actor_id, str)
    assert_type(proposal.action_key, str)
    assert_type(proposal.payload, JsonValue)
    assert proposal.proposal_id == "prop-1"
    assert proposal.actor_id == "agent-1"
    assert proposal.action_key == "advance"
    assert proposal.payload == payload


def test_action_proposal_runtime_checkable_rejects_missing_proposal_id() -> None:
    assert isinstance(_MissingProposalId(), ActionProposal) is False


def test_action_proposal_runtime_checkable_rejects_missing_actor_id() -> None:
    assert isinstance(_MissingActorId(), ActionProposal) is False


def test_action_proposal_runtime_checkable_rejects_missing_action_key() -> None:
    assert isinstance(_MissingActionKey(), ActionProposal) is False


def test_action_proposal_runtime_checkable_rejects_missing_payload() -> None:
    assert isinstance(_MissingPayload(), ActionProposal) is False


def test_action_proposal_contract_is_identity_intent_and_payload_only() -> None:
    assert _public_protocol_members(ActionProposal) == {
        "proposal_id",
        "actor_id",
        "action_key",
        "payload",
    }
