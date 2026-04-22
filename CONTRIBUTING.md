# Contributing

## Overview

- This guide is the operating manual for day-to-day contribution work in
  this repository.
- Use it together with [AGENTS.md](AGENTS.md) for the Oracle-first
  baseline.
- The file-and-test workflow is: pick one issue, add the failing test,
  make the smallest change that passes, verify locally, and open one
  focused PR.
- Keep changes domain-neutral, small, and easy to review.
- Prefer explicit acceptance criteria over implied follow-up work.
- If a change needs broader design discussion, pause and get the Oracle
  consult before you code.

## Issue intake and sizing

- one issue -> one focused pull request.
- do not bundle concepts into one PR.
- If a task spans unrelated concerns or cannot fit in one RED -> GREEN ->
  REFACTOR cycle, split it before coding.
- Prefer the smallest slice that proves one behavior, one rule, or one
  document expansion.
- If cleanup is real but not required for the current acceptance
  criteria, file a follow-up issue instead.
- A good issue description names the target files, the failing or
  missing test, and the exact acceptance gate.
- If the review story takes more than a few paragraphs to explain, the
  slice is probably too large.

## Branch and commit conventions

- Create branches as `<type>/<NNN>-<slug>`.
- Use these type prefixes: feat, fix, docs, test, refactor, chore, ci,
  build, perf.
- Use Conventional Commits for commit subjects.
- Every commit message references the issue number as `(#NN)`.
- Keep RED, GREEN, and REFACTOR as separate commits when each phase
  exists.
- REFACTOR is optional when the GREEN change is already clean enough to
  merge.
- Do not squash local history into one commit before review; the PR
  should show the TDD trail.
- Keep commit messages descriptive enough that reviewers can map them
  back to the issue and the test progression.

## TDD workflow

- TDD is strict: RED -> GREEN -> REFACTOR.
- RED means write or update the smallest failing test first.
- GREEN means make the test pass with the smallest possible
  implementation change.
- REFACTOR means improve names, structure, or duplication without
  changing behavior.
- For documentation work, start with a meta test that fails on the
  missing guidance, then expand the document until the test passes.
- If you cannot explain the failing test before the implementation, the
  slice is probably too large.
- Keep the failing test and the passing change close in time; do not
  stockpile uncommitted work across multiple concepts.
- When REFACTOR is unnecessary, say so in the PR instead of inventing a
  third commit.

## Oracle consult and review

- Request an Oracle consult before implementation when the change
  affects design, contributor workflow, contracts, or scoring
  expectations.
- Bring the issue link, the planned slice, the target files, the
  intended tests, and the main trade-offs to the consult.
- Use the consult to confirm scope, acceptance criteria, and whether
  the issue should be split again.
- Request Oracle review again before merge after local verification is
  green.
- oracle review score = 100/100.
- The oracle scoring rubric is Correctness 30, Test quality 25, API
  design 20, Documentation 10, Type strictness 10, and
  Conventions/process 5.
- A review below 100/100 is not merge-ready; fix the gaps and re-run
  review.
- If the review identifies bundling, split the work instead of arguing
  the scope.

## Local verification and CI gate

- Run the full local gate from the repository root before opening or
  updating a PR.
- Formatting and linting use ruff format strict with line-length 120.
- Run these commands exactly:

```bash
ruff format .
ruff check .
mypy --strict src tests
pytest --cov
```

- Use the verification block in the PR to record each command and the
  result.
- 100% line coverage on new code is required.
- CI gate means the protected main branch must be green before merge.
- Do not use `--no-verify` to bypass hooks or checks.
- Run `mutmut run` when the change needs mutation evidence.
- For pure docs or protocol-only changes, state `N/A` for mutmut in the
  PR.
- On macOS, local mutmut can hit `SIGSEGV` in `os.fork()`; Ubuntu CI is
  authoritative for that result.

## Docstring and type rules

- Write meaningful docstrings for public Python modules, classes, and
  functions.
- Preserve intentionally empty package docstrings where repository
  tests require them.
- No `Any` without justification.
- No `# type: ignore`; use `typing.cast` when narrowing is required.
- Use PEP 695 syntax such as `type Alias = ...`, `def fn[T](...)`, and
  `class Box[T: Bound]`.
- Prefer `@runtime_checkable` Protocol contracts with an anchored
  module docstring.
- For protocol tests, cover structural acceptance, missing-method
  negatives, `_is_protocol`, and the identity-only contract guard.
- Keep contributor-facing examples framework-neutral and domain-neutral.
- If a new abstraction is proposed, justify it with more than one
  concrete use case.

## Pull request structure

- Open the PR only after the local gate is green and the branch is
  ready for focused review.
- The PR body should use this structure:
  - `Closes #N`
  - `Summary`
  - `TDD evidence` with the RED commit and GREEN commit, plus REFACTOR
    when used
  - `Verification` with commands and results
  - `Mutmut policy` with either results or `N/A`
  - optional `Acceptance criteria checklist`
- State clearly when a change is docs-only, protocol-only, or
  intentionally omits a REFACTOR commit.
- Do not bundle concepts, follow-up refactors, and unrelated cleanup
  into the same PR.
- PRs are squash-merged after review, and the merge flow deletes the
  branch with `--delete-branch`.
- Branch protection requires CI green before the squash merge
  completes.
- If the issue acceptance criteria list exact wording, commands, or
  files, copy that evidence into the PR instead of summarizing loosely.
