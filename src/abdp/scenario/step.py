"""Public ``ScenarioStep`` model exposed by ``abdp.scenario``."""

from dataclasses import dataclass

from abdp.agents import AgentDecision
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState

__all__ = ["ScenarioStep"]


@dataclass(frozen=True, slots=True)
class ScenarioStep[S: SegmentState, P: ParticipantState, A: ActionProposal]:
    """Pre-resolution snapshot of one scenario runner iteration.

    Captures the simulation ``state`` before action resolution, the ordered
    ``decisions`` collected from agents this step, and the merged action
    ``proposals`` derived from those decisions.
    """

    state: SimulationState[S, P, A]
    decisions: tuple[AgentDecision[A], ...]
    proposals: tuple[A, ...]
