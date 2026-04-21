from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRIBUTING_PATH = REPO_ROOT / "CONTRIBUTING.md"

MAX_GUIDE_LINES = 50

EXPECTED_TITLE = "# Contributing"
EXPECTED_SHORT_GUIDE_NOTE = "This guide is intentionally short; detailed expansion is deferred to #044."

EXPECTED_SECTION_HEADINGS = (
    "## Small issues only",
    "## Commit prefixes",
    "## Oracle gate",
)

EXPECTED_SMALL_ISSUE_POLICY = "One issue -> one focused pull request."
EXPECTED_SMALL_ISSUE_SPLIT_RULE = (
    "If work spans unrelated concerns or cannot be finished in one RED -> GREEN -> REFACTOR cycle, split it first."
)

EXPECTED_COMMIT_PREFIX_RULE = (
    "Use Conventional Commits prefixes: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `ci`, `build`, `perf`."
)

EXPECTED_ORACLE_GUIDE_POINTER = (
    "See `AGENTS.md` for the Oracle-first workflow and TDD strict: RED -> GREEN -> REFACTOR."
)
EXPECTED_STANDARD_CHECKLIST_INTRO = "Before merge, satisfy the Standard v0.1 checklist:"
EXPECTED_STANDARD_CHECKLIST = (
    "- Oracle 100/100 before merge",
    "- all tests pass",
    "- mypy strict clean",
    "- ruff clean",
    "- 100% line coverage on new code",
)


def test_contributing_file_exists() -> None:
    assert CONTRIBUTING_PATH.is_file()


def test_contributing_file_declares_expected_sections_and_stays_short() -> None:
    assert CONTRIBUTING_PATH.is_file(), CONTRIBUTING_PATH
    contributing_text = CONTRIBUTING_PATH.read_text(encoding="utf-8")

    assert EXPECTED_TITLE in contributing_text
    assert EXPECTED_SHORT_GUIDE_NOTE in contributing_text

    start = 0
    for snippet in EXPECTED_SECTION_HEADINGS:
        index = contributing_text.find(snippet, start)
        assert index >= 0, snippet
        start = index + len(snippet)

    assert len(contributing_text.splitlines()) < MAX_GUIDE_LINES


def test_contributing_file_declares_small_issue_policy_and_commit_prefixes() -> None:
    assert CONTRIBUTING_PATH.is_file(), CONTRIBUTING_PATH
    contributing_text = CONTRIBUTING_PATH.read_text(encoding="utf-8")

    snippets = (
        EXPECTED_SMALL_ISSUE_POLICY,
        EXPECTED_SMALL_ISSUE_SPLIT_RULE,
        EXPECTED_COMMIT_PREFIX_RULE,
    )
    start = 0
    for snippet in snippets:
        index = contributing_text.find(snippet, start)
        assert index >= 0, snippet
        start = index + len(snippet)


def test_contributing_file_declares_oracle_gate_and_standard_v0_1_checklist() -> None:
    assert CONTRIBUTING_PATH.is_file(), CONTRIBUTING_PATH
    contributing_text = CONTRIBUTING_PATH.read_text(encoding="utf-8")

    snippets = (
        EXPECTED_ORACLE_GUIDE_POINTER,
        EXPECTED_STANDARD_CHECKLIST_INTRO,
        *EXPECTED_STANDARD_CHECKLIST,
    )
    start = 0
    for snippet in snippets:
        index = contributing_text.find(snippet, start)
        assert index >= 0, snippet
        start = index + len(snippet)
