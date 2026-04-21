# Plugin system

This document defines how a domain plugin extends the framework, separately from any
plugin loader implementation. It complements [docs/architecture.md](architecture.md) and
[docs/repository-structure.md](repository-structure.md), and refines the package boundary
described in [docs/models/domain-model.md](models/domain-model.md).

## Package boundary

- Domain plugins ship as separate Python packages from the framework.
- In v0.1, plugin code MUST NOT live under `src/abdp/`, including `src/abdp/domains/`.
- `src/abdp/` stays reserved for framework code only.
- A plugin maps its concepts onto `abdp.core` primitives.
- Single-domain code stays inside the plugin and does not leak into framework layers.

## Compatibility and versioning

- Plugins are defined against abdp contracts, not against the loader implementation.
- Each plugin declares an ABDP version range it supports.
- v0.1 makes no promise about internal-module stability across minor versions.
- An incompatible change requires the plugin to release a compatible version.

## Allowed dependencies

- Plugins may depend on `abdp.core`, `abdp.data`, and `abdp.simulation`.
- Plugins may depend on their own packages and on third-party libraries.
- Plugins MUST NOT depend on docs, tests, or repository paths of the framework.
- Lower framework layers MUST NOT import plugins or plugin repositories.
- Randomness used inside a plugin stays seed-aware.
