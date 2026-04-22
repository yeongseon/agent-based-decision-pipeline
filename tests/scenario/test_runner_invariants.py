from __future__ import annotations

from collections.abc import Callable
from typing import Any

from abdp.core import Seed
from abdp.scenario import ScenarioRun, ScenarioRunner
from abdp.simulation import (
    ParticipantState,
    SegmentState,
    SimulationState,
)

_Runner = ScenarioRunner[SegmentState, ParticipantState, Any]


def test_run_invokes_agents_in_declared_order(
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
) -> None:
    initial = make_state(step_index=0, pending=())
    spec = make_spec(scenario_key="ord", seed=Seed(7), initial=initial)
    a1_emit = (make_action("a1"),)
    a2_emit = (make_action("a2"),)
    agent1 = make_recording_agent(agent_id="agent-1", proposals_to_emit=a1_emit)
    agent2 = make_recording_agent(agent_id="agent-2", proposals_to_emit=a2_emit)
    resolver = make_recording_resolver()

    runner: _Runner = ScenarioRunner(agents=(agent1, agent2), resolver=resolver, max_steps=1)
    run = runner.run(spec)

    assert tuple(d.agent_id for d in run.steps[0].decisions) == ("agent-1", "agent-2")
    assert agent1.seen_contexts[0].agent_id == "agent-1"
    assert agent1.seen_contexts[0].scenario_key == "ord"
    assert agent1.seen_contexts[0].step_index == 0
    assert agent1.seen_contexts[0].seed == Seed(7)
    assert agent1.seen_contexts[0].state is initial
    assert agent2.seen_contexts[0].agent_id == "agent-2"


def test_run_merges_pending_before_emissions_and_passes_merged_order_to_resolver(
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
) -> None:
    pending = (make_action("pending"),)
    initial = make_state(step_index=0, pending=pending)
    spec = make_spec(scenario_key="merge", seed=Seed(7), initial=initial)
    a1_emit = (make_action("a1"),)
    a2_emit = (make_action("a2-x"), make_action("a2-y"))
    agent1 = make_recording_agent(agent_id="agent-1", proposals_to_emit=a1_emit)
    agent2 = make_recording_agent(agent_id="agent-2", proposals_to_emit=a2_emit)
    resolver = make_recording_resolver()

    runner: _Runner = ScenarioRunner(agents=(agent1, agent2), resolver=resolver, max_steps=1)
    run = runner.run(spec)

    expected = pending + a1_emit + a2_emit
    assert run.steps[0].proposals == expected
    assert resolver.received == [(0, expected)]


def test_run_records_empty_terminal_step_and_skips_resolver_when_no_proposals(
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
    decision_cls: type,
) -> None:
    initial = make_state(step_index=0, pending=())
    spec = make_spec(scenario_key="quiet", seed=Seed(0), initial=initial)
    silent = make_recording_agent(agent_id="silent", proposals_to_emit=())
    resolver = make_recording_resolver()

    runner: _Runner = ScenarioRunner(agents=(silent,), resolver=resolver, max_steps=5)
    run = runner.run(spec)

    assert run.step_count == 1
    assert run.steps[0].proposals == ()
    assert run.steps[0].state is initial
    assert run.steps[0].decisions == (decision_cls(agent_id="silent", proposals=()),)
    assert silent.seen_contexts != []
    assert silent.seen_contexts[0].step_index == 0
    assert resolver.received == []
    assert run.final_state is initial


def test_run_stops_after_max_steps_resolutions(
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
) -> None:
    initial = make_state(step_index=0, pending=())
    spec = make_spec(scenario_key="bounded", seed=Seed(0), initial=initial)
    emitter = make_recording_agent(agent_id="emit", proposals_to_emit=(make_action("e"),))
    resolver = make_recording_resolver()

    runner: _Runner = ScenarioRunner(agents=(emitter,), resolver=resolver, max_steps=2)
    run = runner.run(spec)

    assert run.step_count == 2
    assert len(resolver.received) == 2
    assert run.final_state.step_index == 2
    assert run.steps[0].state.step_index == 0
    assert run.steps[1].state.step_index == 1


def test_run_is_deterministic_for_same_spec_agents_and_resolver(
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
) -> None:
    initial = make_state(step_index=0, pending=(make_action("p"),))
    spec = make_spec(scenario_key="det", seed=Seed(42), initial=initial)

    def _build_run() -> ScenarioRun[SegmentState, ParticipantState, Any]:
        agent = make_recording_agent(
            agent_id="a",
            proposals_to_emit=(make_action("x"), make_action("y")),
        )
        resolver = make_recording_resolver()
        runner: _Runner = ScenarioRunner(agents=(agent,), resolver=resolver, max_steps=3)
        return runner.run(spec)

    assert _build_run() == _build_run()


def test_run_with_zero_max_steps_returns_initial_state_without_polling_agents(
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
) -> None:
    initial = make_state(step_index=0, pending=(make_action("ignored"),))
    spec = make_spec(scenario_key="zero", seed=Seed(0), initial=initial)
    agent = make_recording_agent(agent_id="a", proposals_to_emit=(make_action("x"),))
    resolver = make_recording_resolver()

    runner: _Runner = ScenarioRunner(agents=(agent,), resolver=resolver, max_steps=0)
    run = runner.run(spec)

    assert run.step_count == 0
    assert run.final_state is initial
    assert agent.seen_contexts == []
    assert resolver.received == []
