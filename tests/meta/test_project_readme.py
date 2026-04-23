from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"

TAGLINE = "A Python framework for reproducible agent-based decision simulation"

SECTION_HEADINGS: tuple[str, ...] = (
    "## What it is",
    "## Why it exists",
    "## Getting started",
    "## Roadmap",
    "## Used by",
)

SECTION_SNIPPETS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "## What it is",
        (
            "reproducible agent-based decision simulation",
            "[non-goals](docs/vision.md#non-goals)",
        ),
    ),
    (
        "## Why it exists",
        (
            "rebuild one-off simulations",
            "[vision](docs/vision.md)",
        ),
    ),
    (
        "## Getting started",
        (
            "pip install -e .",
            "[10-minute modeling quickstart](docs/quickstart.md)",
            "`abdp.agents`",
            "`abdp.scenario`",
            "`ScenarioRunner`",
        ),
    ),
    (
        "## Roadmap",
        ("[Roadmap](docs/roadmap.md)",),
    ),
    (
        "## Used by",
        ("[`kpubdata-lab/younggeul`](https://github.com/kpubdata-lab/younggeul)",),
    ),
)

FORBIDDEN_SNIPPETS: tuple[str, ...] = (
    "v1.0",
    "production-ready",
    "will support",
    "enterprise",
    "milestone sequencing",
)

MAX_PROJECT_README_LINES = 60


def _read_readme_text() -> str:
    assert README_PATH.is_file(), README_PATH
    return README_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: tuple[str, ...]) -> None:
    start = 0
    for snippet in snippets:
        index = text.find(snippet, start)
        assert index >= 0, snippet
        start = index + len(snippet)


def test_project_readme_exists() -> None:
    assert README_PATH.is_file()


def test_project_readme_includes_tagline_and_required_sections_in_order() -> None:
    text = _read_readme_text()

    assert "# agent-based-decision-pipeline" in text
    assert TAGLINE in text
    _assert_snippets_in_order(text, SECTION_HEADINGS)


def test_each_readme_section_contains_expected_snippets() -> None:
    text = _read_readme_text()

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


def test_project_readme_avoids_forbidden_scope_and_stays_within_line_budget() -> None:
    text = _read_readme_text()

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, snippet

    assert len(text.splitlines()) <= MAX_PROJECT_README_LINES
