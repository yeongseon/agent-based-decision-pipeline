# Roadmap

This roadmap keeps `v0.1` focused on layers 1-3 contracts and points contributors to the shipped boundary references in [docs/architecture.md](architecture.md), [docs/models/agent-model.md](models/agent-model.md), [docs/evaluation.md](evaluation.md), and [docs/evidence-reporting.md](evidence-reporting.md). It is milestone-oriented only: calendar dates and detailed release engineering stay out of scope unless a maintainer chooses to add them later.

## Scope and non-goals overview

- This roadmap is milestone-oriented rather than date-oriented.
- `v0.1` is the contract baseline for `core`, `data`, and `simulation`.
- `v0.2` and `v0.3` describe expansion themes, not calendar promises.
- Detailed release engineering and maintainer scheduling are intentionally excluded here.

## v0.1 milestone

- `v0.1` keeps implementation scope on layers 1-3 contracts: `core`, `data`, and `simulation`.
- The agent, evaluation, and evidence/reporting boundary docs stay documentation-first in `v0.1`.
- `v0.1` does not implement `abdp.agents`, `abdp.evaluation`, `abdp.evidence`, or `abdp.reporting`.
- `v0.1` does not add domain code, provider integrations, or complex infrastructure.
- `v0.1` does not promise calendar dates.

## v0.2 milestone themes

- `v0.2` should prove one thin end-to-end path on top of the frozen contracts before widening the framework surface.
- `v0.2` should add contributor guidance and examples that make the current contracts easier to use.
- `v0.2` should test new shared abstractions against at least two domains before promoting them into the framework.
- `v0.2` should keep seeded reproducibility, stable contracts, and simple storage assumptions intact.

## v0.3 milestone themes

- `v0.3` may broaden implementations around agents, evaluation, evidence, and reporting once `v0.2` proves the boundaries.
- `v0.3` may refine cross-layer composition instead of introducing parallel stacks or competing abstractions.
- `v0.3` may improve comparison, audit, and reporting workflows that build on earlier contract work.
- `v0.3` is still a roadmap milestone, not a calendar promise.

## Explicit non-goals for v0.1

- No implementation work beyond layers 1-3 belongs in `v0.1`; that includes layers 4, 6, 7, and 8.
- No domain-specific framework code belongs in `v0.1`; shared abstractions still need evidence from at least two domains.
- No provider-specific clients, orchestration services, or release automation belong in `v0.1`.
- No calendar dates, release promises, or detailed release engineering belong in `v0.1`.
- No complex infrastructure belongs in `v0.1` while the file-and-test workflow remains sufficient.

## Revisit triggers for more complex infrastructure

- Revisit more complex infrastructure when the same pain appears across at least two domains or contributor workflows.
- Revisit it when layer 4, 6, 7, or 8 implementations create repeated manual steps that simple tests and docs cannot police.
- Revisit it when seeded local workflows stop being enough to validate reproducibility, evidence links, or reporting outputs.
- Revisit it only after the simpler contract-and-tests path is clearly failing for current work.
