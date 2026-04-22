from dataclasses import dataclass

from abdp.core import Seed
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState

__all__ = ["AgentContext"]


@dataclass(frozen=True, slots=True)
class AgentContext[S: SegmentState, P: ParticipantState, A: ActionProposal]:
    """Read-only snapshot passed to ``Agent.decide`` for one step.

    Carries the deterministic seed, current simulation state, and identifiers
    that scope an agent's decision within a scenario step.
    """

    scenario_key: str
    agent_id: str
    step_index: int
    seed: Seed
    state: SimulationState[S, P, A]
