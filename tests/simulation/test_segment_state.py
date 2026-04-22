"""Conformance tests for the segment state protocol contract."""

from __future__ import annotations

from typing import assert_type

from abdp.simulation import segment_state
from abdp.simulation.segment_state import SegmentState


class _ValidSegment:
    def __init__(self, segment_id: str, participant_ids: tuple[str, ...]) -> None:
        self.segment_id = segment_id
        self.participant_ids = participant_ids


class _MissingSegmentId:
    def __init__(self) -> None:
        self.participant_ids: tuple[str, ...] = ()


class _MissingParticipantIds:
    def __init__(self) -> None:
        self.segment_id = "s1"


def _public_protocol_members(proto: type) -> set[str]:
    return {
        name
        for name, value in proto.__dict__.items()
        if not name.startswith("_") and (callable(value) or isinstance(value, property))
    }


def test_segment_state_module_docstring_includes_contract_anchor() -> None:
    doc = segment_state.__doc__ or ""
    assert "Segment state protocol contract:" in doc
    assert "identity-and-membership" in doc
    assert "segment_id: str" in doc
    assert "participant_ids: tuple[str, ...]" in doc
    assert "Runtime protocol checks are shallow" in doc
    assert "No guarantees about uniqueness, non-emptiness, persistence, serialization, or thread safety" in doc


def test_segment_state_module_exports_public_symbols_only() -> None:
    assert segment_state.__all__ == ["SegmentState"]
    assert segment_state.SegmentState is SegmentState


def test_segment_state_is_protocol() -> None:
    assert getattr(SegmentState, "_is_protocol", False) is True


def test_segment_state_class_docstring_is_omitted_for_pure_protocol_exemplar() -> None:
    assert SegmentState.__doc__ is None


def test_segment_state_runtime_checkable_accepts_minimal_valid_impl() -> None:
    instance = _ValidSegment("s1", ("p1", "p2"))
    assert isinstance(instance, SegmentState) is True
    state: SegmentState = instance
    assert_type(state.segment_id, str)
    assert_type(state.participant_ids, tuple[str, ...])
    assert state.segment_id == "s1"
    assert state.participant_ids == ("p1", "p2")


def test_segment_state_runtime_checkable_rejects_missing_segment_id() -> None:
    assert isinstance(_MissingSegmentId(), SegmentState) is False


def test_segment_state_runtime_checkable_rejects_missing_participant_ids() -> None:
    assert isinstance(_MissingParticipantIds(), SegmentState) is False


def test_segment_state_contract_is_identity_and_membership_only() -> None:
    assert _public_protocol_members(SegmentState) == {"segment_id", "participant_ids"}
