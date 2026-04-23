"""Determinism tests: same ``(seed, scenario, run_id)`` -> byte-identical traces."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from abdp.core import Seed
from abdp.inspector import (
    MemoryTraceStore,
    SQLiteTraceStore,
    TraceEvent,
    TraceRecorder,
)
from abdp.scenario import ScenarioRunner
from abdp.simulation import ParticipantState, SegmentState, SimulationState

_Runner = ScenarioRunner[SegmentState, ParticipantState, Any]

_SEED = Seed(7)
_RUN_ID = "run-deterministic"


def _event_tuple(ev: TraceEvent) -> tuple[Any, ...]:
    return (
        ev.event_id,
        ev.run_id,
        ev.seq,
        ev.step_index,
        ev.event_type,
        tuple(sorted(ev.attributes.items())),
        ev.timestamp_ns,
        ev.parent_event_id,
    )


def _execute_scenario(
    *,
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
    store: MemoryTraceStore | SQLiteTraceStore,
) -> None:
    initial = make_state(step_index=0, pending=())
    spec = make_spec(scenario_key="determinism", seed=_SEED, initial=initial)
    agent = make_recording_agent(agent_id="a", proposals_to_emit=(make_action("x"),))
    resolver = make_recording_resolver()
    recorder = TraceRecorder(store=store, seed=_SEED, run_id=_RUN_ID)
    runner: _Runner = ScenarioRunner(agents=(agent,), resolver=resolver, max_steps=3, recorder=recorder)
    runner.run(spec)


def test_two_runs_with_same_seed_produce_byte_identical_traces(
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
) -> None:
    store_a = MemoryTraceStore()
    store_b = MemoryTraceStore()
    _execute_scenario(
        make_action=make_action,
        make_state=make_state,
        make_spec=make_spec,
        make_recording_agent=make_recording_agent,
        make_recording_resolver=make_recording_resolver,
        store=store_a,
    )
    _execute_scenario(
        make_action=make_action,
        make_state=make_state,
        make_spec=make_spec,
        make_recording_agent=make_recording_agent,
        make_recording_resolver=make_recording_resolver,
        store=store_b,
    )

    events_a = [_event_tuple(e) for e in store_a.query(run_id=_RUN_ID)]
    events_b = [_event_tuple(e) for e in store_b.query(run_id=_RUN_ID)]
    assert events_a == events_b
    assert len(events_a) > 0


def test_event_ids_only_depend_on_seed_run_id_seq() -> None:
    store = MemoryTraceStore()
    recorder = TraceRecorder(store=store, seed=_SEED, run_id=_RUN_ID)
    a = recorder.record(event_type="step.begin", step_index=0, attributes={"x": 1})
    b = recorder.record(event_type="step.end", step_index=99, attributes={"y": "z"})

    store2 = MemoryTraceStore()
    recorder2 = TraceRecorder(store=store2, seed=_SEED, run_id=_RUN_ID)
    a2 = recorder2.record(event_type="other", step_index=42, attributes={"q": True})
    b2 = recorder2.record(event_type="another", step_index=0, attributes={})

    assert a.event_id == a2.event_id
    assert b.event_id == b2.event_id


def test_different_seeds_produce_different_event_ids() -> None:
    store_a = MemoryTraceStore()
    store_b = MemoryTraceStore()
    rec_a = TraceRecorder(store=store_a, seed=Seed(1), run_id=_RUN_ID)
    rec_b = TraceRecorder(store=store_b, seed=Seed(2), run_id=_RUN_ID)
    e_a = rec_a.record(event_type="x", step_index=0, attributes={})
    e_b = rec_b.record(event_type="x", step_index=0, attributes={})
    assert e_a.event_id != e_b.event_id


def test_different_run_ids_produce_different_event_ids() -> None:
    store = MemoryTraceStore()
    rec_a = TraceRecorder(store=store, seed=_SEED, run_id="run-a")
    rec_b = TraceRecorder(store=store, seed=_SEED, run_id="run-b")
    e_a = rec_a.record(event_type="x", step_index=0, attributes={})
    e_b = rec_b.record(event_type="x", step_index=0, attributes={})
    assert e_a.event_id != e_b.event_id


def test_sqlite_store_round_trip_preserves_event_tuples(
    tmp_path: Any,
    make_action: Callable[[str], Any],
    make_state: Callable[..., SimulationState[SegmentState, ParticipantState, Any]],
    make_spec: type,
    make_recording_agent: type,
    make_recording_resolver: type,
) -> None:
    db = tmp_path / "trace.db"
    sqlite_store = SQLiteTraceStore(db)
    _execute_scenario(
        make_action=make_action,
        make_state=make_state,
        make_spec=make_spec,
        make_recording_agent=make_recording_agent,
        make_recording_resolver=make_recording_resolver,
        store=sqlite_store,
    )
    sqlite_store.close()

    mem_store = MemoryTraceStore()
    _execute_scenario(
        make_action=make_action,
        make_state=make_state,
        make_spec=make_spec,
        make_recording_agent=make_recording_agent,
        make_recording_resolver=make_recording_resolver,
        store=mem_store,
    )

    reopened = SQLiteTraceStore(db)
    sqlite_events = [_event_tuple(e) for e in reopened.query(run_id=_RUN_ID)]
    reopened.close()
    mem_events = [_event_tuple(e) for e in mem_store.query(run_id=_RUN_ID)]
    assert sqlite_events == mem_events
