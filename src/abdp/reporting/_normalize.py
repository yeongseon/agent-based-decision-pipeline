"""Shared deterministic value normalization for ``abdp.reporting``.

Both :func:`abdp.reporting.render_json_report` and
:func:`abdp.reporting.render_markdown_report` consume :func:`to_jsonable`
so JSON-serializable abdp values are normalized through one set of
invariants:

* primitives, ``StrEnum`` (via ``.value``), ``UUID`` (canonical string),
  and timezone-aware UTC ``datetime`` (ISO 8601);
* tuples and lists become lists; dicts require ``str`` keys;
* non-finite floats are rejected;
* values typed as the simulation generic protocols
  (``ActionProposal``/``SegmentState``/``ParticipantState``/``AgentDecision``)
  are projected to their protocol attributes only;
* dataclasses are projected by ``dataclasses.fields`` order;
* cyclic inputs raise a deterministic ``ValueError`` instead of
  ``RecursionError``.
"""

import dataclasses
import math
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import UUID

from abdp.agents.decision import AgentDecision
from abdp.simulation.action_proposal import ActionProposal
from abdp.simulation.participant_state import ParticipantState
from abdp.simulation.segment_state import SegmentState

__all__ = ["CycleGuard", "to_jsonable"]


class CycleGuard:
    """Tracks visited container ids on the active descent path."""

    __slots__ = ("_active",)

    def __init__(self) -> None:
        self._active: set[int] = set()

    def enter(self, value: Any) -> None:
        oid = id(value)
        if oid in self._active:
            raise ValueError(f"cyclic reference detected while serializing {type(value).__name__}")
        self._active.add(oid)

    def leave(self, value: Any) -> None:
        self._active.discard(id(value))


def to_jsonable(value: Any, guard: CycleGuard | None = None) -> Any:
    """Normalize ``value`` to a JSON-compatible Python value."""
    return _to_jsonable(value, guard if guard is not None else CycleGuard())


def _to_jsonable(value: Any, guard: CycleGuard) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite float values are not JSON-serializable: {value!r}")
        return value
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, str):
        return value
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return _serialize_datetime(value)
    if isinstance(value, (tuple, list)):
        guard.enter(value)
        try:
            return [_to_jsonable(item, guard) for item in value]
        finally:
            guard.leave(value)
    if isinstance(value, dict):
        guard.enter(value)
        try:
            return _serialize_mapping(value, guard)
        finally:
            guard.leave(value)
    for proto, attrs in _PROTOCOL_PROJECTIONS:
        if isinstance(value, proto):
            guard.enter(value)
            try:
                return {attr: _to_jsonable(getattr(value, attr), guard) for attr in attrs}
            finally:
                guard.leave(value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        guard.enter(value)
        try:
            return {f.name: _to_jsonable(getattr(value, f.name), guard) for f in dataclasses.fields(value)}
        finally:
            guard.leave(value)
    raise TypeError(f"cannot serialize value of type {type(value).__name__}")


def _serialize_datetime(value: datetime) -> str:
    tz = value.tzinfo
    if tz is None or tz.utcoffset(value) != timedelta(0):
        raise ValueError("datetime must be timezone-aware UTC")
    return value.isoformat()


def _serialize_mapping(value: dict[Any, Any], guard: CycleGuard) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in value.items():
        if not isinstance(k, str):
            raise TypeError(f"dict key must be str, got {type(k).__name__}")
        out[k] = _to_jsonable(v, guard)
    return out


_PROTOCOL_PROJECTIONS: tuple[tuple[type, tuple[str, ...]], ...] = (
    (ActionProposal, ("proposal_id", "actor_id", "action_key", "payload")),
    (AgentDecision, ("agent_id", "proposals")),
    (SegmentState, ("segment_id", "participant_ids")),
    (ParticipantState, ("participant_id",)),
)
