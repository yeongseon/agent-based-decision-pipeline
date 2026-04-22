from typing import Protocol, runtime_checkable

from abdp.simulation.action_proposal import ActionProposal
from abdp.simulation.participant_state import ParticipantState
from abdp.simulation.segment_state import SegmentState
from abdp.simulation.state import SimulationState

__all__ = ["ActionResolver"]


@runtime_checkable
class ActionResolver[S: SegmentState, P: ParticipantState, A: ActionProposal](Protocol):
    """Resolve agent proposals into the next SimulationState.

    Implementations MUST NOT mutate the input ``state``; they return the next
    ``SimulationState[S, P, A]`` derived from ``state`` and ``proposals``.
    """

    def resolve(
        self,
        state: SimulationState[S, P, A],
        proposals: tuple[A, ...],
    ) -> SimulationState[S, P, A]: ...  # pragma: no cover
