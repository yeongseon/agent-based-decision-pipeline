"""Compatibility proof: queue scheduling as the second domain over abdp.simulation contracts."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import assert_type
from uuid import UUID

import abdp
from abdp.core.types import Seed, is_json_value
from abdp.simulation import (
    ActionProposal,
    ParticipantState,
    ScenarioSpec,
    SegmentState,
    SimulationState,
    SnapshotRef,
)
from tests.fixtures.queue_scheduling_domain import (
    Job,
    QueueProposal,
    QueueScenario,
    Slot,
    Worker,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

SCENARIO_KEY = "latency-baseline"
SEED = Seed(11)
SNAPSHOT_UUID = UUID("22222222-2222-2222-2222-222222222222")
SNAPSHOT_TIER = "bronze"
SNAPSHOT_STORAGE_KEY = "snapshots/bronze/queue-scheduling-initial.json"


def _build_scenario() -> QueueScenario:
    return QueueScenario(scenario_key=SCENARIO_KEY, seed=SEED)


def _build_state() -> SimulationState[Slot, Worker, QueueProposal]:
    return _build_scenario().build_initial_state()


def test_worker_satisfies_participant_state_protocol() -> None:
    worker = Worker(participant_id="worker-fast", queue_id="expedite", max_parallel_jobs=1)

    assert isinstance(worker, ParticipantState)
    assert worker.participant_id == "worker-fast"
    assert isinstance(worker.participant_id, str)
    assert worker.queue_id == "expedite"
    assert worker.max_parallel_jobs == 1


def test_slot_satisfies_segment_state_protocol() -> None:
    slot = Slot(
        segment_id="slot-expedite",
        participant_ids=("worker-fast",),
        queue_id="expedite",
        latency_target_ms=50,
    )

    assert isinstance(slot, SegmentState)
    assert slot.segment_id == "slot-expedite"
    assert isinstance(slot.participant_ids, tuple)
    assert slot.participant_ids == ("worker-fast",)
    assert slot.queue_id == "expedite"
    assert slot.latency_target_ms == 50


def test_proposal_satisfies_action_proposal_protocol() -> None:
    job = Job(job_id="job-hot", queue_id="expedite", latency_ms=35, priority=9)
    proposal = QueueProposal(
        proposal_id="proposal-enqueue",
        actor_id="worker-flex",
        action_key="enqueue",
        payload={"job": job.as_payload(), "slot_id": "slot-expedite"},
    )

    assert isinstance(proposal, ActionProposal)
    assert proposal.proposal_id == "proposal-enqueue"
    assert proposal.actor_id == "worker-flex"
    assert proposal.action_key == "enqueue"
    assert proposal.payload == {
        "job": {
            "job_id": "job-hot",
            "queue_id": "expedite",
            "latency_ms": 35,
            "priority": 9,
        },
        "slot_id": "slot-expedite",
    }


def test_scenario_satisfies_scenario_spec_protocol() -> None:
    scenario = _build_scenario()

    assert isinstance(scenario, ScenarioSpec)
    assert scenario.scenario_key == SCENARIO_KEY
    assert scenario.seed == SEED

    state = scenario.build_initial_state()
    assert_type(state, SimulationState[Slot, Worker, QueueProposal])
    assert isinstance(state, SimulationState)


def test_build_initial_state_returns_valid_simulation_state() -> None:
    state = _build_state()

    assert state.step_index == 0
    assert state.seed == SEED
    assert isinstance(state.snapshot_ref, SnapshotRef)
    assert state.snapshot_ref.snapshot_id == SNAPSHOT_UUID
    assert state.snapshot_ref.tier == SNAPSHOT_TIER
    assert state.snapshot_ref.storage_key == SNAPSHOT_STORAGE_KEY


def test_simulation_state_has_expected_field_types_and_ordering() -> None:
    state = _build_state()

    assert_type(state.segments, tuple[Slot, ...])
    assert_type(state.participants, tuple[Worker, ...])
    assert_type(state.pending_actions, tuple[QueueProposal, ...])

    assert isinstance(state.segments, tuple)
    assert isinstance(state.participants, tuple)
    assert isinstance(state.pending_actions, tuple)

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


def test_no_abdp_source_files_were_modified_by_this_fixture() -> None:
    fixture_path = Path(inspect.getfile(QueueScenario)).resolve()
    abdp_pkg_path = Path(inspect.getfile(abdp)).resolve().parent
    sim_state_path = Path(inspect.getfile(SimulationState)).resolve()

    assert fixture_path.is_relative_to(REPO_ROOT / "tests")
    assert not fixture_path.is_relative_to(REPO_ROOT / "src")
    assert abdp_pkg_path == REPO_ROOT / "src" / "abdp"
    assert sim_state_path == REPO_ROOT / "src" / "abdp" / "simulation" / "state.py"


def test_payload_is_json_value() -> None:
    state = _build_state()
    job = Job(job_id="probe", queue_id="standard", latency_ms=100, priority=5)

    assert is_json_value(job.as_payload())
    for proposal in state.pending_actions:
        assert is_json_value(proposal.payload)
