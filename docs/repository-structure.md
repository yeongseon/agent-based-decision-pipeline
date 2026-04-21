# Repository structure

This guide fixes the repository layout for ABDP.
[docs/architecture.md](architecture.md) is the authority for layer names;
`docs/naming.md` and `docs/prd.md` stay authoritative for naming rules and the v0.1 scope boundary.

## Current top-level tree

```text
.github/workflows/ci.yml
AGENTS.md
CONTRIBUTING.md
LICENSE
README.md
docs/
  README.md
  adr/
  architecture.md
  development/
  examples/
  models/
  naming.md
  prd.md
  vision.md
mypy.ini
pyproject.toml
pytest.ini
src/
  abdp/
    __init__.py
    core/
    data/
    py.typed
    simulation/
    version.py
tests/
  meta/
  unit/
```

## Placement rules

- `src/abdp/` holds framework source code, with layer packages such as `abdp.core`, `abdp.data`, and `abdp.simulation`.
- New layer code follows `src/abdp/<layer>/`, and layer names come from the architecture document.
- `tests/meta/` holds repository and documentation contract tests.
- `tests/unit/` holds unit tests for code under `src/abdp/`.
- `docs/` holds framework documentation only and does not hold executable framework code.

## Reserved domains layer

- `abdp.domains` stays reserved as the framework layer name.
- Real domain plugins ship as separate Python packages, not under `src/abdp/domains/`.
- Example domain plugins follow the same rule and stay outside the `src/abdp/` tree.
- Do not add domain-specific package names anywhere under `src/abdp/`.
