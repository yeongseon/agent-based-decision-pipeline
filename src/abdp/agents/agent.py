"""Public ``Agent`` protocol exposed by ``abdp.agents``."""

from typing import Protocol, runtime_checkable

from abdp.agents.context import AgentContext
from abdp.agents.decision import AgentDecision
from abdp.simulation import ActionProposal, ParticipantState, SegmentState

__all__ = ["Agent"]


@runtime_checkable
class Agent[S: SegmentState, P: ParticipantState, A: ActionProposal](Protocol):
    """Decision-making participant in a scenario step."""

    agent_id: str

    def decide(self, context: AgentContext[S, P, A]) -> AgentDecision[A]:
        """Return a decision for the given context."""

        ...  # pragma: no cover
