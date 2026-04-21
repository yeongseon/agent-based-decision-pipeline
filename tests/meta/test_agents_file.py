from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"

EXPECTED_TITLE = "# AGENTS"

EXPECTED_SECTION_HEADINGS = (
    "## Oracle-first workflow",
    "## Engineering rules",
    "## Standard v0.1 checklist",
)

EXPECTED_ORACLE_CONSULT_RULE = "Oracle consult before implementation is required."
EXPECTED_TDD_RULE = "TDD strict: RED -> GREEN -> REFACTOR."
EXPECTED_COMMIT_RULE = (
    "Use three separate commits for RED, GREEN, and REFACTOR, and each commit message must reference the issue number."
)
EXPECTED_ORACLE_MERGE_RULE = "Oracle 100/100 before merge is required."
EXPECTED_ISSUE_SIZING_RULE = (
    "Size each issue so it fits one focused pull request; if it spans unrelated concerns "
    "or cannot be finished in one RED -> GREEN -> REFACTOR cycle, split it first."
)
EXPECTED_DOCSTRING_RULE = (
    "Write meaningful docstrings for public Python modules, classes, and functions, and "
    "preserve intentionally empty package docstrings where the repo tests require them."
)
EXPECTED_NO_ANY_RULE = "No `Any` without justification."
EXPECTED_NO_TYPE_IGNORE_RULE = "No `# type: ignore`."

EXPECTED_RULE_SNIPPETS = (
    EXPECTED_ORACLE_CONSULT_RULE,
    EXPECTED_TDD_RULE,
    EXPECTED_COMMIT_RULE,
    EXPECTED_ORACLE_MERGE_RULE,
    EXPECTED_ISSUE_SIZING_RULE,
    EXPECTED_DOCSTRING_RULE,
    EXPECTED_NO_ANY_RULE,
    EXPECTED_NO_TYPE_IGNORE_RULE,
)

EXPECTED_STANDARD_CHECKLIST = (
    "- Oracle 100/100 before merge",
    "- all tests pass",
    "- mypy strict clean",
    "- ruff clean",
    "- 100% line coverage on new code",
)


def _read_agents_text() -> str:
    assert AGENTS_PATH.is_file(), AGENTS_PATH
    return AGENTS_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: tuple[str, ...]) -> None:
    start = 0
    for snippet in snippets:
        index = text.find(snippet, start)
        assert index >= 0, snippet
        start = index + len(snippet)


def test_agents_file_exists() -> None:
    assert AGENTS_PATH.is_file()


def test_agents_file_declares_required_sections() -> None:
    agents_text = _read_agents_text()

    assert EXPECTED_TITLE in agents_text
    _assert_snippets_in_order(agents_text, EXPECTED_SECTION_HEADINGS)


def test_agents_file_declares_oracle_first_rules_and_repo_constraints() -> None:
    agents_text = _read_agents_text()

    _assert_snippets_in_order(agents_text, EXPECTED_RULE_SNIPPETS)


def test_agents_file_declares_standard_v0_1_checklist() -> None:
    agents_text = _read_agents_text()

    _assert_snippets_in_order(agents_text, EXPECTED_STANDARD_CHECKLIST)
