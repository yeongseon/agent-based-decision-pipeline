# Evaluation

This document defines the future layer 6 `evaluation` boundary for ABDP without adding `abdp.evaluation`
code in `v0.1`. It extends [docs/models/agent-model.md](models/agent-model.md) and
[docs/models/scenario-model.md](models/scenario-model.md) and applies the layer rules from
[docs/architecture.md](architecture.md); implementation remains `post-v0.1` work, and evidence or
reporting schema detail stay out of scope.

## Scope and layer boundary

- `abdp.evaluation` is the layer 6 boundary for post-run `metrics`, `gate` evaluation, and `aggregation`.
- In `v0.1`, evaluation is documented only; `post-v0.1` work may implement code against frozen contracts.
- Evaluation reads simulation and data outputs after execution and does not mutate `abdp.simulation` state.
- Evidence collection and reporting formats stay outside this document.

## Metrics and gate evaluation

- Evaluation computes `metrics` from deterministic run outputs rather than inventing new domain-specific score names.
- A `gate` is a rule that interprets one or more metric results against documented thresholds or predicates.
- Gate evaluation may yield pass, fail, or similar neutral judgments without changing the recorded run artifacts.
- Metric and gate definitions stay domain-neutral in the framework; domain meaning belongs in plugins.

## Result aggregation

- `aggregation` combines metric results and gate outcomes into a run-level or comparison-level summary.
- Aggregation may group by scenario, segment, participant, or repeated run set when those identities already exist.
- Aggregation records derived outcomes, not new simulation actions, and does not replace evidence or reporting.
- If multiple runs are compared, aggregation should preserve which scenario identity and `Seed` produced each result.

## Inputs consumed from simulation and data outputs

- Evaluation may consume `SimulationState` outputs such as `step_index`, `segments`, `participants`, and `pending_actions`.
- Evaluation may inspect emitted `ActionProposal` values, including `proposal_id`, `actor_id`, `action_key`, and `payload`.
- Evaluation may read `SnapshotManifest`, `SnapshotRef`, and tiered `bronze`, `silver`, and `gold` outputs from `abdp.data`.
- Shared inputs may include `ScenarioSpec` metadata such as `scenario_key`, plus `Seed`, `JsonValue`, and `stable_hash` values used to join records.
