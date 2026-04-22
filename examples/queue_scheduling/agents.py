"""Queue scheduling agents that emit per-step worker heartbeats."""

from __future__ import annotations

from dataclasses import dataclass
from typing import override

from abdp.agents import Agent, AgentContext, AgentDecision

from examples.queue_scheduling.domain import QueueProposal, Slot, Worker


@dataclass(slots=True, kw_only=True)
class WorkerDecision:
    agent_id: str
    proposals: tuple[QueueProposal, ...]


@dataclass(slots=True, kw_only=True)
class QueueWorkerAgent(Agent[Slot, Worker, QueueProposal]):
    agent_id: str
    queue_id: str

    @override
    def decide(
        self,
        context: AgentContext[Slot, Worker, QueueProposal],
    ) -> AgentDecision[QueueProposal]:
        heartbeat = self._build_heartbeat(context.step_index)
        return WorkerDecision(agent_id=self.agent_id, proposals=(heartbeat,))

    def _build_heartbeat(self, step_index: int) -> QueueProposal:
        return QueueProposal(
            proposal_id=f"heartbeat-{self.queue_id}-step{step_index}",
            actor_id=self.agent_id,
            action_key="heartbeat",
            payload={"queue_id": self.queue_id, "step_index": step_index},
        )
