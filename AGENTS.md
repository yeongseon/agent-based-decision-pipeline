# AGENTS

## Oracle-first workflow

1. Oracle consult before implementation is required.
2. TDD strict: RED -> GREEN -> REFACTOR.
3. Use three separate commits for RED, GREEN, and REFACTOR, and each commit message must reference the issue number.
4. Oracle 100/100 before merge is required.

## Engineering rules

- Size each issue so it fits one focused pull request; if it spans unrelated concerns or cannot be finished in one RED -> GREEN -> REFACTOR cycle, split it first.
- Write meaningful docstrings for public Python modules, classes, and functions, and preserve intentionally empty package docstrings where the repo tests require them.
- No `Any` without justification.
- No `# type: ignore`.

## Standard v0.1 checklist

- Oracle 100/100 before merge
- all tests pass
- mypy strict clean
- ruff clean
- 100% line coverage on new code
