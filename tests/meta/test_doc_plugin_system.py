from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_SYSTEM_PATH = REPO_ROOT / "docs" / "plugin-system.md"
TITLE = "# Plugin system"
ARCHITECTURE_REFERENCE = "[docs/architecture.md](architecture.md)"
REPOSITORY_STRUCTURE_REFERENCE = "[docs/repository-structure.md](repository-structure.md)"
DOMAIN_MODEL_REFERENCE = "[docs/models/domain-model.md](models/domain-model.md)"
MAX_LINE_COUNT = 70

REQUIRED_HEADINGS: list[str] = [
    "## Package boundary",
    "## Compatibility and versioning",
    "## Allowed dependencies",
]

SECTION_ANCHORS: dict[str, list[str]] = {
    "## Package boundary": [
        "Domain plugins ship as separate Python packages from the framework.",
        "In v0.1, plugin code MUST NOT live under `src/abdp/`, including `src/abdp/domains/`.",
        "`src/abdp/` stays reserved for framework code only.",
        "A plugin maps its concepts onto `abdp.core` primitives.",
        "Single-domain code stays inside the plugin and does not leak into framework layers.",
    ],
    "## Compatibility and versioning": [
        "Plugins are defined against abdp contracts, not against the loader implementation.",
        "Each plugin declares an ABDP version range it supports.",
        "v0.1 makes no promise about internal-module stability across minor versions.",
        "An incompatible change requires the plugin to release a compatible version.",
    ],
    "## Allowed dependencies": [
        "Plugins may depend on `abdp.core`, `abdp.data`, and `abdp.simulation`.",
        "Plugins may depend on their own packages and on third-party libraries.",
        "Plugins MUST NOT depend on docs, tests, or repository paths of the framework.",
        "Lower framework layers MUST NOT import plugins or plugin repositories.",
        "Randomness used inside a plugin stays seed-aware.",
    ],
}

REQUIRED_PHRASES: list[str] = [
    "src/abdp/",
    "`src/abdp/`",
    "`src/abdp/domains/`",
    "abdp contracts",
    "`abdp.core`",
    "`abdp.data`",
    "`abdp.simulation`",
    "separate Python packages",
    "plugin repositories",
    "version range",
    "domain plugin",
    "plugin loader implementation",
    "third-party libraries",
    "seed-aware",
]

FORBIDDEN_SNIPPETS: list[str] = [
    "real estate",
    "real-estate",
    "housing",
    "mortgage",
    "insurance",
    "retail",
    "korean",
    "Korean",
    "south korea",
    "RealEstateAgent",
]


def _read_plugin_system_text() -> str:
    return PLUGIN_SYSTEM_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: list[str]) -> None:
    position = -1
    for snippet in snippets:
        next_position = text.find(snippet, position + 1)
        assert next_position != -1, f"Missing snippet: {snippet}"
        assert next_position > position, f"Snippet out of order: {snippet}"
        position = next_position


def test_plugin_system_file_exists() -> None:
    assert PLUGIN_SYSTEM_PATH.is_file(), f"Expected plugin system doc at {PLUGIN_SYSTEM_PATH}"


def test_plugin_system_has_title_and_single_doc_references() -> None:
    text = _read_plugin_system_text()

    assert text.startswith(f"{TITLE}\n"), f"Expected plugin system doc to start with {TITLE!r}"
    assert text.count(ARCHITECTURE_REFERENCE) == 1, (
        f"Expected exactly one architecture reference: {ARCHITECTURE_REFERENCE}"
    )
    assert text.count(REPOSITORY_STRUCTURE_REFERENCE) == 1, (
        f"Expected exactly one repository structure reference: {REPOSITORY_STRUCTURE_REFERENCE}"
    )
    assert text.count(DOMAIN_MODEL_REFERENCE) == 1, (
        f"Expected exactly one domain model reference: {DOMAIN_MODEL_REFERENCE}"
    )


def test_plugin_system_has_required_section_headings_in_order() -> None:
    text = _read_plugin_system_text()

    _assert_snippets_in_order(text, REQUIRED_HEADINGS)


def test_plugin_system_sections_include_expected_anchors() -> None:
    text = _read_plugin_system_text()

    for index, heading in enumerate(REQUIRED_HEADINGS):
        start = text.index(heading)
        end = len(text)
        if index + 1 < len(REQUIRED_HEADINGS):
            end = text.index(REQUIRED_HEADINGS[index + 1], start + len(heading))
        section_text = text[start:end]

        for anchor in SECTION_ANCHORS[heading]:
            assert anchor in section_text, f"Missing anchor in {heading}: {anchor}"


def test_plugin_system_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_plugin_system_text()

    for phrase in REQUIRED_PHRASES:
        assert phrase in text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_plugin_system_stays_within_line_budget() -> None:
    text = _read_plugin_system_text()

    assert len(text.splitlines()) <= MAX_LINE_COUNT, f"Plugin system doc exceeds line budget of {MAX_LINE_COUNT}"
