"""Tests for ``abdp.inspector.SQLiteTraceStore``."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from abdp.core.types import Seed
from abdp.inspector import (
    SQLiteTraceStore,
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


def test_sqlite_store_implements_protocol(tmp_path: Path) -> None:
    store = SQLiteTraceStore(tmp_path / "t.db")
    try:
        assert isinstance(store, TraceStore)
    finally:
        store.close()


def test_sqlite_store_in_memory_append_and_query(tmp_path: Path) -> None:
    store = SQLiteTraceStore(":memory:")
    try:
        e0 = _make(seq=0)
        e1 = _make(seq=1)
        store.append(e0)
        store.append(e1)
        assert tuple(store.query(run_id="run-1")) == (e0, e1)
    finally:
        store.close()


def test_sqlite_store_persists_across_reopen(tmp_path: Path) -> None:
    db = tmp_path / "t.db"
    store = SQLiteTraceStore(db)
    e0 = _make(seq=0)
    e1 = _make(seq=1, event_type="step.end")
    store.append(e0)
    store.append(e1)
    store.close()

    reopened = SQLiteTraceStore(db)
    try:
        assert tuple(reopened.query(run_id="run-1")) == (e0, e1)
    finally:
        reopened.close()


def test_sqlite_store_round_trips_attributes(tmp_path: Path) -> None:
    store = SQLiteTraceStore(":memory:")
    try:
        ev = _make(seq=0, attributes={"s": "v", "i": 1, "f": 1.5, "b": True})
        store.append(ev)
        (got,) = tuple(store.query(run_id="run-1"))
        assert got == ev
        assert got.attributes == {"s": "v", "i": 1, "f": 1.5, "b": True}
    finally:
        store.close()


def test_sqlite_store_round_trips_parent_event_id(tmp_path: Path) -> None:
    store = SQLiteTraceStore(":memory:")
    try:
        parent = _make(seq=0)
        child = _make(seq=1, parent_event_id=parent.event_id)
        store.append(parent)
        store.append(child)
        events = tuple(store.query(run_id="run-1"))
        assert events == (parent, child)
        assert events[1].parent_event_id == parent.event_id
    finally:
        store.close()


def test_sqlite_store_rejects_duplicate_event_id(tmp_path: Path) -> None:
    store = SQLiteTraceStore(":memory:")
    try:
        e = _make(seq=0)
        store.append(e)
        with pytest.raises(ValueError, match="duplicate event_id"):
            store.append(e)
    finally:
        store.close()


def test_sqlite_store_filters_by_step_index(tmp_path: Path) -> None:
    store = SQLiteTraceStore(":memory:")
    try:
        e0 = _make(seq=0, step_index=0)
        e1 = _make(seq=1, step_index=1)
        store.append(e0)
        store.append(e1)
        assert tuple(store.query(run_id="run-1", step_index=1)) == (e1,)
    finally:
        store.close()


def test_sqlite_store_filters_by_event_type(tmp_path: Path) -> None:
    store = SQLiteTraceStore(":memory:")
    try:
        e0 = _make(seq=0, event_type="step.begin")
        e1 = _make(seq=1, event_type="step.end")
        store.append(e0)
        store.append(e1)
        assert tuple(store.query(run_id="run-1", event_type="step.end")) == (e1,)
    finally:
        store.close()


def test_sqlite_store_close_is_idempotent(tmp_path: Path) -> None:
    store = SQLiteTraceStore(tmp_path / "t.db")
    store.close()
    store.close()


def test_sqlite_store_append_after_close_raises(tmp_path: Path) -> None:
    store = SQLiteTraceStore(":memory:")
    store.close()
    with pytest.raises(RuntimeError, match="closed"):
        store.append(_make(seq=0))


def test_sqlite_store_query_returns_seq_order(tmp_path: Path) -> None:
    store = SQLiteTraceStore(":memory:")
    try:
        events = tuple(_make(seq=s) for s in (3, 1, 2, 0))
        for ev in events:
            store.append(ev)
        got = tuple(store.query(run_id="run-1"))
        assert [e.seq for e in got] == [0, 1, 2, 3]
    finally:
        store.close()


def test_sqlite_store_runs_returns_distinct_run_ids(tmp_path: Path) -> None:
    store = SQLiteTraceStore(":memory:")
    try:
        store.append(_make(seq=0, run_id="run-a"))
        store.append(_make(seq=0, run_id="run-b"))
        assert sorted(store.runs()) == ["run-a", "run-b"]
    finally:
        store.close()


def test_sqlite_store_event_returns_event_by_id(tmp_path: Path) -> None:
    store = SQLiteTraceStore(":memory:")
    try:
        e = _make(seq=0)
        store.append(e)
        assert store.event(e.event_id) == e
    finally:
        store.close()


def test_sqlite_store_event_returns_none_for_unknown_id(tmp_path: Path) -> None:
    from uuid import UUID

    store = SQLiteTraceStore(":memory:")
    try:
        assert store.event(UUID("00000000-0000-0000-0000-000000000099")) is None
    finally:
        store.close()


def test_sqlite_store_query_unknown_filter_raises(tmp_path: Path) -> None:
    store = SQLiteTraceStore(":memory:")
    try:
        store.append(_make(seq=0))
        with pytest.raises(TypeError, match="filter"):
            tuple(store.query(run_id="run-1", bogus="x"))
    finally:
        store.close()


def test_sqlite_store_append_rejects_non_trace_event(tmp_path: Path) -> None:
    store = SQLiteTraceStore(":memory:")
    try:
        with pytest.raises(TypeError, match="TraceEvent"):
            store.append("not an event")  # type: ignore[arg-type]
    finally:
        store.close()
