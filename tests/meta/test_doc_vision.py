from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VISION_PATH = REPO_ROOT / "docs" / "vision.md"

TAGLINE = "A Python framework for reproducible agent-based decision simulation"

SECTION_HEADINGS: tuple[str, ...] = (
    "## Problem statement",
    "## Target users",
    "## Non-goals",
    "## v0.1 promise",
)

SECTION_SNIPPETS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "## Problem statement",
        (
            "study or compare decision strategies",
            "assumptions, inputs, randomness, and outputs can be reproduced and reviewed.",
        ),
    ),
    (
        "## Target users",
        (
            "researchers, analysts, and product or policy teams",
            "rerun the same experiment with controlled randomness",
        ),
    ),
    (
        "## Non-goals",
        (
            "Not a real-time simulation engine for live operational systems.",
            "Not a domain library with built-in business, policy, scientific, or game rules.",
            "Not an autonomous decision-making service that replaces human accountability.",
        ),
    ),
    (
        "## v0.1 promise",
        (
            "public API can stay aligned with that scope.",
            "The v0.1 checklist is simple:",
            "This document sets scope, not implementation commitments beyond v0.1.",
        ),
    ),
)

FORBIDDEN_SNIPPETS: tuple[str, ...] = (
    "core/data/simulation/agents/scenario/evaluation/evidence/reporting/domains",
    "9 architectural layers",
    "milestone sequencing",
    "v0.2",
    "v1.0",
)

MAX_VISION_LINES = 60


def _read_vision_text() -> str:
    assert VISION_PATH.is_file(), VISION_PATH
    return VISION_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: tuple[str, ...]) -> None:
    start = 0
    for snippet in snippets:
        index = text.find(snippet, start)
        assert index >= 0, snippet
        start = index + len(snippet)


def test_vision_file_exists() -> None:
    assert VISION_PATH.is_file()


def test_vision_includes_tagline_and_required_sections_in_order() -> None:
    text = _read_vision_text()

    assert TAGLINE in text
    _assert_snippets_in_order(text, SECTION_HEADINGS)


def test_each_section_contains_expected_snippets() -> None:
    text = _read_vision_text()

    for index, (heading, snippets) in enumerate(SECTION_SNIPPETS):
        section_start = text.index(heading)
        if index + 1 < len(SECTION_SNIPPETS):
            next_heading = SECTION_SNIPPETS[index + 1][0]
            section_end = text.index(next_heading, section_start + len(heading))
        else:
            section_end = len(text)

        section_text = text[section_start:section_end]
        for snippet in snippets:
            assert snippet in section_text, f"{heading}: {snippet}"


def test_vision_avoids_forbidden_scope_and_stays_within_line_budget() -> None:
    text = _read_vision_text()

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, snippet

    assert len(text.splitlines()) <= MAX_VISION_LINES
