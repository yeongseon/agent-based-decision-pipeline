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

## Known equivalent mutants

Some mutations produce code that is behaviorally identical to the original
and therefore cannot be killed by any test. These are tracked here so they
are not re-investigated on every CI run. Equivalent-mutant survivors do not
count against the `0 surviving mutations` quality gate; they are exceptions
documented per mutant ID with the exact mutation diff and the equivalence
rationale.

### `abdp.core.hashing`

- `abdp.core.hashing.x__canonical_json_bytes__mutmut_4`:
  `ensure_ascii=False` -> `ensure_ascii=None`. `json.dumps` interprets the
  flag via truthiness, and `None` is falsy, so the canonical output is
  byte-identical to the original.
- `abdp.core.hashing.x__canonical_json_bytes__mutmut_6`:
  `allow_nan=False` -> `allow_nan=None`. Same rationale as above; `None` is
  falsy and `json.dumps` raises on non-finite floats in both cases, so the
  canonical output is byte-identical.

If a future change makes either flag observable (for example, by switching
to a JSON encoder that distinguishes `None` from `False`), revisit these
entries instead of treating them as permanent exceptions.
