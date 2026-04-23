# agent-based-decision-pipeline

A Python framework for reproducible agent-based decision simulation

## Roadmap

See [Roadmap](docs/roadmap.md) for milestone scope, including the v0.2 modeling toolkit boundary and v0.3 themes.

## Quickstart

New here? Start with the [10-minute modeling quickstart](docs/quickstart.md).

## Used by

- [`kpubdata-lab/younggeul`](https://github.com/kpubdata-lab/younggeul) — Korean apartment market simulation. Adopts `abdp.core.stable_hash`, `abdp.data` contract aliases, `abdp.reporting.render_json_report`, and shadow `abdp.simulation.ScenarioRunner` + `abdp.evidence.AuditLog` projection on top of LangGraph. See younggeul's [ADR-012 final selective-adoption inventory](https://github.com/kpubdata-lab/younggeul/blob/main/docs/adr/012-abdp-backed-core.md#final-selective-adoption-inventory) for the per-surface adoption breakdown.

If your project uses `abdp`, open a PR adding it here.
