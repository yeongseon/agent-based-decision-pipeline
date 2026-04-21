# Contributing

This guide is intentionally short; detailed expansion is deferred to #044.

## Small issues only

- One issue -> one focused pull request.
- If work spans unrelated concerns or cannot be finished in one RED -> GREEN -> REFACTOR cycle, split it first.

## Commit prefixes

- Use Conventional Commits prefixes: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `ci`, `build`, `perf`.

## Oracle gate

- See `AGENTS.md` for the Oracle-first workflow and TDD strict: RED -> GREEN -> REFACTOR.
- Before merge, satisfy the Standard v0.1 checklist:
  - Oracle 100/100 before merge
  - all tests pass
  - mypy strict clean
  - ruff clean
  - 100% line coverage on new code
