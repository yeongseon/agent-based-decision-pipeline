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

## v0.2 modeling toolkit boundary

`v0.2` ships the modeling toolkit packages `abdp.agents` and `abdp.scenario` and proves them with two executable example domains under `examples/`. The boundary is locked by the following 14 issues:

- `#092` — `docs: pin v0.2 modeling-toolkit boundary`: lock this section so the v0.2 surface is unambiguous before implementation.
- `#093` — `feat(agents): add AgentDecision protocol`: introduce the per-step output contract for agents.
- `#094` — `feat(agents): add AgentContext dataclass`: package the per-step input passed into `Agent.decide`.
- `#095` — `feat(agents): add Agent protocol and package exports`: finalize the `abdp.agents` public surface.
- `#096` — `feat(scenario): add ActionResolver protocol`: declare how proposals turn into the next state.
- `#097` — `feat(scenario): add ScenarioStep dataclass`: capture one runner iteration.
- `#098` — `feat(scenario): add ScenarioRun dataclass`: capture the full execution trace.
- `#099` — `feat(scenario): add ScenarioRunner execution loop`: implement the deterministic runner.
- `#100` — `test(scenario): lock runner determinism and step invariants`: pin the runner contract with invariant tests.
- `#101` — `feat(examples): add executable credit underwriting sample`: prove the toolkit on the credit underwriting domain.
- `#102` — `chore(examples): promote queue scheduling fixture into example module`: relocate the second-domain fixture.
- `#103` — `feat(examples): add executable queue scheduling sample`: prove the toolkit on the queue scheduling domain.
- `#104` — `docs: add 10-minute modeling quickstart`: walk a new contributor from zero to a runnable scenario. See [quickstart.md](quickstart.md).
- `#105` — `test(agents): freeze agents and scenario public surfaces`: lock both new package namespaces.

## Explicit non-goals for v0.2

- No evaluation symbols, gates, or summaries belong in `v0.2`; that work is reserved for `v0.3`.
- No evidence records, claims, audit logs, or stores belong in `v0.2`; that work is reserved for `v0.3`.
- No CLI entry point, run command, or report command belongs in `v0.2`; that work is reserved for `v0.3`.
- No persistence backends or storage adapters belong in `v0.2`; the in-memory toolkit must remain sufficient.
- No domain-specific code belongs under `src/abdp/**`; domain logic lives only in `examples/` and tests.

## v0.3 milestone themes

- `v0.3` may broaden implementations around agents, evaluation, evidence, and reporting once `v0.2` proves the boundaries.
- `v0.3` may refine cross-layer composition instead of introducing parallel stacks or competing abstractions.
- `v0.3` may improve comparison, audit, and reporting workflows that build on earlier contract work.
- `v0.3` is still a roadmap milestone, not a calendar promise.

## v0.3 milestone scope

The `v0.3` milestone delivers the auditable simulation surface across `abdp.evaluation`, `abdp.evidence`, `abdp.reporting`, and `abdp.cli`, plus end-to-end audit-flow proofs in both example domains. It is locked by the following 20 issues:

- `#106` — `docs: define v0.3 auditable simulation boundary`: lock the v0.3 scope, reserved keys, and non-goals.
- `#107` — `test(evaluation): freeze evaluation public surface`: lock the `abdp.evaluation` package namespace.
- `#108` — `feat(evaluation): add metric protocol and result record`: introduce the metric contract.
- `#109` — `feat(evaluation): add ordered metric evaluation helper`: deterministic metric application.
- `#110` — `feat(evaluation): add gate protocol and result record`: introduce the gate contract.
- `#111` — `feat(evaluation): add gate evaluation and summary aggregation`: combine metric and gate outcomes.
- `#112` — `test(evidence): freeze evidence public surface`: lock the `abdp.evidence` package namespace.
- `#113` — `feat(evidence): add EvidenceRecord`: minimal evidence row contract.
- `#114` — `feat(evidence): add ClaimRecord`: claim row referencing evidence rows.
- `#115` — `feat(evidence): add AuditLog bundle`: deterministic audit-log container.
- `#116` — `feat(evidence): add EvidenceStore protocol`: abstract storage contract.
- `#117` — `feat(evidence): add in-memory evidence store`: reference implementation.
- `#118` — `test(reporting): freeze reporting public surface`: lock the `abdp.reporting` package namespace.
- `#119` — `feat(reporting): add deterministic JSON renderer`: machine-readable report output.
- `#120` — `feat(reporting): add deterministic Markdown renderer`: human-readable report output.
- `#121` — `feat(cli): add CLI entrypoint and import-path loader`: shared `abdp.cli` command surface.
- `#122` — `feat(cli): add CLI run command`: execute scenarios from the terminal.
- `#123` — `feat(cli): add CLI report command`: render audit logs from the terminal.
- `#124` — `test(examples): prove credit underwriting audit flow`: end-to-end evidence and report assertion in the credit underwriting example.
- `#125` — `test(examples): prove queue scheduling audit flow`: end-to-end evidence and report assertion in the queue scheduling example.

Reserved evidence keys: `evidence_key="selected_proposal"` is the mandatory key recording which proposal a resolver applied at each step; all v0.3 audit flows must emit it and all v0.3 reporting renderers must surface it.

## Explicit non-goals for v0.3

- No remote storage, network adapters, or hosted services belong in `v0.3`; the in-memory evidence store remains the reference.
- No plugin system, dynamic discovery, or external entry-point registration belongs in `v0.3`; CLI loaders use explicit import paths only.
- No web UI, dashboard, browser viewer, or HTML output belongs in `v0.3`; reporting stays JSON and Markdown.
- No domain-specific code belongs under `src/abdp/**` in `v0.3`; example audit flows live only in `examples/` and `tests/`.

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
