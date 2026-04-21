from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NAMING_PATH = REPO_ROOT / "docs" / "naming.md"
TITLE = "# Naming conventions"
ARCHITECTURE_REFERENCE = "[docs/architecture.md](architecture.md)"
MAX_LINE_COUNT = 70

REQUIRED_HEADINGS: list[str] = [
    "## Package and module names",
    "## Public symbol names",
    "## Issue, PR, and commit names",
]

SECTION_ANCHORS: dict[str, list[str]] = {
    "## Package and module names": [
        (
            "The root package is `abdp`, and layer packages follow `abdp.<layer>` with layers "
            "taken from the architecture document."
        ),
        "Modules under `abdp.<layer>` use lowercase `snake_case` names.",
        "`abdp.core` names stay framework-generic and must not encode a domain concept.",
    ],
    "## Public symbol names": [
        "Classes use `PascalCase`.",
        "Functions and methods use `snake_case`.",
        "Constants use `UPPER_SNAKE_CASE`.",
        "Type aliases use `PascalCase`.",
    ],
    "## Issue, PR, and commit names": [
        ("Issue titles and PR titles use lowercase commit-style prefixes that stay Conventional Commits-compatible."),
        "Commit subjects use Conventional Commits with lowercase types only.",
        "Allowed types: `docs:`, `test:`, `refactor:`, `feat:`, `fix:`, `chore:`, `ci:`, `build:`.",
        "Branch names follow `<type>/<NNN>-<kebab-slug>`.",
    ],
}

REQUIRED_PHRASES: list[str] = [
    "`abdp.<layer>`",
    "`snake_case`",
    "`PascalCase`",
    "`UPPER_SNAKE_CASE`",
    "`<type>/<NNN>-<kebab-slug>`",
    "Conventional Commits",
    "`docs:`",
    "`test:`",
    "`refactor:`",
    "`feat:`",
    "`fix:`",
    "`chore:`",
    "`ci:`",
    "`build:`",
]

FORBIDDEN_SNIPPETS: list[str] = [
    "RealEstateAgent",
    "HousingScorer",
    "real estate",
    "mortgage",
    "Korean",
    "Docs:",
    "Feat:",
]


def _read_naming_text() -> str:
    return NAMING_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: list[str]) -> None:
    position = -1
    for snippet in snippets:
        next_position = text.find(snippet, position + 1)
        assert next_position != -1, f"Missing snippet: {snippet}"
        assert next_position > position, f"Snippet out of order: {snippet}"
        position = next_position


def test_naming_file_exists() -> None:
    assert NAMING_PATH.is_file(), f"Expected naming doc at {NAMING_PATH}"


def test_naming_has_title_and_single_architecture_reference() -> None:
    text = _read_naming_text()

    assert text.startswith(f"{TITLE}\n"), f"Expected naming doc to start with {TITLE!r}"
    assert text.count(ARCHITECTURE_REFERENCE) == 1, (
        f"Expected exactly one architecture reference: {ARCHITECTURE_REFERENCE}"
    )


def test_naming_has_required_section_headings_in_order() -> None:
    text = _read_naming_text()

    _assert_snippets_in_order(text, REQUIRED_HEADINGS)


def test_naming_sections_include_expected_anchors() -> None:
    text = _read_naming_text()

    for index, heading in enumerate(REQUIRED_HEADINGS):
        start = text.index(heading)
        end = len(text)
        if index + 1 < len(REQUIRED_HEADINGS):
            end = text.index(REQUIRED_HEADINGS[index + 1], start + len(heading))
        section_text = text[start:end]

        for anchor in SECTION_ANCHORS[heading]:
            assert anchor in section_text, f"Missing anchor in {heading}: {anchor}"


def test_naming_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_naming_text()

    for phrase in REQUIRED_PHRASES:
        assert phrase in text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_naming_stays_within_line_budget() -> None:
    text = _read_naming_text()

    assert len(text.splitlines()) <= MAX_LINE_COUNT, f"Naming doc exceeds line budget of {MAX_LINE_COUNT}"
