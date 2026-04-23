# agent-based-decision-pipeline

A Python framework for reproducible agent-based decision simulation

## What it is

abdp is a Python framework for reproducible agent-based decision simulation. It defines the contracts an experiment needs — agents, scenarios, evaluation, evidence, and reporting — so the same simulation can be rerun, inspected, and compared instead of rebuilt as a one-off script.

The framework intentionally keeps a narrow shipped surface. Domain rules, integrations, hosted services, and dashboards are explicitly out of scope; see [non-goals](docs/vision.md#non-goals) for the full list.

## Why it exists

Teams that study or compare decision strategies often rebuild one-off simulations that are hard to rerun, inspect, and compare. abdp exists to be the shared substrate for those experiments so assumptions, inputs, randomness, and outputs can be reproduced and reviewed by someone other than the original author. See the [vision](docs/vision.md) for the problem statement and target users.

## Getting started

Install from source:

```bash
pip install -e .
```

Then walk the [10-minute modeling quickstart](docs/quickstart.md). It introduces `abdp.agents`, `abdp.scenario`, and the deterministic `ScenarioRunner` by building a single self-contained reproducible scenario top-to-bottom.

## Roadmap

See [Roadmap](docs/roadmap.md) for milestone scope, the v0.2 modeling toolkit boundary, the v0.3 auditable simulation surface, and the explicit non-goals attached to each milestone.

## Used by

- [`kpubdata-lab/younggeul`](https://github.com/kpubdata-lab/younggeul) — Korean apartment market simulation. Adopts `abdp.core.stable_hash`, `abdp.data` contract aliases, `abdp.reporting.render_json_report`, and shadow `abdp.simulation.ScenarioRunner` + `abdp.evidence.AuditLog` projection on top of LangGraph. See younggeul's [ADR-012 final selective-adoption inventory](https://github.com/kpubdata-lab/younggeul/blob/main/docs/adr/012-abdp-backed-core.md#final-selective-adoption-inventory) for the per-surface adoption breakdown.

If your project uses `abdp`, open a PR adding it here.
