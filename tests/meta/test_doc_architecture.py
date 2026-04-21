from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE_PATH = REPO_ROOT / "docs" / "architecture.md"
TITLE = "# Layered architecture"
PRD_REFERENCE = "[docs/prd.md](prd.md)"
MAX_LINE_COUNT = 90

REQUIRED_HEADINGS: list[str] = [
    "## Layer responsibilities",
    "## Allowed dependency direction",
    "## Hard rules",
]

SECTION_ANCHORS: dict[str, list[str]] = {
    "## Layer responsibilities": [
        "Layers 1-3 = `core`, `data`, `simulation`; they are the only v0.1 implementation target.",
        "1. `core` — Stable framework contracts, shared types, and invariants with no domain-specific concepts.",
        (
            "9. `domains` — Optional domain plugins that adapt the framework to a specific field "
            "without changing the core framework."
        ),
    ],
    "## Allowed dependency direction": [
        (
            "The frozen order is `core <- data <- simulation <- agents <- scenario <- "
            "evaluation <- evidence <- reporting <- domains`."
        ),
        "An ABDP layer may import only itself and layers to its left in that order.",
        "- `abdp.core` imports no sibling layer, no `domains` package, and no domain package directly.",
        "- `domains` may import any lower layer, but no lower layer may import `domains`.",
        "Review rule: if an import points rightward in the frozen order, it is disallowed.",
    ],
    "## Hard rules": [
        '"core framework must not contain domain-specific concepts"',
        '"core must not import domain packages directly"',
        '"plugins must depend on the core contracts"',
        '"abstractions should be justified by at least two domains"',
        '"If randomness is introduced, it must be seed-aware"',
    ],
}

REQUIRED_PHRASES: list[str] = [
    "`core`",
    "`data`",
    "`simulation`",
    "`agents`",
    "`scenario`",
    "`evaluation`",
    "`evidence`",
    "`reporting`",
    "`domains`",
    "`abdp.core`",
    "at least two domains",
    "seed-aware",
]

FORBIDDEN_SNIPPETS: list[str] = [
    "real estate",
    "housing",
    "mortgage",
    "insurance",
    "retail",
    "korean",
    "south korea",
]


def _read_architecture_text() -> str:
    return ARCHITECTURE_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: list[str]) -> None:
    position = -1
    for snippet in snippets:
        next_position = text.find(snippet, position + 1)
        assert next_position != -1, f"Missing snippet: {snippet}"
        assert next_position > position, f"Snippet out of order: {snippet}"
        position = next_position


def test_architecture_file_exists() -> None:
    assert ARCHITECTURE_PATH.is_file(), f"Expected architecture doc at {ARCHITECTURE_PATH}"


def test_architecture_has_title_and_single_prd_reference() -> None:
    text = _read_architecture_text()

    assert text.startswith(f"{TITLE}\n"), f"Expected architecture doc to start with {TITLE!r}"
    assert text.count(PRD_REFERENCE) == 1, f"Expected exactly one PRD reference: {PRD_REFERENCE}"


def test_architecture_has_required_section_headings_in_order() -> None:
    text = _read_architecture_text()

    _assert_snippets_in_order(text, REQUIRED_HEADINGS)


def test_architecture_sections_include_expected_anchors() -> None:
    text = _read_architecture_text()

    for index, heading in enumerate(REQUIRED_HEADINGS):
        start = text.index(heading)
        end = len(text)
        if index + 1 < len(REQUIRED_HEADINGS):
            end = text.index(REQUIRED_HEADINGS[index + 1], start + len(heading))
        section_text = text[start:end]

        for anchor in SECTION_ANCHORS[heading]:
            assert anchor in section_text, f"Missing anchor in {heading}: {anchor}"


def test_architecture_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_architecture_text()

    for phrase in REQUIRED_PHRASES:
        assert phrase in text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_architecture_stays_within_line_budget() -> None:
    text = _read_architecture_text()

    assert len(text.splitlines()) <= MAX_LINE_COUNT, f"Architecture doc exceeds line budget of {MAX_LINE_COUNT}"
