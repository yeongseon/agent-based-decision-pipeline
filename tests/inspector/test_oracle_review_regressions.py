"""Regression tests for Oracle review (PR #174) findings on issue #172."""

from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path
from uuid import UUID

import pytest

from abdp.cli.__main__ import main
from abdp.core import Seed
from abdp.inspector import (
    MemoryTraceStore,
    SQLiteTraceStore,
    TraceEvent,
    TraceRecorder,
    make_trace_event,
)


def _ev(seq: int = 0, *, run_id: str = "run-x") -> TraceEvent:
    return make_trace_event(
        seed=Seed(7),
        run_id=run_id,
        seq=seq,
        step_index=0,
        event_type="x",
        attributes={},
        timestamp_ns=seq,
        parent_event_id=None,
    )


def test_trace_event_attributes_are_isolated_from_external_dict_mutation() -> None:
    src: dict[str, object] = {"a": 1}
    ev = make_trace_event(
        seed=Seed(0),
        run_id="r",
        seq=0,
        step_index=0,
        event_type="x",
        attributes=src,
        timestamp_ns=0,
        parent_event_id=None,
    )
    src["a"] = 999
    src["b"] = "added"
    assert dict(ev.attributes) == {"a": 1}


def test_trace_event_attributes_mapping_is_not_writable() -> None:
    ev = make_trace_event(
        seed=Seed(0),
        run_id="r",
        seq=0,
        step_index=0,
        event_type="x",
        attributes={"a": 1},
        timestamp_ns=0,
        parent_event_id=None,
    )
    with pytest.raises(TypeError):
        ev.attributes["a"] = 2  # type: ignore[index]


def test_trace_event_rejects_nan_attribute_value() -> None:
    with pytest.raises(ValueError):
        make_trace_event(
            seed=Seed(0),
            run_id="r",
            seq=0,
            step_index=0,
            event_type="x",
            attributes={"k": math.nan},
            timestamp_ns=0,
            parent_event_id=None,
        )


def test_trace_event_rejects_positive_infinity_attribute_value() -> None:
    with pytest.raises(ValueError):
        make_trace_event(
            seed=Seed(0),
            run_id="r",
            seq=0,
            step_index=0,
            event_type="x",
            attributes={"k": math.inf},
            timestamp_ns=0,
            parent_event_id=None,
        )


def test_trace_event_rejects_negative_infinity_attribute_value() -> None:
    with pytest.raises(ValueError):
        make_trace_event(
            seed=Seed(0),
            run_id="r",
            seq=0,
            step_index=0,
            event_type="x",
            attributes={"k": -math.inf},
            timestamp_ns=0,
            parent_event_id=None,
        )


def test_memory_store_rejects_duplicate_run_id_seq_pair() -> None:
    store = MemoryTraceStore()
    a = make_trace_event(
        seed=Seed(1),
        run_id="r",
        seq=0,
        step_index=0,
        event_type="x",
        attributes={},
        timestamp_ns=0,
        parent_event_id=None,
    )
    b = make_trace_event(
        seed=Seed(2),
        run_id="r",
        seq=0,
        step_index=0,
        event_type="y",
        attributes={},
        timestamp_ns=0,
        parent_event_id=None,
    )
    assert a.event_id != b.event_id
    store.append(a)
    with pytest.raises(ValueError):
        store.append(b)


def test_sqlite_store_duplicate_run_id_seq_message_mentions_run_id_seq(tmp_path: Path) -> None:
    store = SQLiteTraceStore(tmp_path / "t.db")
    a = make_trace_event(
        seed=Seed(1),
        run_id="r",
        seq=0,
        step_index=0,
        event_type="x",
        attributes={},
        timestamp_ns=0,
        parent_event_id=None,
    )
    b = make_trace_event(
        seed=Seed(2),
        run_id="r",
        seq=0,
        step_index=0,
        event_type="y",
        attributes={},
        timestamp_ns=0,
        parent_event_id=None,
    )
    store.append(a)
    with pytest.raises(ValueError) as exc:
        store.append(b)
    store.close()
    assert "(run_id, seq)" in str(exc.value)


class _FlakyStore:
    def __init__(self) -> None:
        self.calls = 0
        self.appended: list[TraceEvent] = []

    def append(self, event: TraceEvent) -> None:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("simulated transient failure")
        self.appended.append(event)


def test_recorder_does_not_advance_seq_when_store_append_fails() -> None:
    store = _FlakyStore()
    recorder = TraceRecorder(store=store, seed=Seed(0), run_id="r")  # type: ignore[arg-type]
    with pytest.raises(RuntimeError):
        recorder.record(event_type="x", step_index=0, attributes={})
    ok = recorder.record(event_type="x", step_index=0, attributes={})
    assert ok.seq == 0


def test_inspect_cli_returns_two_on_corrupt_attributes_json(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    db = tmp_path / "trace.db"
    store = SQLiteTraceStore(db)
    store.close()
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO trace_events VALUES (?,?,?,?,?,?,?,?)",
        (
            str(UUID(int=1)),
            "run-x",
            0,
            0,
            "step.begin",
            "this-is-not-json",
            0,
            None,
        ),
    )
    conn.commit()
    conn.close()

    exit_code = main(["inspect", "run-x", "--db", str(db)])
    captured = capsysbinary.readouterr()
    assert exit_code == 2
    assert captured.out == b""
    assert captured.err != b""


def test_inspect_cli_returns_two_on_corrupt_event_id(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    db = tmp_path / "trace.db"
    store = SQLiteTraceStore(db)
    store.close()
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO trace_events VALUES (?,?,?,?,?,?,?,?)",
        (
            "not-a-uuid",
            "run-x",
            0,
            0,
            "step.begin",
            json.dumps({}),
            0,
            None,
        ),
    )
    conn.commit()
    conn.close()

    exit_code = main(["inspect", "run-x", "--db", str(db)])
    captured = capsysbinary.readouterr()
    assert exit_code == 2
    assert captured.out == b""
    assert captured.err != b""
