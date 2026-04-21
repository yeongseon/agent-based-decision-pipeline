from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_STRUCTURE_PATH = REPO_ROOT / "docs" / "repository-structure.md"
TITLE = "# Repository structure"
ARCHITECTURE_REFERENCE = "[docs/architecture.md](architecture.md)"
MAX_LINE_COUNT = 70

REQUIRED_HEADINGS: list[str] = [
    "## Current top-level tree",
    "## Placement rules",
    "## Reserved domains layer",
]

SECTION_ANCHORS: dict[str, list[str]] = {
    "## Current top-level tree": [
        ".github/workflows/ci.yml",
        "docs/",
        "src/",
        "tests/",
    ],
    "## Placement rules": [
        (
            "`src/abdp/` holds framework source code, with layer packages such as "
            "`abdp.core`, `abdp.data`, and `abdp.simulation`."
        ),
        "New layer code follows `src/abdp/<layer>/`, and layer names come from the architecture document.",
        "`tests/meta/` holds repository and documentation contract tests.",
        "`tests/unit/` holds unit tests for code under `src/abdp/`.",
        "`docs/` holds framework documentation only and does not hold executable framework code.",
    ],
    "## Reserved domains layer": [
        "`abdp.domains` stays reserved as the framework layer name.",
        "Real domain plugins ship as separate Python packages, not under `src/abdp/domains/`.",
        "Example domain plugins follow the same rule and stay outside the `src/abdp/` tree.",
        "Do not add domain-specific package names anywhere under `src/abdp/`.",
    ],
}

REQUIRED_PHRASES: list[str] = [
    "`src/abdp/`",
    "`src/abdp/<layer>/`",
    "`tests/meta/`",
    "`tests/unit/`",
    "`docs/`",
    "`abdp.domains`",
    "`abdp.core`",
    "`abdp.data`",
    "`abdp.simulation`",
    "`docs/naming.md`",
    "`docs/prd.md`",
    "separate Python packages",
]

FORBIDDEN_SNIPPETS: list[str] = [
    "abdp/realestate/",
    "abdp/housing/",
    "RealEstateAgent",
    "Korean",
    "mortgage",
]


def _read_repository_structure_text() -> str:
    return REPOSITORY_STRUCTURE_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: list[str]) -> None:
    position = -1
    for snippet in snippets:
        next_position = text.find(snippet, position + 1)
        assert next_position != -1, f"Missing snippet: {snippet}"
        assert next_position > position, f"Snippet out of order: {snippet}"
        position = next_position


def test_repository_structure_file_exists() -> None:
    assert REPOSITORY_STRUCTURE_PATH.is_file(), f"Expected repository structure doc at {REPOSITORY_STRUCTURE_PATH}"


def test_repository_structure_has_title_and_single_architecture_reference() -> None:
    text = _read_repository_structure_text()

    assert text.startswith(f"{TITLE}\n"), f"Expected repository structure doc to start with {TITLE!r}"
    assert text.count(ARCHITECTURE_REFERENCE) == 1, (
        f"Expected exactly one architecture reference: {ARCHITECTURE_REFERENCE}"
    )


def test_repository_structure_has_required_section_headings_in_order() -> None:
    text = _read_repository_structure_text()

    _assert_snippets_in_order(text, REQUIRED_HEADINGS)


def test_repository_structure_sections_include_expected_anchors() -> None:
    text = _read_repository_structure_text()

    for index, heading in enumerate(REQUIRED_HEADINGS):
        start = text.index(heading)
        end = len(text)
        if index + 1 < len(REQUIRED_HEADINGS):
            end = text.index(REQUIRED_HEADINGS[index + 1], start + len(heading))
        section_text = text[start:end]

        for anchor in SECTION_ANCHORS[heading]:
            assert anchor in section_text, f"Missing anchor in {heading}: {anchor}"


def test_repository_structure_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_repository_structure_text()

    for phrase in REQUIRED_PHRASES:
        assert phrase in text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_repository_structure_stays_within_line_budget() -> None:
    text = _read_repository_structure_text()

    assert len(text.splitlines()) <= MAX_LINE_COUNT, f"Repository structure doc exceeds line budget of {MAX_LINE_COUNT}"
