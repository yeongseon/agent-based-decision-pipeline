"""Deterministic JSON renderer for :class:`abdp.evidence.AuditLog`.

``render_json_report`` walks an :class:`~abdp.evidence.AuditLog` (or any
JSON-serializable abdp value) and emits a stable, sorted-key JSON string.

Determinism rules:

* keys are sorted; tuples become lists; UUIDs become canonical strings.
* ``datetime`` values must be timezone-aware UTC; naive or offset-aware
  non-UTC datetimes are rejected.
* dict keys must be ``str``; non-string keys are rejected.
* non-finite floats (``NaN``/``Infinity``) are rejected.
* values typed as the simulation generic protocols (``ActionProposal``,
  ``SegmentState``, ``ParticipantState``, ``AgentDecision``) are projected
  to their protocol attributes only; extra dataclass fields are dropped.
"""

import dataclasses
import json
import math
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import UUID

from abdp.agents.decision import AgentDecision
from abdp.simulation.action_proposal import ActionProposal
from abdp.simulation.participant_state import ParticipantState
from abdp.simulation.segment_state import SegmentState

__all__ = ["render_json_report"]


def render_json_report(value: Any, *, indent: int = 2) -> str:
    """Render ``value`` to a deterministic JSON string."""
    payload = _to_jsonable(value)
    return json.dumps(
        payload,
        indent=indent,
        sort_keys=True,
        separators=(",", ": "),
        ensure_ascii=False,
        allow_nan=False,
    )


def _to_jsonable(value: Any) -> Any:
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
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return _serialize_mapping(value)
    for proto, attrs in _PROTOCOL_PROJECTIONS:
        if isinstance(value, proto):
            return {attr: _to_jsonable(getattr(value, attr)) for attr in attrs}
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _serialize_dataclass(value)
    raise TypeError(f"cannot serialize value of type {type(value).__name__}")


def _serialize_datetime(value: datetime) -> str:
    tz = value.tzinfo
    if tz is None or tz.utcoffset(value) != timedelta(0):
        raise ValueError("datetime must be timezone-aware UTC")
    return value.isoformat()


def _serialize_mapping(value: dict[Any, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in value.items():
        if not isinstance(k, str):
            raise TypeError(f"dict key must be str, got {type(k).__name__}")
        out[k] = _to_jsonable(v)
    return out


def _serialize_dataclass(value: Any) -> dict[str, Any]:
    return {f.name: _to_jsonable(getattr(value, f.name)) for f in dataclasses.fields(value)}


_PROTOCOL_PROJECTIONS: tuple[tuple[type, tuple[str, ...]], ...] = (
    (ActionProposal, ("proposal_id", "actor_id", "action_key", "payload")),
    (AgentDecision, ("agent_id", "proposals")),
    (SegmentState, ("segment_id", "participant_ids")),
    (ParticipantState, ("participant_id",)),
)
