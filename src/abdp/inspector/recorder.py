"""``TraceRecorder`` helper that writes :class:`TraceEvent`s into a :class:`TraceStore`.

The recorder owns the monotonic ``seq`` counter and timestamp derivation
for one run, so callers (notably :class:`abdp.scenario.ScenarioRunner`)
only need to describe *what* happened.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from uuid import UUID

from abdp.core.types import Seed
from abdp.inspector.event import TraceAttributeValue, TraceEvent, make_trace_event
from abdp.inspector.store import TraceStore

__all__ = ["TraceRecorder"]


@dataclass
class TraceRecorder:
    store: TraceStore
    seed: Seed
    run_id: str
    _next_seq: int = field(default=0, init=False, repr=False)

    def record(
        self,
        *,
        event_type: str,
        step_index: int,
        attributes: Mapping[str, TraceAttributeValue],
        parent_event_id: UUID | None = None,
    ) -> TraceEvent:
        seq = self._next_seq
        self._next_seq += 1
        ev = make_trace_event(
            seed=self.seed,
            run_id=self.run_id,
            seq=seq,
            step_index=step_index,
            event_type=event_type,
            attributes=dict(attributes),
            timestamp_ns=seq,
            parent_event_id=parent_event_id,
        )
        self.store.append(ev)
        return ev
