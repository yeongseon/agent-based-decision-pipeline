from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Protocol, cast, get_args, get_origin
from uuid import UUID

import pytest

from abdp.core import Seed
from abdp.review.attempt import ReviewAttempt, ReviewDecision, ReviewTrace
from abdp.scenario import ScenarioStep
from abdp.simulation import ParticipantState, SegmentState, SimulationState
from abdp.simulation.snapshot_ref import SnapshotRef


class _DataclassParams(Protocol):
    frozen: bool


@dataclass(frozen=True, slots=True)
class _Action:
    proposal_id: str
    actor_id: str
    action_key: str
    payload: None


@dataclass(slots=True)
class _Decision:
    agent_id: str
    proposals: tuple[_Action, ...]


def _step(step_index: int = 0) -> ScenarioStep[SegmentState, ParticipantState, _Action]:
    action = _Action(proposal_id="proposal-1", actor_id="agent-1", action_key="noop", payload=None)
    state = SimulationState[SegmentState, ParticipantState, _Action](
        step_index=step_index,
        seed=Seed(7),
        snapshot_ref=SnapshotRef(snapshot_id=UUID(int=1), tier="bronze", storage_key="snapshots/1"),
        segments=(),
        participants=(),
        pending_actions=(),
    )
    decision = _Decision(agent_id="agent-1", proposals=(action,))
    return ScenarioStep(state=state, decisions=(decision,), proposals=(action,))


def test_review_decision_is_frozen_slot_backed_dataclass() -> None:
    params = cast(_DataclassParams, object.__getattribute__(ReviewDecision, "__dataclass_params__"))

    assert dataclasses.is_dataclass(ReviewDecision)
    assert params.frozen is True
    assert "__slots__" in ReviewDecision.__dict__


def test_review_attempt_is_frozen_slot_backed_dataclass() -> None:
    params = cast(_DataclassParams, object.__getattribute__(ReviewAttempt, "__dataclass_params__"))

    assert dataclasses.is_dataclass(ReviewAttempt)
    assert params.frozen is True
    assert "__slots__" in ReviewAttempt.__dict__


def test_review_trace_is_frozen_slot_backed_dataclass() -> None:
    params = cast(_DataclassParams, object.__getattribute__(ReviewTrace, "__dataclass_params__"))

    assert dataclasses.is_dataclass(ReviewTrace)
    assert params.frozen is True
    assert "__slots__" in ReviewTrace.__dict__


def test_review_decision_declares_expected_fields() -> None:
    fields = {field.name: field.type for field in dataclasses.fields(ReviewDecision)}

    assert fields == {"score": float, "critique": str}


def test_review_attempt_declares_expected_fields() -> None:
    fields = {field.name: field.type for field in dataclasses.fields(ReviewAttempt)}

    assert fields["step_index"] is int
    assert fields["attempt_no"] is int
    assert get_origin(fields["step"]) is ScenarioStep
    assert fields["decision"] is ReviewDecision
    assert fields["accepted"] is bool


def test_review_trace_declares_attempts_field() -> None:
    fields = {field.name: field.type for field in dataclasses.fields(ReviewTrace)}

    assert get_origin(fields["attempts"]) is tuple
    assert get_origin(get_args(fields["attempts"])[0]) is ReviewAttempt


def test_review_decision_accepts_finite_score() -> None:
    decision = ReviewDecision(score=0.75, critique="accepted")

    assert decision.score == 0.75
    assert decision.critique == "accepted"


@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan"), float("inf")])
def test_review_decision_rejects_invalid_score(value: float) -> None:
    with pytest.raises(ValueError):
        ReviewDecision(score=value, critique="bad")


@pytest.mark.parametrize("value", [-1, True])
def test_review_attempt_rejects_invalid_attempt_no(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        ReviewAttempt(
            step_index=0,
            attempt_no=cast(int, value),
            step=_step(),
            decision=ReviewDecision(0.5, "x"),
            accepted=False,
        )


def test_review_attempt_rejects_step_index_mismatch() -> None:
    with pytest.raises(ValueError):
        ReviewAttempt(
            step_index=3,
            attempt_no=0,
            step=_step(step_index=2),
            decision=ReviewDecision(0.5, "x"),
            accepted=False,
        )


def test_review_trace_preserves_deterministic_equality() -> None:
    attempt: ReviewAttempt[_Action] = ReviewAttempt(
        step_index=0,
        attempt_no=1,
        step=_step(),
        decision=ReviewDecision(0.25, "retry"),
        accepted=False,
    )

    assert attempt == ReviewAttempt(
        step_index=0,
        attempt_no=1,
        step=_step(),
        decision=ReviewDecision(0.25, "retry"),
        accepted=False,
    )
    assert ReviewTrace(attempts=(attempt,)) == ReviewTrace(attempts=(attempt,))
