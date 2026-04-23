# CLI

The `abdp` console script ships three subcommands for running scenarios,
rendering audit reports, and inspecting captured traces from the command
line. The CLI surface is a thin, deterministic wrapper around the same
building blocks shown in the
[10-minute modeling quickstart](quickstart.md); it does not introduce new
domain primitives.

## Install

```bash
uv sync
```

Inside the project virtual environment, invoke the CLI either through `uv`
or directly through Python:

```bash
uv run abdp --help
python -m abdp --help
```

Both forms reach the same entry point; the rest of this guide writes
commands as `abdp …` for brevity, but every example is equivalent to
`uv run abdp …` or `python -m abdp …` from a checkout.

## Commands

| Command | Purpose |
| --- | --- |
| `abdp run` | Build an `AuditLog` from a scenario factory and render it to JSON. |
| `abdp report` | Reload a serialized `AuditLog` and re-render it as JSON or Markdown. |
| `abdp inspect` | Query a SQLite trace store and emit JSON Lines (see [Inspector](inspector.md)). |

`abdp` with no arguments (or `--help`) prints the parser help and exits `0`.

## Running a scenario

```bash
abdp run <module.path:callable> --seed N [--output FILE]
```

`<module.path:callable>` is a strict `module.path:callable` spec resolved by
`abdp.cli.loader`. The named attribute must be a callable that accepts a
`Seed` and returns an `abdp.evidence.AuditLog`.

- `--seed` is required and must be a non-negative `uint32` integer.
- `--output FILE` writes the rendered JSON report to `FILE` (UTF-8 bytes);
  omit it to stream the JSON to stdout.
- A `WARN` overall status still exits `0`, but a single
  `warning: audit completed with WARN status` line is written to stderr.

The JSON written here is the same artifact `abdp report` consumes; persist it
if you intend to re-render later.

## Rendering a report

```bash
abdp report <path> --format {json,markdown} [--output FILE]
```

`<path>` is a JSON file previously produced by `abdp run` (or by
`abdp.reporting.render_json_report`). The reconstructed `AuditLog` is
re-rendered:

- `--format json` emits byte-identical JSON to the original render.
- `--format markdown` emits the Markdown report.
- `--output FILE` writes the rendered bytes to `FILE`; omit it to stream to
  stdout.

`abdp report` always exits `0` on a successful render regardless of the
audit's overall status; loader, parse, or shape errors exit `2` with a
single-line stderr message.

## Exit codes

| Command | Code | Meaning |
| --- | --- | --- |
| `abdp run` | `0` | Scenario produced an `AuditLog` with overall status `PASS` or `WARN`. |
| `abdp run` | `1` | Scenario produced an `AuditLog` with overall status `FAIL`. |
| `abdp run` | `2` | Loader could not resolve the spec or the factory did not return an `AuditLog`. |
| `abdp report` | `0` | Audit log reloaded and re-rendered successfully. |
| `abdp report` | `2` | Audit log could not be read, parsed, or reconstructed. |
| `abdp inspect` | `0` | Trace query completed (zero or more events emitted). |
| `abdp inspect` | `2` | Trace database missing/corrupt, output unwritable, or argparse rejection. |

`WARN` does not change the exit code; it only emits the stderr notice noted
under [Running a scenario](#running-a-scenario).

## Reproducibility notes

- `--seed` is the only knob the CLI itself controls; it validates the value
  and forwards it to the factory resolved from `<module.path:callable>`.
- Reproducible output therefore depends on the factory being seed-driven and
  deterministic — that is, on the factory using only the supplied `Seed` to
  build the `AuditLog`. Given such a factory, the same `(spec, --seed)` pair
  produces the same `AuditLog` on every run.
- Seeds are validated as non-negative `uint32` integers; out-of-range values
  exit at the parser, before any factory runs.
- `abdp report --format json` rebuilds the in-memory `AuditLog` and re-renders
  it; the result is byte-identical to the JSON originally produced by
  `abdp run --output ...`. This is what makes round-tripping safe in CI.

## CLI vs programmatic API

Use the CLI when you want a reproducible, scriptable entry point: a single
`abdp run …` invocation pinned to a seed, suitable for cron jobs, CI
pipelines, or shell-driven evaluation matrices.

Use the programmatic API when you are still designing the scenario or want
direct access to the in-memory `ScenarioRun`. The
[10-minute modeling quickstart](quickstart.md) walks through `abdp.agents`,
`abdp.scenario`, and `ScenarioRunner`; once the factory you build there
returns an `AuditLog`, point `abdp run` at it.
