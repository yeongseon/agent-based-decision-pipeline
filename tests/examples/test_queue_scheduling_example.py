from __future__ import annotations

from abdp.core.types import Seed
from abdp.simulation import SimulationState
from examples.queue_scheduling.domain import QueueProposal, QueueScenario, Slot, Worker


def test_queue_scheduling_example_import_path_builds_expected_state() -> None:
    scenario = QueueScenario(scenario_key="latency-baseline", seed=Seed(11))

    state = scenario.build_initial_state()

    assert isinstance(state, SimulationState)
    assert tuple(slot.segment_id for slot in state.segments) == (
        "slot-expedite",
        "slot-standard",
    )
    assert tuple(worker.participant_id for worker in state.participants) == (
        "worker-fast",
        "worker-flex",
    )
    assert tuple(proposal.action_key for proposal in state.pending_actions) == (
        "enqueue",
        "promote",
        "drop",
    )
    assert all(isinstance(slot, Slot) for slot in state.segments)
    assert all(isinstance(worker, Worker) for worker in state.participants)
    assert all(isinstance(proposal, QueueProposal) for proposal in state.pending_actions)
