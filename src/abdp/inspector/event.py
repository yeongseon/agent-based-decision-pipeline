"""``TraceEvent`` frozen dataclass and ``make_trace_event`` factory exposed by ``abdp.inspector``.

A ``TraceEvent`` is one entry in the inspector/tracing plane. Identity is
derived deterministically from ``(seed, run_id, seq)`` via a private
namespace UUID so the same event captured under the same seed always
shares an ``event_id``. ``step_index``, ``event_type``, ``attributes``,
``timestamp_ns``, and ``parent_event_id`` are payload metadata and do
not influence identity.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final
from uuid import UUID

from abdp.core.ids import deterministic_uuid
from abdp.core.types import Seed

__all__ = ["TraceAttributeValue", "TraceEvent", "make_trace_event"]

_TRACE_NAMESPACE: Final = UUID("3a8c7e6d-1f24-4e7b-9c08-7c8a2f5b6d10")
_NAME_SEPARATOR: Final = "\0"

TraceAttributeValue = str | int | float | bool


@dataclass(frozen=True, slots=True)
class TraceEvent:
    """One entry in the inspector/tracing plane."""

    event_id: UUID
    run_id: str
    seq: int
    step_index: int
    event_type: str
    attributes: Mapping[str, TraceAttributeValue]
    timestamp_ns: int
    parent_event_id: UUID | None

    def __post_init__(self) -> None:
        if not self.run_id:
            raise ValueError("run_id must be a non-empty string")
        if not self.event_type:
            raise ValueError("event_type must be a non-empty string")
        if self.seq < 0:
            raise ValueError("seq must be non-negative")
        if self.step_index < 0:
            raise ValueError("step_index must be non-negative")
        if self.timestamp_ns < 0:
            raise ValueError("timestamp_ns must be non-negative")
        if not isinstance(self.attributes, Mapping):
            raise TypeError(
                f"attributes must be a Mapping[str, TraceAttributeValue], got {type(self.attributes).__name__}"
            )
        frozen: dict[str, TraceAttributeValue] = {}
        for key, value in self.attributes.items():
            if not isinstance(key, str):
                raise TypeError(f"attribute key must be str, got {type(key).__name__}")
            if not isinstance(value, str | int | float | bool):
                raise TypeError(
                    f"attribute value for {key!r} must be str|int|float|bool, " f"got {type(value).__name__}"
                )
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError(f"attribute value for {key!r} must be a finite float, got {value!r}")
            frozen[key] = value
        object.__setattr__(self, "attributes", MappingProxyType(frozen))


def make_trace_event(
    *,
    seed: Seed,
    run_id: str,
    seq: int,
    step_index: int,
    event_type: str,
    attributes: Mapping[str, TraceAttributeValue],
    timestamp_ns: int,
    parent_event_id: UUID | None,
) -> TraceEvent:
    """Build a :class:`TraceEvent` with a deterministically derived ``event_id``.

    ``event_id`` is derived from ``seed``, the private trace namespace,
    and ``f"{run_id}\\0{seq}"``; all other arguments are payload metadata
    and do not influence identity.
    """
    name = f"{run_id}{_NAME_SEPARATOR}{seq}"
    event_id = deterministic_uuid(seed, _TRACE_NAMESPACE, name)
    return TraceEvent(
        event_id=event_id,
        run_id=run_id,
        seq=seq,
        step_index=step_index,
        event_type=event_type,
        attributes=attributes,
        timestamp_ns=timestamp_ns,
        parent_event_id=parent_event_id,
    )
