# Layered architecture

This document defines the frozen layer model for ABDP and continues the v0.1 boundary set in [docs/prd.md](prd.md).

## Layer responsibilities

Layers 1-3 = `core`, `data`, `simulation`; they are the only v0.1 implementation target.

1. `core` — Stable framework contracts, shared types, and invariants with no domain-specific concepts.
2. `data` — Structured inputs, outputs, repositories, and serialization that move data into and out of simulations.
3. `simulation` — Deterministic execution flow, runtime control, and orchestration for running a simulation.
4. `agents` — Agent contracts and behavior composition used inside a simulation run.
5. `scenario` — Scenario assembly that binds agents, inputs, and conditions into a runnable case.
6. `evaluation` — Metrics and judgments applied to simulation results.
7. `evidence` — Traces, observations, and supporting artifacts collected from execution and evaluation.
8. `reporting` — Presentation-ready summaries and exports derived from evidence and evaluation.
9. `domains` — Optional domain plugins that adapt the framework to a specific field without changing the core framework.

## Allowed dependency direction

The frozen order is `core <- data <- simulation <- agents <- scenario <- evaluation <- evidence <- reporting <- domains`.
An ABDP layer may import only itself and layers to its left in that order.

- `abdp.core` imports no sibling layer, no `domains` package, and no domain package directly.
- `abdp.core` public types and contracts must stay free of domain-specific concepts.
- `data` may import only `core`.
- `simulation` may import only `data` and `core`.
- `agents` may import only `simulation`, `data`, and `core`.
- `scenario` may import only `agents`, `simulation`, `data`, and `core`.
- `evaluation` may import only `scenario`, `agents`, `simulation`, `data`, and `core`.
- `evidence` may import only `evaluation`, `scenario`, `agents`, `simulation`, `data`, and `core`.
- `reporting` may import only `evidence`, `evaluation`, `scenario`, `agents`, `simulation`, `data`, and `core`.
- `domains` may import any lower layer, but no lower layer may import `domains`.

Review rule: if an import points rightward in the frozen order, it is disallowed.

## Hard rules

- "core framework must not contain domain-specific concepts"
- "core must not import domain packages directly"
- "plugins must depend on the core contracts"
- "abstractions should be justified by at least two domains"
- "If randomness is introduced, it must be seed-aware"
