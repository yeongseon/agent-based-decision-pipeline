"""Test-local queue scheduling domain proving the v0.1 simulation contracts admit a second domain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import override
from uuid import UUID

from abdp.core.types import JsonValue, Seed
from abdp.simulation import ScenarioSpec, SimulationState, SnapshotRef


@dataclass(frozen=True, slots=True, kw_only=True)
class Worker:
    participant_id: str
    queue_id: str
    max_parallel_jobs: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Slot:
    segment_id: str
    participant_ids: tuple[str, ...]
    queue_id: str
    latency_target_ms: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Job:
    job_id: str
    queue_id: str
    latency_ms: int
    priority: int

    def as_payload(self) -> JsonValue:
        return {
            "job_id": self.job_id,
            "queue_id": self.queue_id,
            "latency_ms": self.latency_ms,
            "priority": self.priority,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class QueueProposal:
    proposal_id: str
    actor_id: str
    action_key: str
    payload: JsonValue


class QueueScenario(ScenarioSpec[Slot, Worker, QueueProposal]):
    def __init__(self, *, scenario_key: str, seed: Seed) -> None:
        self._scenario_key = scenario_key
        self._seed = seed

    @property
    def scenario_key(self) -> str:
        return self._scenario_key

    @property
    def seed(self) -> Seed:
        return self._seed

    @override
    def build_initial_state(self) -> SimulationState[Slot, Worker, QueueProposal]:
        workers = (
            Worker(participant_id="worker-fast", queue_id="expedite", max_parallel_jobs=1),
            Worker(participant_id="worker-flex", queue_id="standard", max_parallel_jobs=2),
        )
        slots = (
            Slot(
                segment_id="slot-expedite",
                participant_ids=("worker-fast",),
                queue_id="expedite",
                latency_target_ms=50,
            ),
            Slot(
                segment_id="slot-standard",
                participant_ids=("worker-flex",),
                queue_id="standard",
                latency_target_ms=200,
            ),
        )
        hot_job = Job(job_id="job-hot", queue_id="expedite", latency_ms=35, priority=9)
        aging_job = Job(job_id="job-aging", queue_id="standard", latency_ms=140, priority=6)
        stale_job = Job(job_id="job-stale", queue_id="standard", latency_ms=420, priority=1)
        proposals = (
            QueueProposal(
                proposal_id="proposal-enqueue",
                actor_id="worker-flex",
                action_key="enqueue",
                payload={"job": hot_job.as_payload(), "slot_id": "slot-expedite"},
            ),
            QueueProposal(
                proposal_id="proposal-promote",
                actor_id="worker-fast",
                action_key="promote",
                payload={
                    "job": aging_job.as_payload(),
                    "from_slot_id": "slot-standard",
                    "to_slot_id": "slot-expedite",
                },
            ),
            QueueProposal(
                proposal_id="proposal-drop",
                actor_id="worker-fast",
                action_key="drop",
                payload={"job": stale_job.as_payload(), "reason": "latency_budget_exceeded"},
            ),
        )
        return SimulationState[Slot, Worker, QueueProposal](
            step_index=0,
            seed=self.seed,
            snapshot_ref=SnapshotRef(
                snapshot_id=UUID("22222222-2222-2222-2222-222222222222"),
                tier="bronze",
                storage_key="snapshots/bronze/queue-scheduling-initial.json",
            ),
            segments=slots,
            participants=workers,
            pending_actions=proposals,
        )
