from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = REPO_ROOT / "docs" / "adr" / "0000-template.md"

MAX_TEMPLATE_LINES = 20

EXPECTED_TITLE = "# 0000 - ADR template"
EXPECTED_TEMPLATE_NOTE = "Template only. Copy this file to a new numbered ADR and replace every placeholder before use."

EXPECTED_SECTION_HEADINGS = (
    "## Status",
    "## Context",
    "## Decision",
    "## Consequences",
)

EXPECTED_PLACEHOLDER_SNIPPETS = (
    "TBD",
    "<describe the problem, constraints, and forces>",
    "<describe the chosen option>",
    "<describe expected benefits, trade-offs, and follow-up work>",
)

FORBIDDEN_REPO_SPECIFIC_SNIPPETS = (
    "agent-based-decision-pipeline",
    "abdp",
)


def test_adr_template_file_exists() -> None:
    assert TEMPLATE_PATH.is_file()


def test_adr_template_file_declares_expected_sections_and_stays_short() -> None:
    assert TEMPLATE_PATH.is_file(), TEMPLATE_PATH
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert EXPECTED_TITLE in template_text
    assert EXPECTED_TEMPLATE_NOTE in template_text

    start = 0
    for snippet in EXPECTED_SECTION_HEADINGS:
        index = template_text.find(snippet, start)
        assert index >= 0, snippet
        start = index + len(snippet)

    assert len(template_text.splitlines()) < MAX_TEMPLATE_LINES


def test_adr_template_file_is_generic_and_contains_only_placeholder_content() -> None:
    assert TEMPLATE_PATH.is_file(), TEMPLATE_PATH
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")

    start = 0
    for snippet in EXPECTED_PLACEHOLDER_SNIPPETS:
        index = template_text.find(snippet, start)
        assert index >= 0, snippet
        start = index + len(snippet)

    lowered_template_text = template_text.lower()
    for snippet in FORBIDDEN_REPO_SPECIFIC_SNIPPETS:
        assert snippet not in lowered_template_text
