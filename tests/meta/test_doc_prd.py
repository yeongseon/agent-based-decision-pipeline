from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRD_PATH = REPO_ROOT / "docs" / "prd.md"
TITLE = "# Product requirements (v0.1)"
VISION_REFERENCE = "[docs/vision.md](vision.md)"
MAX_LINE_COUNT = 80

REQUIRED_HEADINGS: list[str] = [
    "## Primary user and job",
    "## Core use cases",
    "## Success criteria",
    "## v0.1 in-scope",
    "## v0.1 out-of-scope",
    "## v0.1 milestone",
]

SECTION_ANCHORS: dict[str, list[str]] = {
    "## Primary user and job": [
        (
            "The primary user is a developer or researcher who needs a reproducible way to model "
            "and replay agent-based decisions."
        ),
    ],
    "## Core use cases": [
        "- Create structured input data for a decision simulation.",
    ],
    "## Success criteria": [
        "- Every merged v0.1 PR satisfies the Standard v0.1 checklist.",
    ],
    "## v0.1 in-scope": [
        "- A minimal runnable framework boundary for layers 1-3 = core, data, simulation.",
    ],
    "## v0.1 out-of-scope": [
        "- Work beyond layers 1-3.",
    ],
    "## v0.1 milestone": [
        'The v0.1 milestone is "core skeleton".',
        (
            "It is complete when the tagged v0.1.0 release provides tested contracts for layers "
            "1-3 and contains only core, data, and simulation."
        ),
    ],
}

REQUIRED_PHRASES: list[str] = [
    "core skeleton",
    "tested contracts for layers 1-3",
]

FORBIDDEN_SNIPPETS: list[str] = [
    "agents layer",
    "evaluation layer",
    "reporting layer",
    "scenario layer",
    "evidence layer",
    "domains layer",
    "pull request",
    "Conventional Commits",
]

HISTORICAL_CALLOUT_LINE = (
    "> **Historical (v0.1 baseline).** See [Roadmap](roadmap.md) for current "
    "scope and [README](../README.md) for the current shipped surface."
)


def _read_prd_text() -> str:
    return PRD_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: list[str]) -> None:
    position = -1
    for snippet in snippets:
        next_position = text.find(snippet, position + 1)
        assert next_position != -1, f"Missing snippet: {snippet}"
        assert next_position > position, f"Snippet out of order: {snippet}"
        position = next_position


def test_prd_file_exists() -> None:
    assert PRD_PATH.is_file(), f"Expected PRD file at {PRD_PATH}"


def test_prd_has_title_and_single_vision_reference() -> None:
    text = _read_prd_text()

    assert text.startswith(f"{TITLE}\n")
    assert text.count(VISION_REFERENCE) == 1


def test_prd_has_required_section_headings_in_order() -> None:
    text = _read_prd_text()

    _assert_snippets_in_order(text, REQUIRED_HEADINGS)


def test_prd_sections_include_expected_anchors() -> None:
    text = _read_prd_text()

    for index, heading in enumerate(REQUIRED_HEADINGS):
        start = text.index(heading)
        end = len(text)
        if index + 1 < len(REQUIRED_HEADINGS):
            end = text.index(REQUIRED_HEADINGS[index + 1], start + len(heading))
        section_text = text[start:end]

        for anchor in SECTION_ANCHORS[heading]:
            assert anchor in section_text, f"Missing anchor in {heading}: {anchor}"


def test_prd_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_prd_text()

    for phrase in REQUIRED_PHRASES:
        assert phrase in text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_prd_stays_within_line_budget() -> None:
    text = _read_prd_text()

    assert len(text.splitlines()) <= MAX_LINE_COUNT


def test_prd_signposts_v01_baseline_above_first_section() -> None:
    text = _read_prd_text()

    callout_index = text.find(HISTORICAL_CALLOUT_LINE)
    assert callout_index >= 0, "Historical (v0.1 baseline) callout missing"

    first_section_index = text.index(REQUIRED_HEADINGS[0])
    assert callout_index < first_section_index, "Historical callout must appear above the first '##' section heading"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in HISTORICAL_CALLOUT_LINE, snippet
