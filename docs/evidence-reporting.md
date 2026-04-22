# Evidence and reporting

This document defines the future layer 7 `evidence` and layer 8 `reporting` boundaries for ABDP
without adding `abdp.evidence` or `abdp.reporting` code in `v0.1`. It extends
[docs/models/agent-model.md](models/agent-model.md),
[docs/models/scenario-model.md](models/scenario-model.md), and
[docs/evaluation.md](evaluation.md), and applies the layer rules from
[docs/architecture.md](architecture.md); implementation remains `post-v0.1`, and this is a
schema-vs-implementation contract rather than an implementation plan.

## Scope and layer boundary

- `abdp.evidence` is the layer 7 boundary for execution traces, observations, and supporting artifacts.
- `abdp.reporting` is the layer 8 boundary for presentation-ready `markdown` and `JSON` outputs.
- The schema-vs-implementation boundary is explicit: no abdp.evidence or abdp.reporting code lands in v0.1.
- Evidence and reporting consume `metrics`, `gate` outcomes, and frozen run outputs without mutating `SimulationState`.

## EvidenceRecord, ClaimRecord, and GateResult concepts

- `EvidenceRecord` is the canonical schema record for a single observed fact, artifact, or linkage to stored data.
- `ClaimRecord` is the canonical schema record for a derived statement that cites one or more `EvidenceRecord` values.
- `GateResult` is the canonical schema record for a `gate` judgment tied to `metrics`, thresholds, and status.
- Records may carry `Seed`, `JsonValue`, and `stable_hash` values to preserve deterministic joins across runs.
- Records may refer to `SimulationState`, `ActionProposal`, `ScenarioSpec`, `SnapshotManifest`, and `SnapshotRef` identities.

## Evidence store expectations

- An `evidence store` preserves immutable records plus references to `bronze`, `silver`, and `gold` artifacts.
- Store entries may point at `SnapshotManifest` or `SnapshotRef` metadata rather than copying large payloads inline.
- Store keys should be stable across reruns when `Seed`, scenario identity, and canonical `JsonValue` content match.
- The store contract is schema-oriented: field names, identifiers, and relations are in scope; file layouts are not.

## Markdown and JSON reporting expectations

- `abdp.reporting` should render the same underlying records into human-readable `markdown` and machine-readable `JSON`.
- Reports should summarize `metrics`, `GateResult`, and cited `ClaimRecord` or `EvidenceRecord` entries without new logic.
- A report may group by scenario, segment, participant, or run when those identities already exist in `SimulationState`.
- Reporting may include links back to `ActionProposal` and `SnapshotManifest` records so derived summaries stay auditable.

## SQL DDL note

- A future `SQL DDL` may declare schema objects for `EvidenceRecord`, `ClaimRecord`, and `GateResult`.
- This note is schema-level only: required columns, keys, and relations are in scope, but migrations and storage engines are not.
- Real SQL migrations, concrete database setup, and `abdp.evidence` or `abdp.reporting` implementation stay `post-v0.1`.
