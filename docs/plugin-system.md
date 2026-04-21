# Plugin system

This document defines the package boundary for domain plugins in ABDP v0.1 and aligns
with [docs/architecture.md](architecture.md),
[docs/repository-structure.md](repository-structure.md), and
[docs/models/domain-model.md](models/domain-model.md).

## Package boundary

- Domain plugins are separate Python packages, not code added under `src/abdp/`.
- In v0.1, domain plugins MUST NOT be added under `src/abdp/`, including `src/abdp/domains/`.
- `src/abdp/` stays reserved for framework code, and domain code stays in plugin repositories.
- A plugin maps domain objects onto `abdp.core` primitives without changing the core framework.
- If only one domain needs a concept, keep it in the plugin instead of adding it to `abdp.core`.

## Compatibility and versioning

- Compatibility is defined against documented abdp contracts, not a plugin loader implementation.
- A plugin should declare the ABDP version range it supports in its own package metadata.
- v0.1 does not promise compatibility for internal modules, unpublished APIs, or future loader behavior.
- If an abdp contract changes incompatibly, the plugin should release an updated compatible version.

## Allowed dependencies

- A domain plugin may depend on released `abdp` packages such as `abdp.core`, `abdp.data`, and `abdp.simulation`.
- A domain plugin may also depend on its own domain packages and third-party libraries it needs.
- A domain plugin must not depend on ABDP docs, tests, or repository-only import paths.
- Lower ABDP layers must not import a domain plugin or any domain package directly.
- If a plugin introduces randomness, it must stay seed-aware.
