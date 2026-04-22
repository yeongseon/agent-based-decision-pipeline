"""Public ``ScenarioRun`` model exposed by ``abdp.scenario``."""

from dataclasses import dataclass

from abdp.core import Seed
from abdp.scenario.step import ScenarioStep
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState

__all__ = ["ScenarioRun"]


@dataclass(frozen=True, slots=True)
class ScenarioRun[S: SegmentState, P: ParticipantState, A: ActionProposal]:
    """Full execution trace of a scenario.

    Carries the deterministic ``scenario_key`` and ``seed``, the ordered
    sequence of ``steps`` produced by the runner, and the post-resolution
    ``final_state`` snapshot.
    """

    scenario_key: str
    seed: Seed
    steps: tuple[ScenarioStep[S, P, A], ...]
    final_state: SimulationState[S, P, A]

    @property
    def step_count(self) -> int:
        """Return the number of steps in the run."""
        return len(self.steps)
