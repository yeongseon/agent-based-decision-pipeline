"""Integration test for the queue scheduling example (#103).

Mirrors the credit underwriting integration test shape, but exercises the
``ScenarioRunner.max_steps`` cap as the termination boundary instead of natural
proposal exhaustion. Two ``QueueWorkerAgent`` instances emit per-step heartbeats
that keep proposals flowing until ``max_steps`` is reached.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import assert_type

import pytest

import abdp
from abdp.agents import Agent
from abdp.core.types import Seed
from abdp.scenario import ActionResolver, ScenarioRun, ScenarioRunner
from examples.queue_scheduling import (
    QueueProposal,
    QueueResolver,
    QueueScenario,
    QueueWorkerAgent,
    Slot,
    Worker,
)
from examples.queue_scheduling.__main__ import main as queue_main

REPO_ROOT = Path(__file__).resolve().parents[2]
SEED = Seed(11)
SCENARIO_KEY = "latency-baseline"


def _build_runner() -> ScenarioRunner[Slot, Worker, QueueProposal]:
    return ScenarioRunner[Slot, Worker, QueueProposal](
        agents=(
            QueueWorkerAgent(agent_id="worker-fast", queue_id="expedite"),
            QueueWorkerAgent(agent_id="worker-flex", queue_id="standard"),
        ),
        resolver=QueueResolver(),
        max_steps=3,
    )


def test_queue_worker_agent_satisfies_agent_protocol() -> None:
    agent = QueueWorkerAgent(agent_id="worker-fast", queue_id="expedite")
    assert isinstance(agent, Agent)
    assert agent.agent_id == "worker-fast"


def test_queue_resolver_satisfies_action_resolver_protocol() -> None:
    assert isinstance(QueueResolver(), ActionResolver)


def test_run_is_deterministic_for_fixed_seed() -> None:
    runner = _build_runner()
    run_a = runner.run(QueueScenario(scenario_key=SCENARIO_KEY, seed=SEED))
    run_b = runner.run(QueueScenario(scenario_key=SCENARIO_KEY, seed=SEED))
    assert run_a == run_b


def test_run_terminates_via_max_steps_cap() -> None:
    run = _build_runner().run(QueueScenario(scenario_key=SCENARIO_KEY, seed=SEED))
    _ = assert_type(run, ScenarioRun[Slot, Worker, QueueProposal])
    assert run.scenario_key == SCENARIO_KEY
    assert run.seed == SEED
    assert run.step_count == 3
    assert run.final_state.step_index == 3
    assert run.final_state.pending_actions == ()


def test_first_step_merges_initial_pending_with_worker_heartbeats() -> None:
    run = _build_runner().run(QueueScenario(scenario_key=SCENARIO_KEY, seed=SEED))
    keys = sorted(p.action_key for p in run.steps[0].proposals)
    assert keys == ["drop", "enqueue", "heartbeat", "heartbeat", "promote"]


def test_subsequent_steps_only_carry_worker_heartbeats() -> None:
    run = _build_runner().run(QueueScenario(scenario_key=SCENARIO_KEY, seed=SEED))
    for step in run.steps[1:]:
        keys = tuple(p.action_key for p in step.proposals)
        assert keys == ("heartbeat", "heartbeat")


def test_resolver_rejects_unknown_action_key() -> None:
    state = QueueScenario(scenario_key=SCENARIO_KEY, seed=SEED).build_initial_state()
    bad = QueueProposal(
        proposal_id="bad-001",
        actor_id="worker-fast",
        action_key="mystery",
        payload={},
    )
    with pytest.raises(ValueError, match="Unknown action_key"):
        QueueResolver().resolve(state, (bad,))


def test_main_entrypoint_prints_deterministic_summary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    queue_main()
    captured = capsys.readouterr()
    assert "scenario_key=latency-baseline" in captured.out
    assert "seed=11" in captured.out
    assert "step_count=3" in captured.out
    assert "final_step_index=3" in captured.out
    assert "max_steps_reached=True" in captured.out


def test_no_abdp_source_files_modified_by_example() -> None:
    fixture_path = Path(inspect.getfile(QueueScenario)).resolve()
    abdp_pkg_path = Path(inspect.getfile(abdp)).resolve().parent
    assert fixture_path.is_relative_to(REPO_ROOT / "examples")
    assert not fixture_path.is_relative_to(REPO_ROOT / "src")
    assert abdp_pkg_path == REPO_ROOT / "src" / "abdp"
