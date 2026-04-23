"""``TraceStore`` protocol and ``MemoryTraceStore`` reference implementation.

Mirrors the ``EvidenceStore`` pattern: a minimal pluggable persistence
contract for inspector :class:`TraceEvent` records, with an in-memory
reference implementation backed by insertion-ordered dicts. SQLite-backed
persistence lives in :mod:`abdp.inspector.sqlite_store`.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any, Protocol, runtime_checkable
from uuid import UUID

from abdp.inspector.event import TraceEvent

__all__ = ["MemoryTraceStore", "TraceStore", "validate_query_filters"]

_QUERY_FILTERS = frozenset({"step_index", "event_type"})


def validate_query_filters(filters: dict[str, Any]) -> None:
    unknown = set(filters) - _QUERY_FILTERS
    if unknown:
        joined = ", ".join(sorted(unknown))
        raise TypeError(f"unknown query filter(s): {joined}")


@runtime_checkable
class TraceStore(Protocol):
    def append(self, event: TraceEvent) -> None: ...  # pragma: no cover

    def query(self, *, run_id: str, **filters: Any) -> Iterable[TraceEvent]: ...  # pragma: no cover

    def event(self, event_id: UUID) -> TraceEvent | None: ...  # pragma: no cover

    def runs(self) -> Iterable[str]: ...  # pragma: no cover

    def close(self) -> None: ...  # pragma: no cover


class MemoryTraceStore:
    def __init__(self) -> None:
        self._events: dict[UUID, TraceEvent] = {}

    def append(self, event: TraceEvent) -> None:
        if not isinstance(event, TraceEvent):
            raise TypeError(f"expected TraceEvent, got {type(event).__name__}")
        if event.event_id in self._events:
            raise ValueError(f"duplicate event_id: {event.event_id}")
        self._events[event.event_id] = event

    def query(self, *, run_id: str, **filters: Any) -> Iterator[TraceEvent]:
        validate_query_filters(filters)
        step_index = filters.get("step_index")
        event_type = filters.get("event_type")
        for ev in self._events.values():
            if ev.run_id != run_id:
                continue
            if step_index is not None and ev.step_index != step_index:
                continue
            if event_type is not None and ev.event_type != event_type:
                continue
            yield ev

    def event(self, event_id: UUID) -> TraceEvent | None:
        return self._events.get(event_id)

    def runs(self) -> Iterator[str]:
        seen: set[str] = set()
        for ev in self._events.values():
            if ev.run_id not in seen:
                seen.add(ev.run_id)
                yield ev.run_id

    def close(self) -> None:
        return None
