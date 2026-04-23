"""SQLite-backed :class:`TraceStore` implementation.

Persists :class:`TraceEvent` records into a single ``trace_events`` table
keyed by ``event_id``. Attribute mappings and ``parent_event_id`` are
serialized as JSON / nullable TEXT columns. Suitable for local
development inspection; production deployments should use a future
OTLP/Postgres adapter (out of scope for this issue).
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from uuid import UUID

from abdp.inspector.event import TraceEvent
from abdp.inspector.store import validate_query_filters

__all__ = ["SQLiteTraceStore"]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS trace_events (
    event_id        TEXT PRIMARY KEY,
    run_id          TEXT NOT NULL,
    seq             INTEGER NOT NULL,
    step_index      INTEGER NOT NULL,
    event_type      TEXT NOT NULL,
    attributes_json TEXT NOT NULL,
    timestamp_ns    INTEGER NOT NULL,
    parent_event_id TEXT,
    UNIQUE(run_id, seq)
);
CREATE INDEX IF NOT EXISTS idx_trace_run ON trace_events(run_id, seq);
CREATE INDEX IF NOT EXISTS idx_trace_step ON trace_events(run_id, step_index);
CREATE INDEX IF NOT EXISTS idx_trace_type ON trace_events(run_id, event_type);
"""


class SQLiteTraceStore:
    def __init__(self, path: str | Path) -> None:
        self._path = str(path)
        self._conn: sqlite3.Connection | None = sqlite3.connect(self._path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def append(self, event: TraceEvent) -> None:
        conn = self._require_open()
        if not isinstance(event, TraceEvent):
            raise TypeError(f"expected TraceEvent, got {type(event).__name__}")
        try:
            conn.execute(
                "INSERT INTO trace_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(event.event_id),
                    event.run_id,
                    event.seq,
                    event.step_index,
                    event.event_type,
                    json.dumps(dict(event.attributes), sort_keys=True),
                    event.timestamp_ns,
                    str(event.parent_event_id) if event.parent_event_id else None,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError(
                f"duplicate event_id or (run_id, seq) collision for event_id={event.event_id}: {exc}"
            ) from exc
        conn.commit()

    def query(self, *, run_id: str, **filters: Any) -> Iterator[TraceEvent]:
        validate_query_filters(filters)
        conn = self._require_open()
        sql = "SELECT * FROM trace_events WHERE run_id = ?"
        params: list[Any] = [run_id]
        if (step_index := filters.get("step_index")) is not None:
            sql += " AND step_index = ?"
            params.append(step_index)
        if (event_type := filters.get("event_type")) is not None:
            sql += " AND event_type = ?"
            params.append(event_type)
        sql += " ORDER BY seq"
        for row in conn.execute(sql, params):
            yield _row_to_event(row)

    def event(self, event_id: UUID) -> TraceEvent | None:
        conn = self._require_open()
        row = conn.execute("SELECT * FROM trace_events WHERE event_id = ?", (str(event_id),)).fetchone()
        return _row_to_event(row) if row is not None else None

    def runs(self) -> Iterator[str]:
        conn = self._require_open()
        for (run_id,) in conn.execute("SELECT DISTINCT run_id FROM trace_events"):
            yield run_id

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _require_open(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("SQLiteTraceStore is closed")
        return self._conn


def _row_to_event(row: tuple[Any, ...]) -> TraceEvent:
    (event_id, run_id, seq, step_index, event_type, attrs_json, ts_ns, parent_id) = row
    return TraceEvent(
        event_id=UUID(event_id),
        run_id=run_id,
        seq=seq,
        step_index=step_index,
        event_type=event_type,
        attributes=json.loads(attrs_json),
        timestamp_ns=ts_ns,
        parent_event_id=UUID(parent_id) if parent_id else None,
    )
