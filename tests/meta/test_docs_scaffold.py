from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_INDEX_PATH = REPO_ROOT / "docs" / "README.md"
DEVELOPMENT_README_PATH = REPO_ROOT / "docs" / "development" / "README.md"
MODELS_README_PATH = REPO_ROOT / "docs" / "models" / "README.md"
EXAMPLES_README_PATH = REPO_ROOT / "docs" / "examples" / "README.md"
ADR_README_PATH = REPO_ROOT / "docs" / "adr" / "README.md"

README_PATHS: tuple[Path, ...] = (
    DOCS_INDEX_PATH,
    DEVELOPMENT_README_PATH,
    MODELS_README_PATH,
    EXAMPLES_README_PATH,
    ADR_README_PATH,
)

MAX_DOCS_INDEX_LINES = 10
MAX_SUBSECTION_README_LINES = 10
MAX_EXAMPLES_INDEX_LINES = 80

EXPECTED_DOCS_INDEX_SNIPPETS = (
    "# Docs",
    "This index is intentionally minimal. Detailed expansion is deferred to #044.",
    "- [Development](development/README.md) — Contributor process and v0.1 issue queue.",
    "- [Models](models/README.md) — Conceptual model documentation for abdp.",
    "- [Examples](examples/README.md) — Worked examples and tutorials.",
    "- [ADRs](adr/README.md) — Architecture decision records and template.",
    "- [CLI](cli.md) — Command-line usage reference for `abdp run` and `abdp report`.",
)

EXPECTED_SUBSECTION_TITLES: tuple[tuple[Path, str], ...] = (
    (DEVELOPMENT_README_PATH, "# Development"),
    (MODELS_README_PATH, "# Models"),
    (EXAMPLES_README_PATH, "# Examples"),
    (ADR_README_PATH, "# ADRs"),
)

EXPECTED_PLACEHOLDER_SUBSECTION_README_SNIPPETS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (
        DEVELOPMENT_README_PATH,
        (
            "# Development",
            "Placeholder only. Contributor process and v0.1 issue queue live here.",
            "Detailed expansion is deferred to #044.",
        ),
    ),
    (
        MODELS_README_PATH,
        (
            "# Models",
            "Placeholder only. Conceptual model documentation for abdp lives here.",
            "Detailed expansion is deferred to #044.",
        ),
    ),
    (
        ADR_README_PATH,
        (
            "# ADRs",
            "Architecture decision records live here.",
            "Start from [0000-template.md](0000-template.md) when writing a new ADR.",
            "Directory index details are deferred to #044.",
        ),
    ),
)

EXPECTED_EXAMPLES_INDEX_SECTIONS: tuple[str, ...] = (
    "## Credit underwriting",
    "## Queue scheduling",
    "## Frozen outputs",
)

EXPECTED_EXAMPLES_INDEX_SNIPPETS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "## Credit underwriting",
        (
            "python -m examples.credit_underwriting",
            "[`examples/credit_underwriting`](../../examples/credit_underwriting)",
            "`examples.credit_underwriting.audit:build_audit_log`",
            "`selected_proposal`",
            "non-empty proposal step",
        ),
    ),
    (
        "## Queue scheduling",
        (
            "python -m examples.queue_scheduling",
            "[`examples/queue_scheduling`](../../examples/queue_scheduling)",
            "`examples.queue_scheduling.audit:build_audit_log`",
            "`selected_proposal`",
            "non-empty proposal step",
        ),
    ),
    (
        "## Frozen outputs",
        (
            "[`outputs/credit_underwriting_report.json`](outputs/credit_underwriting_report.json)",
            "[`outputs/queue_scheduling_report.json`](outputs/queue_scheduling_report.json)",
            "byte-identical",
        ),
    ),
)

FORBIDDEN_EXAMPLES_INDEX_SNIPPETS: tuple[str, ...] = (
    "coming soon",
    "future example",
    "will support",
    "production-ready",
    "enterprise",
    "v1.0",
    "milestone sequencing",
    "Placeholder only.",
    "Detailed expansion is deferred to #044.",
)

EXPECTED_ADR_TEMPLATE_POINTER = "Start from [0000-template.md](0000-template.md) when writing a new ADR."


def _read_text(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: tuple[str, ...]) -> None:
    start = 0
    for snippet in snippets:
        index = text.find(snippet, start)
        assert index >= 0, snippet
        start = index + len(snippet)


def test_docs_scaffold_files_exist() -> None:
    for path in README_PATHS:
        assert path.is_file(), path


def test_docs_index_declares_expected_navigation_and_stays_short() -> None:
    docs_index_text = _read_text(DOCS_INDEX_PATH)

    _assert_snippets_in_order(docs_index_text, EXPECTED_DOCS_INDEX_SNIPPETS)

    assert len(docs_index_text.splitlines()) < MAX_DOCS_INDEX_LINES


def test_subsection_readmes_declare_expected_titles() -> None:
    for path, expected_title in EXPECTED_SUBSECTION_TITLES:
        assert expected_title in _read_text(path)


def test_placeholder_subsection_readmes_remain_short() -> None:
    for path, expected_snippets in EXPECTED_PLACEHOLDER_SUBSECTION_README_SNIPPETS:
        readme_text = _read_text(path)

        _assert_snippets_in_order(readme_text, expected_snippets)

        assert len(readme_text.splitlines()) < MAX_SUBSECTION_README_LINES


def test_examples_index_surfaces_runnable_examples_and_frozen_outputs() -> None:
    text = _read_text(EXAMPLES_README_PATH)

    _assert_snippets_in_order(text, EXPECTED_EXAMPLES_INDEX_SECTIONS)

    for index, (heading, snippets) in enumerate(EXPECTED_EXAMPLES_INDEX_SNIPPETS):
        section_start = text.index(heading)
        if index + 1 < len(EXPECTED_EXAMPLES_INDEX_SNIPPETS):
            next_heading = EXPECTED_EXAMPLES_INDEX_SNIPPETS[index + 1][0]
            section_end = text.index(next_heading, section_start + len(heading))
        else:
            section_end = len(text)

        section_text = text[section_start:section_end]
        for snippet in snippets:
            assert snippet in section_text, f"{heading}: {snippet}"


def test_examples_index_avoids_forbidden_scope_and_stays_within_line_budget() -> None:
    text = _read_text(EXAMPLES_README_PATH)

    for snippet in FORBIDDEN_EXAMPLES_INDEX_SNIPPETS:
        assert snippet not in text, snippet

    assert len(text.splitlines()) <= MAX_EXAMPLES_INDEX_LINES


def test_adr_readme_references_template() -> None:
    adr_readme_text = _read_text(ADR_README_PATH)

    assert EXPECTED_ADR_TEMPLATE_POINTER in adr_readme_text
