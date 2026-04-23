"""Tests for ``abdp.inspector.MemoryTraceStore`` and ``TraceStore`` protocol."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest

from abdp.core.types import Seed
from abdp.inspector import (
    MemoryTraceStore,
    TraceEvent,
    TraceStore,
    make_trace_event,
)


def _make(seq: int = 0, **overrides: Any) -> TraceEvent:
    base: dict[str, Any] = {
        "seed": Seed(0),
        "run_id": "run-1",
        "seq": seq,
        "step_index": seq,
        "event_type": "step.begin",
        "attributes": {},
        "timestamp_ns": seq,
        "parent_event_id": None,
    }
    base.update(overrides)
    return make_trace_event(**base)


def test_memory_store_implements_protocol() -> None:
    store = MemoryTraceStore()
    assert isinstance(store, TraceStore)


def test_memory_store_append_and_query_roundtrip() -> None:
    store = MemoryTraceStore()
    e0 = _make(seq=0)
    e1 = _make(seq=1)
    store.append(e0)
    store.append(e1)
    assert tuple(store.query(run_id="run-1")) == (e0, e1)


def test_memory_store_query_returns_only_matching_run_id() -> None:
    store = MemoryTraceStore()
    e_a = _make(seq=0, run_id="run-a")
    e_b = _make(seq=0, run_id="run-b")
    store.append(e_a)
    store.append(e_b)
    assert tuple(store.query(run_id="run-a")) == (e_a,)
    assert tuple(store.query(run_id="run-b")) == (e_b,)


def test_memory_store_rejects_duplicate_event_id() -> None:
    store = MemoryTraceStore()
    e = _make(seq=0)
    store.append(e)
    with pytest.raises(ValueError, match="duplicate event_id"):
        store.append(e)


def test_memory_store_query_filters_by_step_index() -> None:
    store = MemoryTraceStore()
    e0 = _make(seq=0, step_index=0)
    e1 = _make(seq=1, step_index=1)
    e2 = _make(seq=2, step_index=1)
    store.append(e0)
    store.append(e1)
    store.append(e2)
    assert tuple(store.query(run_id="run-1", step_index=1)) == (e1, e2)


def test_memory_store_query_filters_by_event_type() -> None:
    store = MemoryTraceStore()
    e0 = _make(seq=0, event_type="step.begin")
    e1 = _make(seq=1, event_type="step.end")
    store.append(e0)
    store.append(e1)
    assert tuple(store.query(run_id="run-1", event_type="step.end")) == (e1,)


def test_memory_store_query_unknown_run_id_returns_empty() -> None:
    store = MemoryTraceStore()
    store.append(_make(seq=0))
    assert tuple(store.query(run_id="missing")) == ()


def test_memory_store_close_is_idempotent() -> None:
    store = MemoryTraceStore()
    store.close()
    store.close()


def test_memory_store_preserves_insertion_order() -> None:
    store = MemoryTraceStore()
    seqs = (3, 1, 2, 0)
    events = tuple(_make(seq=s) for s in seqs)
    for ev in events:
        store.append(ev)
    assert tuple(store.query(run_id="run-1")) == events


def test_memory_store_append_rejects_non_trace_event() -> None:
    store = MemoryTraceStore()
    with pytest.raises(TypeError, match="TraceEvent"):
        store.append("not an event")  # type: ignore[arg-type]


def test_memory_store_query_unknown_filter_raises() -> None:
    store = MemoryTraceStore()
    store.append(_make(seq=0))
    with pytest.raises(TypeError, match="filter"):
        tuple(store.query(run_id="run-1", bogus="x"))


def test_memory_store_runs_returns_distinct_run_ids() -> None:
    store = MemoryTraceStore()
    store.append(_make(seq=0, run_id="run-a"))
    store.append(_make(seq=1, run_id="run-a"))
    store.append(_make(seq=0, run_id="run-b"))
    assert sorted(store.runs()) == ["run-a", "run-b"]


def test_memory_store_event_returns_event_by_id() -> None:
    store = MemoryTraceStore()
    e = _make(seq=0)
    store.append(e)
    assert store.event(e.event_id) == e


def test_memory_store_event_returns_none_for_unknown_id() -> None:
    store = MemoryTraceStore()
    assert store.event(UUID("00000000-0000-0000-0000-000000000099")) is None
