# Agent model

This document defines the future layer 4 `agents` boundary for ABDP without adding `abdp.agents` code in
v0.1. It extends the scenario boundary in [docs/models/scenario-model.md](scenario-model.md) and applies
the layer rules from [docs/architecture.md](../architecture.md); concrete provider connectors and runtime
composition stay out of scope.

## Scope and layer boundary

- An agent observes `SimulationState`, decides under a policy boundary, and emits `ActionProposal` values.
- The agent layer owns proposal generation, not state mutation or scenario assembly.
- Domain plugins may supply their own agents without changing `abdp.simulation`.
- Concrete model providers, prompt wiring, and transport adapters stay outside this model.

## Observation, decision, and action lifecycle

- Observation reads the current `SimulationState` as input and does not mutate it.
- Decision applies a rule-based, model-based, or hybrid policy behind the agent boundary.
- Action emission returns zero or more `ActionProposal` values for the current step.
- Simulation consumes emitted proposals later; the agent does not record an `action` or write a `snapshot` directly.

## Agent contract boundary

- The minimal agent boundary is observe current state, decide, and propose next actions.
- An agent contract may depend on `SimulationState` and return `ActionProposal` values only.
- The boundary does not include provider clients, prompt formats, tool registries, or persistence APIs.
- Agents stay pluggable per domain because domain meaning lives in the plugin, not in the framework contract.

## Relationship to ActionProposal and ScenarioSpec

- Every emitted proposal must satisfy `ActionProposal` with `proposal_id`, `actor_id`, `action_key`, and `payload`.
- `payload` stays a `JsonValue`, so agent outputs remain domain-neutral at the framework boundary.
- `ScenarioSpec` remains responsible for `scenario_key`, `seed`, and `build_initial_state()` before observation begins.
- Agents consume the seeded initial state and may surface proposals via `pending_actions` in `SimulationState`.
