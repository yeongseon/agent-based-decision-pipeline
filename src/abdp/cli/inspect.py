"""``abdp inspect`` subcommand: query a SQLite trace store and emit JSON Lines.

Each emitted line is a JSON object with the full :class:`abdp.inspector.TraceEvent`
shape (UUIDs as strings, ``parent_event_id`` nullable). Events are ordered by
``seq``. Optional ``--step`` and ``--event-type`` filters are translated into
``TraceStore.query`` keyword arguments. Loader and query errors return ``2`` with
a single-line stderr message; an unknown ``run_id`` is not an error and exits
``0`` with no output.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

from abdp.inspector import SQLiteTraceStore, TraceEvent

__all__ = ["InspectError", "inspect", "inspect_command"]

_EXIT_OK = 0
_EXIT_ERROR = 2


class InspectError(Exception):
    """Raised when a trace store cannot be opened or queried."""


def inspect(
    run_id: str,
    *,
    db: Path,
    step: int | None = None,
    event_type: str | None = None,
    output: Path | None = None,
) -> int:
    if step is not None and step < 0:
        print("--step must be a non-negative integer", file=sys.stderr)
        return _EXIT_ERROR
    if not db.exists():
        print(f"trace database not found: {db}", file=sys.stderr)
        return _EXIT_ERROR
    try:
        store = _open_store(db)
    except InspectError as exc:
        print(str(exc).splitlines()[0], file=sys.stderr)
        return _EXIT_ERROR
    try:
        filters: dict[str, Any] = {}
        if step is not None:
            filters["step_index"] = step
        if event_type is not None:
            filters["event_type"] = event_type
        try:
            events = list(store.query(run_id=run_id, **filters))
        except (sqlite3.DatabaseError, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise InspectError(f"malformed trace database: {exc}") from exc
        rendered = _render_jsonl(events)
        _write_output(rendered, output)
    except (OSError, InspectError) as exc:
        print(str(exc).splitlines()[0] if str(exc) else type(exc).__name__, file=sys.stderr)
        return _EXIT_ERROR
    finally:
        store.close()
    return _EXIT_OK


def _open_store(db: Path) -> SQLiteTraceStore:
    try:
        return SQLiteTraceStore(db)
    except sqlite3.DatabaseError as exc:
        raise InspectError(f"invalid trace database: {exc}") from exc


def inspect_command(args: argparse.Namespace) -> int:
    return inspect(
        cast(str, args.run_id),
        db=cast(Path, args.db),
        step=cast("int | None", args.step),
        event_type=cast("str | None", args.event_type),
        output=cast("Path | None", args.output),
    )


def _render_jsonl(events: Iterable[TraceEvent]) -> str:
    lines: list[str] = []
    for ev in events:
        payload: dict[str, Any] = {
            "event_id": str(ev.event_id),
            "run_id": ev.run_id,
            "seq": ev.seq,
            "step_index": ev.step_index,
            "event_type": ev.event_type,
            "attributes": dict(ev.attributes),
            "timestamp_ns": ev.timestamp_ns,
            "parent_event_id": str(ev.parent_event_id) if ev.parent_event_id is not None else None,
        }
        lines.append(json.dumps(payload, sort_keys=True))
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def _write_output(content: str, output: Path | None) -> None:
    encoded = content.encode("utf-8")
    if output is None:
        buffer = getattr(sys.stdout, "buffer", None)
        if buffer is None:
            sys.stdout.write(content)
        else:
            buffer.write(encoded)
    else:
        output.write_bytes(encoded)
