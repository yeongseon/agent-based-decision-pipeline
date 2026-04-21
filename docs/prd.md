# Product requirements (v0.1)

This document defines the minimum product boundary for v0.1 of ABDP and continues the scope set in [docs/vision.md](vision.md).

## Primary user and job

The primary user is a developer or researcher who needs a reproducible way to model and replay agent-based decisions.
Their job is to define inputs, run a simulation, and inspect stable outputs that can be compared across runs.

## Core use cases

- Create structured input data for a decision simulation.
- Run a deterministic simulation through the v0.1 core.
- Inspect outputs that can be replayed and compared for the same inputs.
- Use the resulting contracts as the acceptance boundary for later issues.

## Success criteria

- Every issue proposed for v0.1 can be accepted or rejected by checking it against this document.
- Every merged v0.1 PR satisfies the Standard v0.1 checklist.
- The tagged v0.1.0 release contains only layers 1-3 = core, data, simulation.
- Every public v0.1 contract in src/abdp/ is exercised by at least one automated test.

## v0.1 in-scope

- A minimal runnable framework boundary for layers 1-3 = core, data, simulation.
- Public contracts that let users supply inputs, execute a simulation, and observe stable outputs.
- Tests that prove the supported v0.1 behavior of those contracts.
- Documentation that states the boundary clearly enough to judge issue fit.

## v0.1 out-of-scope

- Work beyond layers 1-3.
- Layered architecture detail beyond naming layers 1-3 = core, data, simulation.
- Contributor workflow guidance.
- Product promises outside the stated v0.1 boundary.

## v0.1 milestone

The v0.1 milestone is "core skeleton".
It is complete when the tagged v0.1.0 release provides tested contracts for layers 1-3 and contains only core, data, and simulation.
