# First domain example

This example complements [docs/architecture.md](../architecture.md),
[docs/models/scenario-model.md](../models/scenario-model.md), and
[docs/plugin-system.md](../plugin-system.md) by walking one concrete domain through the v0.1
contracts. It does not add code to `src/abdp/`.

## Overview

This is the first canonical domain example for ABDP v0.1.
It shows how one credit underwriting workflow maps onto the existing contracts without extending
the framework.
The goal is contract mapping, not plugin implementation.

## Domain framing

The domain is a neutral credit underwriting workflow for one loan application.
The applicant is the focal business entity in the example, but the framework still sees only
neutral simulation contracts.
An underwriting job is one run through ordered review segments.
The example stays in credit underwriting and keeps domain meaning outside the framework.

## Mapping participants and segments

An applicant maps to `ParticipantState` via `participant_id`. In this example, the plugin gives
the applicant domain meaning such as credit profile, document status, or employment details, but
the framework contract only requires a stable participant identity.

A review stage such as intake, verification, or approval maps to `SegmentState` via `segment_id`.
`SegmentState.participant_ids` lists the participants active in that stage of the underwriting
job. The `participant_ids` tuple can include the applicant and a review service or reviewer, but
the contract stays neutral about what those roles mean.

The framework does not know why a segment exists; it only preserves stable identities and
membership. That keeps the example concrete for credit underwriting while still proving that the
core contracts do not need domain-specific fields.

## Mapping action proposals

A recommended next step maps to `ActionProposal`. In credit underwriting, that recommendation
might be "request a missing pay stub", "flag a verification mismatch", or "advance to approval",
but the framework only sees four neutral fields.

`proposal_id` identifies the recommendation, `actor_id` identifies who proposed it, and
`action_key` names the neutral action. `payload` carries domain details such as requested
documents, risk notes, or a proposed disposition.

The proposal stays a candidate action until the simulation decides what to record next. The
contract does not encode how proposals are ranked, accepted, or rejected; that policy belongs
to the plugin.

## Mapping snapshots and scenario

A case extract for the underwriting job is stored as a `SnapshotManifest` in the data layer. The
manifest captures the snapshot identity, tier, storage key, and other reproducibility fields
that the data layer already owns.

`SnapshotRef.from_manifest(SnapshotManifest)` gives simulation a lightweight pointer to that
case snapshot. Simulation does not load the snapshot contents; it only carries the
`SnapshotRef`.

A single underwriting job is represented by one `SimulationState` value with `step_index`,
`snapshot_ref`, `segments`, `participants`, and `pending_actions`. A domain `ScenarioSpec` sets
`scenario_key`, carries `seed`, and `build_initial_state()` returns the initial
`SimulationState`. The plugin owns the construction logic; the framework only enforces the
contract shape.

## Plugin packaging boundary

In real use, this example belongs in a separate plugin package.
Its domain classes live outside `src/abdp/` and outside `src/abdp/simulation/`.
The framework keeps domain concepts out of `src/abdp/`.
If credit underwriting needs extra fields, the plugin adds them without changing the core
contracts.

The boundary is not a style preference. It is the only way the v0.1 abstractions can be reused
by a different domain without forcing framework edits for each new use case.

## Comparison to the second-domain proof

This is the first domain proof for the v0.1 contracts.
Issue #046 adds a queue scheduling example as the second domain proof.
If credit underwriting and queue scheduling both fit the same contracts, the framework boundary
is earning its place.
One domain example explains the mapping; the second checks that the contracts stay
domain-neutral.
