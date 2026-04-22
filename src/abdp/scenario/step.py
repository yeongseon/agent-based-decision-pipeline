from dataclasses import dataclass

from abdp.agents import AgentDecision
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState

__all__ = ["ScenarioStep"]


@dataclass(frozen=True, slots=True)
class ScenarioStep[S: SegmentState, P: ParticipantState, A: ActionProposal]:
    state: SimulationState[S, P, A]
    decisions: tuple[AgentDecision[A], ...]
    proposals: tuple[A, ...]
