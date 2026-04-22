"""Conformance tests for the participant state protocol contract."""

from __future__ import annotations

from typing import assert_type

from abdp.simulation import participant_state
from abdp.simulation.participant_state import ParticipantState


class _ValidParticipant:
    def __init__(self, participant_id: str) -> None:
        self.participant_id = participant_id


class _MissingParticipantId:
    pass


def _public_protocol_members(proto: type) -> set[str]:
    return {
        name
        for name, value in proto.__dict__.items()
        if not name.startswith("_") and (callable(value) or isinstance(value, property))
    }


def test_participant_state_module_docstring_includes_contract_anchor() -> None:
    doc = participant_state.__doc__ or ""
    assert "Participant state protocol contract:" in doc
    assert "identity-only" in doc
    assert "participant_id: str" in doc
    assert "Runtime protocol checks are shallow" in doc
    assert "No guarantees about persistence, serialization, or thread safety" in doc


def test_participant_state_module_exports_public_symbols_only() -> None:
    assert participant_state.__all__ == ["ParticipantState"]
    assert participant_state.ParticipantState is ParticipantState


def test_participant_state_is_protocol() -> None:
    assert getattr(ParticipantState, "_is_protocol", False) is True


def test_participant_state_class_docstring_is_omitted_for_pure_protocol_exemplar() -> None:
    assert ParticipantState.__doc__ is None


def test_participant_state_runtime_checkable_accepts_minimal_valid_impl() -> None:
    instance = _ValidParticipant("p1")
    assert isinstance(instance, ParticipantState) is True
    state: ParticipantState = instance
    assert_type(state.participant_id, str)
    assert state.participant_id == "p1"


def test_participant_state_runtime_checkable_rejects_missing_participant_id() -> None:
    assert isinstance(_MissingParticipantId(), ParticipantState) is False


def test_participant_state_contract_is_identity_only() -> None:
    assert _public_protocol_members(ParticipantState) == {"participant_id"}
