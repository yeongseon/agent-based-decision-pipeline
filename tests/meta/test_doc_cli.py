from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_DOC_PATH = REPO_ROOT / "docs" / "cli.md"

TITLE = "# CLI"

SECTION_HEADINGS: tuple[str, ...] = (
    "## Install",
    "## Commands",
    "## Running a scenario",
    "## Rendering a report",
    "## Exit codes",
    "## Reproducibility notes",
    "## CLI vs programmatic API",
)

SECTION_SNIPPETS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "## Install",
        ("uv sync",),
    ),
    (
        "## Commands",
        (
            "`abdp run`",
            "`abdp report`",
        ),
    ),
    (
        "## Running a scenario",
        (
            "abdp run <module.path:callable> --seed N [--output FILE]",
            "module.path:callable",
            "--seed",
            "--output",
            "JSON",
            "stdout",
        ),
    ),
    (
        "## Rendering a report",
        (
            "abdp report <path> --format {json,markdown} [--output FILE]",
            "--format",
            "json",
            "markdown",
            "AuditLog",
        ),
    ),
    (
        "## Exit codes",
        (
            "| `abdp run` | `0` |",
            "| `abdp run` | `1` |",
            "| `abdp run` | `2` |",
            "| `abdp report` | `0` |",
            "| `abdp report` | `2` |",
            "WARN",
            "stderr",
        ),
    ),
    (
        "## Reproducibility notes",
        (
            "`--seed`",
            "uint32",
            "byte-identical",
        ),
    ),
    (
        "## CLI vs programmatic API",
        (
            "[10-minute modeling quickstart](quickstart.md)",
            "`ScenarioRunner`",
        ),
    ),
)

FORBIDDEN_SNIPPETS: tuple[str, ...] = (
    "HTTP",
    "REST",
    "server",
    "dashboard",
    "hosted service",
    "plugin system",
    "dynamic discovery",
    "v1.0",
    "production-ready",
    "will support",
    "enterprise",
    "milestone sequencing",
)

MAX_CLI_DOC_LINES = 120


def _read_cli_doc_text() -> str:
    assert CLI_DOC_PATH.is_file(), CLI_DOC_PATH
    return CLI_DOC_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: tuple[str, ...]) -> None:
    start = 0
    for snippet in snippets:
        index = text.find(snippet, start)
        assert index >= 0, snippet
        start = index + len(snippet)


def test_cli_doc_exists() -> None:
    assert CLI_DOC_PATH.is_file()


def test_cli_doc_has_title_and_required_sections_in_order() -> None:
    text = _read_cli_doc_text()

    assert TITLE in text
    _assert_snippets_in_order(text, SECTION_HEADINGS)


def test_each_cli_doc_section_contains_expected_snippets() -> None:
    text = _read_cli_doc_text()

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


def test_cli_doc_avoids_forbidden_scope_and_stays_within_line_budget() -> None:
    text = _read_cli_doc_text()

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, snippet

    assert len(text.splitlines()) <= MAX_CLI_DOC_LINES
