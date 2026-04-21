# Mutation testing with mutmut

`abdp` runs [mutmut](https://github.com/boxed/mutmut) as part of CI to verify
that every mutation of production code is killed by at least one test. The
authoritative mutation-testing run is the **`Mutmut`** step in
`.github/workflows/ci.yml`, which executes on Ubuntu.

## Local execution

Local runs are encouraged when iterating on a change, but the supported
platform for `mutmut run` is **Linux**. macOS developers may observe every
mutation reported as `segfault` (exit code `-11` / `-9`) due to a known
Python 3.12 + `os.fork()` interaction inside the mutmut worker pool. This is
a tooling limitation, not a defect in the code under test.

If `mutmut run` segfaults on macOS:

1. Treat Ubuntu CI as the source of truth for mutation results.
2. Verify the rest of the local quality gates manually:
   - `ruff format --check .`
   - `ruff check .`
   - `mypy --strict --config-file mypy.ini src/abdp tests`
   - `pytest`
3. Push the branch and rely on the CI **`Mutmut`** job for the
   `0 surviving mutations` guarantee before merging.

## Configuration

Mutmut configuration lives in the `[tool.mutmut]` table of `pyproject.toml`.
The `pytest_add_cli_args` entry only affects pytest invocations issued by
mutmut workers; it does not influence the regular `pytest` command used in
the local quality gates or the CI **`Pytest with coverage`** step.
