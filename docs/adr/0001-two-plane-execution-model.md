# 0001 - Two-plane execution model for Inspector and ReviewLoopRunner

## Status

Accepted (2026-04-24, issue #172). Companion to issue #173 (ReviewLoopRunner).

## Context

abdp v0.3 ships a single-plane execution model: `ScenarioRunner` advances a
`SimulationState`, agents emit proposals, the resolver commits them, and the
canonical evidence/audit pipeline stores the result. There is no
observability hook and no place to record the *process* by which a step was
produced — only the committed outcome.

Two upcoming features need a place to record process-level information:

1. **Inspector / Tracing (#172)** — capture per-step decision evaluations,
   timings, and (in the future) tool calls.
2. **Self-Correction / ReviewLoopRunner (#173)** — wrap each step in a
   propose / critique / revise loop, retaining the rejected attempts as
   reviewable history while still committing only the accepted attempt to
   the canonical evidence store.

The constraint that frames the design: the canonical plane (`ScenarioRun`,
`SimulationState`, `EvidenceRecord`, `ClaimRecord`, `AuditLog`) must stay
byte-identical for the same `(seed, scenario)` whether or not Inspector and
review are enabled. Existing public types must not change shape.

Three alternatives were considered for how to model rejected review
attempts:

- **A. Branchable Seed.** Derive a per-attempt sub-seed and treat each
  attempt as an independent execution branch. Rejected by Oracle: this
  promotes attempts to a first-class execution dimension and forces the
  canonical pipeline to learn about branching just to ignore it. Wrong
  abstraction.
- **B. `evidence_key#attemptN` namespace.** Store all attempts (including
  rejected ones) in the canonical evidence store under suffixed keys. Rejected:
  this pollutes the canonical domain namespace with values that are never
  read by reporting or evaluation, and breaks the invariant that an
  evidence key identifies one accepted observation.
- **C. Tuple `step_index = (n, attempt_no)`.** Overload the logical step
  counter to carry attempt identity. Rejected: `step_index` is an integer
  in every public surface; widening it would either break those surfaces
  or require a parallel "logical step" field that re-introduces the
  problem.

## Decision

Adopt a **two-plane execution model**.

- **Canonical plane (unchanged).** `ScenarioRun.steps[i]` is the single
  accepted outcome of step `i`. `SimulationState.step_index: int` keeps its
  v0.3 meaning. `EvidenceRecord` and `ClaimRecord` only ever record the
  accepted attempt. No public types change.
- **Inspector plane (new, in `abdp.inspector`).** A separate, deterministic
  per-run event stream captured by `TraceRecorder` and persisted by any
  `TraceStore`. Event identity is derived from `(seed, run_id, seq)`, so
  two runs of the same scenario produce byte-identical trace IDs.
- **ReviewLoopRunner uses the Inspector plane** for rejected attempts.
  Rejected attempts are recorded as `review.attempt` events with their own
  `seq` and `parent_event_id`, and never enter the canonical evidence
  store. Only the first accepted attempt commits to the canonical plane.

Concretely this means:

```text
canonical:  step 0 (accepted) ── step 1 (accepted) ── step 2 (accepted) ─→ AuditLog
inspector:  step.begin, decision.evaluate, review.attempt(rejected)*, step.end, …
            ────────────────────────────────────────────────────────────→ TraceStore
```

The Inspector plane is observational only: feature-gating it on or off
never changes the canonical bytes.

## Consequences

**Benefits**

- Public surfaces (`ScenarioRun`, `SimulationState`, `EvidenceRecord`,
  `ClaimRecord`, `AuditLog`) keep their v0.3 shapes; existing tests, docs,
  and downstream code keep working unchanged.
- Determinism proof for ReviewLoopRunner reduces to "only the first accepted
  attempt commits to canonical", which is local to one helper function.
- Inspector can ship and stabilize independently of ReviewLoopRunner; v0.4
  delivers a usable tracing surface even if v0.5 slips.
- Future work (OTLP export, additional event types, alternative stores) can
  extend the Inspector plane without touching canonical code.

**Trade-offs**

- Two planes means two query surfaces. Operators inspecting a run consult
  evidence/audit for *what* happened and the Inspector for *how*. The
  `abdp inspect` CLI exists to make the Inspector plane queryable.
- `ScenarioRunner` grows an optional `recorder: TraceRecorder | None`
  field. The default `None` preserves byte-identical behaviour for
  existing callers.
- Rejected review attempts are never persisted to evidence; teams that
  want them in the canonical plane must build a deliberate adapter on
  top of the Inspector store.

**Follow-up**

- `abdp.review` (issue #173) will introduce `review.attempt` events,
  `parent_event_id` chaining, and an explicit "accepted" attribute on the
  committing attempt.
- A future issue may add an OTLP exporter that translates `TraceEvent`
  records into OTel spans for external collectors.
