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

MAX_README_LINES = 10

EXPECTED_DOCS_INDEX_SNIPPETS = (
    "# Docs",
    "This index is intentionally minimal. Detailed expansion is deferred to #044.",
    "- [Development](development/README.md) — Contributor process and v0.1 issue queue.",
    "- [Models](models/README.md) — Conceptual model documentation for abdp.",
    "- [Examples](examples/README.md) — Worked examples and tutorials.",
    "- [ADRs](adr/README.md) — Architecture decision records and template.",
)

EXPECTED_SUBSECTION_TITLES: tuple[tuple[Path, str], ...] = (
    (DEVELOPMENT_README_PATH, "# Development"),
    (MODELS_README_PATH, "# Models"),
    (EXAMPLES_README_PATH, "# Examples"),
    (ADR_README_PATH, "# ADRs"),
)

EXPECTED_SUBSECTION_README_SNIPPETS: tuple[tuple[Path, tuple[str, ...]], ...] = (
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
        EXAMPLES_README_PATH,
        (
            "# Examples",
            "Placeholder only. Worked examples and tutorials live here.",
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

EXPECTED_ADR_TEMPLATE_POINTER = "Start from [0000-template.md](0000-template.md) when writing a new ADR."


def test_docs_scaffold_files_exist() -> None:
    for path in README_PATHS:
        assert path.is_file(), path


def test_docs_index_declares_expected_navigation_and_stays_short() -> None:
    assert DOCS_INDEX_PATH.is_file(), DOCS_INDEX_PATH
    docs_index_text = DOCS_INDEX_PATH.read_text(encoding="utf-8")

    start = 0
    for snippet in EXPECTED_DOCS_INDEX_SNIPPETS:
        index = docs_index_text.find(snippet, start)
        assert index >= 0, snippet
        start = index + len(snippet)

    assert len(docs_index_text.splitlines()) < MAX_README_LINES


def test_subsection_readmes_declare_expected_titles() -> None:
    for path, expected_title in EXPECTED_SUBSECTION_TITLES:
        assert path.is_file(), path
        readme_text = path.read_text(encoding="utf-8")

        assert expected_title in readme_text


def test_subsection_readmes_remain_placeholders_and_stay_short() -> None:
    for path, expected_snippets in EXPECTED_SUBSECTION_README_SNIPPETS:
        assert path.is_file(), path
        readme_text = path.read_text(encoding="utf-8")

        start = 0
        for snippet in expected_snippets:
            index = readme_text.find(snippet, start)
            assert index >= 0, snippet
            start = index + len(snippet)

        assert len(readme_text.splitlines()) < MAX_README_LINES


def test_adr_readme_references_template() -> None:
    assert ADR_README_PATH.is_file(), ADR_README_PATH
    adr_readme_text = ADR_README_PATH.read_text(encoding="utf-8")

    assert EXPECTED_ADR_TEMPLATE_POINTER in adr_readme_text
