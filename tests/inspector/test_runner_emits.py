"""Tests for ``ScenarioRunner`` -> ``TraceRecorder`` event emission."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from abdp.core import Seed
from abdp.inspector import MemoryTraceStore, TraceRecorder
from abdp.scenario import ScenarioRunner
from abdp.simulation import ParticipantState, SegmentState, SimulationState

_Runner = ScenarioRunner[SegmentState, ParticipantState, Any]


def test_scenario_runner_does_not_require_recorder(
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
) -> None:
    initial = make_state(step_index=0, pending=())
    spec = make_spec(scenario_key="default", seed=Seed(7), initial=initial)
    agent = make_recording_agent(agent_id="a", proposals_to_emit=(make_action("x"),))
    resolver = make_recording_resolver()
    runner: _Runner = ScenarioRunner(agents=(agent,), resolver=resolver, max_steps=2)

    run = runner.run(spec)
    assert run.scenario_key == "default"


def test_scenario_runner_emits_step_begin_and_step_end_events(
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
) -> None:
    initial = make_state(step_index=0, pending=())
    spec = make_spec(scenario_key="emit", seed=Seed(7), initial=initial)
    agent = make_recording_agent(agent_id="a", proposals_to_emit=(make_action("x"),))
    resolver = make_recording_resolver()
    store = MemoryTraceStore()
    recorder = TraceRecorder(store=store, seed=Seed(7), run_id="run-emit")
    runner: _Runner = ScenarioRunner(agents=(agent,), resolver=resolver, max_steps=1, recorder=recorder)

    runner.run(spec)
    events = tuple(store.query(run_id="run-emit"))
    types = [e.event_type for e in events]
    assert "step.begin" in types
    assert "step.end" in types


def test_scenario_runner_emits_decision_evaluate_per_agent(
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
) -> None:
    initial = make_state(step_index=0, pending=())
    spec = make_spec(scenario_key="dec", seed=Seed(7), initial=initial)
    a1 = make_recording_agent(agent_id="agent-1", proposals_to_emit=(make_action("p1"),))
    a2 = make_recording_agent(agent_id="agent-2", proposals_to_emit=(make_action("p2"),))
    resolver = make_recording_resolver()
    store = MemoryTraceStore()
    recorder = TraceRecorder(store=store, seed=Seed(7), run_id="run-dec")
    runner: _Runner = ScenarioRunner(agents=(a1, a2), resolver=resolver, max_steps=1, recorder=recorder)

    runner.run(spec)
    decisions = tuple(store.query(run_id="run-dec", event_type="decision.evaluate"))
    assert len(decisions) == 2
    agent_ids = [e.attributes["agent_id"] for e in decisions]
    assert agent_ids == ["agent-1", "agent-2"]


def test_scenario_runner_emits_events_in_seq_order(
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
) -> None:
    initial = make_state(step_index=0, pending=())
    spec = make_spec(scenario_key="seq", seed=Seed(7), initial=initial)
    agent = make_recording_agent(agent_id="a", proposals_to_emit=(make_action("x"),))
    resolver = make_recording_resolver()
    store = MemoryTraceStore()
    recorder = TraceRecorder(store=store, seed=Seed(7), run_id="run-seq")
    runner: _Runner = ScenarioRunner(agents=(agent,), resolver=resolver, max_steps=2, recorder=recorder)

    runner.run(spec)
    events = tuple(store.query(run_id="run-seq"))
    seqs = [e.seq for e in events]
    assert seqs == sorted(seqs)
    assert seqs == list(range(len(seqs)))


def test_scenario_runner_with_recorder_records_step_indices(
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
) -> None:
    initial = make_state(step_index=0, pending=())
    spec = make_spec(scenario_key="idx", seed=Seed(7), initial=initial)
    agent = make_recording_agent(agent_id="a", proposals_to_emit=(make_action("x"),))
    resolver = make_recording_resolver()
    store = MemoryTraceStore()
    recorder = TraceRecorder(store=store, seed=Seed(7), run_id="run-idx")
    runner: _Runner = ScenarioRunner(agents=(agent,), resolver=resolver, max_steps=2, recorder=recorder)

    runner.run(spec)
    begins = tuple(store.query(run_id="run-idx", event_type="step.begin"))
    assert [e.step_index for e in begins] == [0, 1]


def test_trace_recorder_assigns_monotonic_seq() -> None:
    store = MemoryTraceStore()
    recorder = TraceRecorder(store=store, seed=Seed(0), run_id="r")
    e1 = recorder.record(event_type="x", step_index=0, attributes={})
    e2 = recorder.record(event_type="y", step_index=0, attributes={})
    assert e1.seq == 0
    assert e2.seq == 1


def test_trace_recorder_uses_deterministic_timestamp() -> None:
    store = MemoryTraceStore()
    recorder = TraceRecorder(store=store, seed=Seed(0), run_id="r")
    e = recorder.record(event_type="x", step_index=3, attributes={})
    assert e.timestamp_ns == 0
    e2 = recorder.record(event_type="y", step_index=3, attributes={})
    assert e2.timestamp_ns == 1
