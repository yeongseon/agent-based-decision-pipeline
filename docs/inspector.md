# Inspector

The Inspector is abdp's in-process tracing layer. It captures *how* a scenario
ran — every step boundary and every agent decision — without touching the
canonical evidence/audit plane that downstream evaluation depends on.

This guide covers the surface introduced in v0.4: `abdp.inspector` for
in-process recording and `abdp inspect` for offline querying. It is the
substrate the upcoming Self-Correction / ReviewLoopRunner (v0.5) builds on.

## Two-plane execution model

abdp keeps two independent record planes side by side:

| Plane | What it stores | Public types |
| --- | --- | --- |
| **Canonical** | Committed scenario history: `ScenarioRun`, `SimulationState`, `EvidenceRecord`, `ClaimRecord`, `AuditLog`. Used by reporting, evaluation, audit. | `abdp.scenario`, `abdp.evidence`, `abdp.simulation` (unchanged) |
| **Inspector** | Deterministic per-run trace events: `step.begin`, `decision.evaluate`, `step.end`, and any future review-attempt events. Never feeds back into evidence. | `abdp.inspector` |

The canonical plane is the source of truth for evaluation. The Inspector plane
is purely observational: enabling or disabling it never changes evidence,
audit content, or determinism of the canonical pipeline.

For the design rationale and the alternatives that were rejected, see
[ADR 0001 — Two-plane execution model for Inspector and ReviewLoopRunner](adr/0001-two-plane-execution-model.md).

## TraceEvent

A `TraceEvent` is one entry in the Inspector plane:

```python
from abdp.inspector import TraceEvent
```

| Field | Type | Notes |
| --- | --- | --- |
| `event_id` | `UUID` | Derived from `(seed, run_id, seq)` via a private namespace; only those three influence identity. |
| `run_id` | `str` | Caller-chosen identifier for one ScenarioRunner invocation. |
| `seq` | `int` | Monotonic per run (`0, 1, 2, …`), assigned by `TraceRecorder`. |
| `step_index` | `int` | The canonical scenario step the event belongs to. |
| `event_type` | `str` | `step.begin`, `step.end`, `decision.evaluate`, … (extension namespace open). |
| `attributes` | `Mapping[str, str \| int \| float \| bool]` | OTel-style attribute bag; primitive values only. |
| `timestamp_ns` | `int` | Equal to `seq`; deterministic, never wall-clock derived. |
| `parent_event_id` | `UUID \| None` | Span parenting hook for nested events (e.g. review attempts). |

`make_trace_event(...)` is the factory used by `TraceRecorder`; identity is
fixed by the `(seed, run_id, seq)` triple, so two runs of the same scenario
produce byte-identical event IDs.

## TraceStore

`TraceStore` is a `Protocol` with two ready-made implementations:

| Implementation | Use it for |
| --- | --- |
| `MemoryTraceStore` | Tests and ephemeral in-process inspection. |
| `SQLiteTraceStore(path)` | Persisted traces; default backend for the CLI. |

Both expose:

- `append(event) -> None`
- `query(*, run_id, step_index=None, event_type=None) -> Iterator[TraceEvent]`
- `event(event_id) -> TraceEvent | None`
- `runs() -> Iterator[str]`
- `close() -> None` (idempotent)

Filter keys outside of `step_index` / `event_type` are rejected by
`validate_query_filters` to keep the Protocol contract narrow and forward
compatible.

## Recording from a scenario

`TraceRecorder` owns the `seq` counter for one run and writes into any
`TraceStore`. Inject it into `ScenarioRunner` and the runner emits
`step.begin`, `decision.evaluate` (per agent), and `step.end` events for
every step automatically:

```python
from abdp.core import Seed
from abdp.inspector import SQLiteTraceStore, TraceRecorder
from abdp.scenario import ScenarioRunner

store = SQLiteTraceStore("traces.db")
recorder = TraceRecorder(store=store, seed=Seed(7), run_id="nightly-2026-04-24")
runner = ScenarioRunner(
    agents=(my_agent,),
    resolver=my_resolver,
    max_steps=10,
    recorder=recorder,
)
runner.run(spec)
store.close()
```

`recorder` defaults to `None`; the runner is fully backward compatible —
omit it and no Inspector code path runs.

## Querying with `abdp inspect`

```bash
abdp inspect <run_id> --db PATH [--step N] [--event-type TYPE] [--output FILE]
```

The subcommand opens the SQLite trace database, queries the matching events
for the given `run_id`, and writes one JSON object per line (JSON Lines)
ordered by `seq`:

```json
{"attributes": {"scenario_key": "demo"}, "event_id": "…", "event_type": "step.begin", "parent_event_id": null, "run_id": "nightly-2026-04-24", "seq": 0, "step_index": 0, "timestamp_ns": 0}
{"attributes": {"agent_id": "agent-a", "proposals": 1}, "event_id": "…", "event_type": "decision.evaluate", "parent_event_id": null, "run_id": "nightly-2026-04-24", "seq": 1, "step_index": 0, "timestamp_ns": 1}
…
```

- `--step N` keeps only events whose `step_index` equals `N` (must be
  non-negative).
- `--event-type TYPE` keeps only events whose `event_type` equals `TYPE`.
- `--output FILE` writes the JSON Lines to `FILE` instead of stdout. The
  bytes written to a file are byte-identical to what stdout would produce
  for the same query.
- An unknown `run_id` is not an error: the command exits `0` with no
  output.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Query completed (zero or more events emitted). |
| `2` | Database missing, corrupt, or output path unwritable; argparse rejection (missing required flag, malformed `--step`). |

## Determinism

Two runs with the same `(seed, scenario_key, run_id)` produce byte-identical
trace event tuples. Specifically:

- `event_id` is a deterministic UUID over `(seed, run_id, seq)`.
- `seq` is assigned monotonically by `TraceRecorder`.
- `timestamp_ns` equals `seq` — the Inspector never reads a wall clock.
- `attributes` use only primitive Python types and serialize with sorted
  keys when persisted, so SQLite round-trips preserve byte-equality.

This is the property that lets the upcoming ReviewLoopRunner record
critique attempts on the Inspector plane without ever destabilizing the
canonical evidence stream.

## Non-goals

- HTTP / RPC tracing (no HTTP surface in abdp v0.3).
- OTLP export (forward-compatible attribute names only; no OTel SDK
  dependency).
- Distributed / cross-process spans.
- Web UI or dashboard.
- Persisting full `SimulationState` in trace events; use `SnapshotRef`
  pointers instead.
