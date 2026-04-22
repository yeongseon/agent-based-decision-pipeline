"""Queue scheduling resolver that drains pending proposals each step."""

from __future__ import annotations

from typing import override

from abdp.scenario import ActionResolver
from abdp.simulation import SimulationState

from examples.queue_scheduling.domain import QueueProposal, Slot, Worker

HANDLED_ACTION_KEYS = frozenset({"enqueue", "promote", "drop", "heartbeat"})


class QueueResolver(ActionResolver[Slot, Worker, QueueProposal]):
    @override
    def resolve(
        self,
        state: SimulationState[Slot, Worker, QueueProposal],
        proposals: tuple[QueueProposal, ...],
    ) -> SimulationState[Slot, Worker, QueueProposal]:
        unknown = next(
            (p.action_key for p in proposals if p.action_key not in HANDLED_ACTION_KEYS),
            None,
        )
        if unknown is not None:
            raise ValueError(f"Unknown action_key: {unknown}")
        return SimulationState[Slot, Worker, QueueProposal](
            step_index=state.step_index + 1,
            seed=state.seed,
            snapshot_ref=state.snapshot_ref,
            segments=state.segments,
            participants=state.participants,
            pending_actions=(),
        )
