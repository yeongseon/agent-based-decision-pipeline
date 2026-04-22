from dataclasses import dataclass

from abdp.core import Seed
from abdp.scenario.step import ScenarioStep
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState

__all__ = ["ScenarioRun"]


@dataclass(frozen=True, slots=True)
class ScenarioRun[S: SegmentState, P: ParticipantState, A: ActionProposal]:
    scenario_key: str
    seed: Seed
    steps: tuple[ScenarioStep[S, P, A], ...]
    final_state: SimulationState[S, P, A]

    @property
    def step_count(self) -> int:
        return len(self.steps)
