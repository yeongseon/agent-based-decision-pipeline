"""Public ``AgentContext`` model exposed by ``abdp.agents``."""

from dataclasses import dataclass

from abdp.core import Seed
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState

__all__ = ["AgentContext"]


@dataclass(frozen=True, slots=True)
class AgentContext[S: SegmentState, P: ParticipantState, A: ActionProposal]:
    """Immutable agent-scoped view of a single scenario step.

    Packages the scenario identifier, agent identifier, step index, seed, and
    simulation state needed for one ``Agent.decide`` call.
    """

    scenario_key: str
    agent_id: str
    step_index: int
    seed: Seed
    state: SimulationState[S, P, A]
