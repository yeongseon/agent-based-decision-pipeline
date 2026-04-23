"""Critic protocol for deterministic review scoring."""

from typing import Protocol, runtime_checkable

from abdp.review.attempt import ReviewDecision
from abdp.scenario import ScenarioStep
from abdp.simulation import ActionProposal, ParticipantState, SegmentState

__all__ = ["Critic"]


@runtime_checkable
class Critic[S: SegmentState, P: ParticipantState, A: ActionProposal](Protocol):
    """Deterministic scorer for one proposed scenario step."""

    def evaluate(self, step: ScenarioStep[S, P, A]) -> ReviewDecision: ...  # pragma: no cover
