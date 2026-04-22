from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROADMAP_PATH = REPO_ROOT / "docs" / "roadmap.md"
TITLE = "# Roadmap"
ARCHITECTURE_REFERENCE = "[docs/architecture.md](architecture.md)"
AGENT_MODEL_REFERENCE = "[docs/models/agent-model.md](models/agent-model.md)"
EVALUATION_REFERENCE = "[docs/evaluation.md](evaluation.md)"
EVIDENCE_REPORTING_REFERENCE = "[docs/evidence-reporting.md](evidence-reporting.md)"
MAX_LINE_COUNT = 90

REQUIRED_HEADINGS: list[str] = [
    "## Scope and non-goals overview",
    "## v0.1 milestone",
    "## v0.2 milestone themes",
    "## v0.2 modeling toolkit boundary",
    "## Explicit non-goals for v0.2",
    "## v0.3 milestone themes",
    "## Explicit non-goals for v0.1",
    "## Revisit triggers for more complex infrastructure",
]

SECTION_ANCHORS: dict[str, list[str]] = {
    "## Scope and non-goals overview": [
        "This roadmap is milestone-oriented rather than date-oriented.",
        "`v0.1` is the contract baseline for `core`, `data`, and `simulation`.",
        "`v0.2` and `v0.3` describe expansion themes, not calendar promises.",
        "Detailed release engineering and maintainer scheduling are intentionally excluded here.",
    ],
    "## v0.1 milestone": [
        "`v0.1` keeps implementation scope on layers 1-3 contracts: `core`, `data`, and `simulation`.",
        "The agent, evaluation, and evidence/reporting boundary docs stay documentation-first in `v0.1`.",
        "`v0.1` does not implement `abdp.agents`, `abdp.evaluation`, `abdp.evidence`, or `abdp.reporting`.",
        "`v0.1` does not add domain code, provider integrations, or complex infrastructure.",
        "`v0.1` does not promise calendar dates.",
    ],
    "## v0.2 milestone themes": [
        (
            "`v0.2` should prove one thin end-to-end path on top of the frozen contracts "
            "before widening the framework surface."
        ),
        "`v0.2` should add contributor guidance and examples that make the current contracts easier to use.",
        (
            "`v0.2` should test new shared abstractions against at least two domains "
            "before promoting them into the framework."
        ),
        "`v0.2` should keep seeded reproducibility, stable contracts, and simple storage assumptions intact.",
    ],
    "## v0.3 milestone themes": [
        (
            "`v0.3` may broaden implementations around agents, evaluation, evidence, "
            "and reporting once `v0.2` proves the boundaries."
        ),
        ("`v0.3` may refine cross-layer composition instead of introducing parallel stacks or competing abstractions."),
        "`v0.3` may improve comparison, audit, and reporting workflows that build on earlier contract work.",
        "`v0.3` is still a roadmap milestone, not a calendar promise.",
    ],
    "## v0.2 modeling toolkit boundary": [
        "`v0.2` ships the modeling toolkit packages `abdp.agents` and `abdp.scenario`",
        "`#092`",
        "`#093`",
        "`#094`",
        "`#095`",
        "`#096`",
        "`#097`",
        "`#098`",
        "`#099`",
        "`#100`",
        "`#101`",
        "`#102`",
        "`#103`",
        "`#104`",
        "`#105`",
    ],
    "## Explicit non-goals for v0.2": [
        "No evaluation symbols, gates, or summaries belong in `v0.2`; that work is reserved for `v0.3`.",
        "No evidence records, claims, audit logs, or stores belong in `v0.2`; that work is reserved for `v0.3`.",
        "No CLI entry point, run command, or report command belongs in `v0.2`; that work is reserved for `v0.3`.",
        "No persistence backends or storage adapters belong in `v0.2`; the in-memory toolkit must remain sufficient.",
        "No domain-specific code belongs under `src/abdp/**`; domain logic lives only in `examples/` and tests.",
    ],
    "## Explicit non-goals for v0.1": [
        "No implementation work beyond layers 1-3 belongs in `v0.1`; that includes layers 4, 6, 7, and 8.",
        (
            "No domain-specific framework code belongs in `v0.1`; shared abstractions "
            "still need evidence from at least two domains."
        ),
        "No provider-specific clients, orchestration services, or release automation belong in `v0.1`.",
        "No calendar dates, release promises, or detailed release engineering belong in `v0.1`.",
        "No complex infrastructure belongs in `v0.1` while the file-and-test workflow remains sufficient.",
    ],
    "## Revisit triggers for more complex infrastructure": [
        (
            "Revisit more complex infrastructure when the same pain appears across "
            "at least two domains or contributor workflows."
        ),
        (
            "Revisit it when layer 4, 6, 7, or 8 implementations create repeated "
            "manual steps that simple tests and docs cannot police."
        ),
        (
            "Revisit it when seeded local workflows stop being enough to validate "
            "reproducibility, evidence links, or reporting outputs."
        ),
        "Revisit it only after the simpler contract-and-tests path is clearly failing for current work.",
    ],
}

REQUIRED_PHRASES: list[str] = [
    "`v0.1`",
    "`v0.2`",
    "`v0.3`",
    "contributors",
    "milestone-oriented",
    "date-oriented",
    "layers 1-3",
    "`core`",
    "`data`",
    "`simulation`",
    "boundary docs",
    "documentation-first",
    "`abdp.agents`",
    "`abdp.evaluation`",
    "`abdp.evidence`",
    "`abdp.reporting`",
    "domain code",
    "provider integrations",
    "calendar dates",
    "calendar promises",
    "detailed release engineering",
    "maintainer",
    "one thin end-to-end path",
    "contributor guidance",
    "two domains",
    "seeded reproducibility",
    "stable contracts",
    "simple storage assumptions",
    "cross-layer composition",
    "comparison",
    "audit",
    "release automation",
    "complex infrastructure",
    "file-and-test workflow",
    "contract baseline",
    "modeling toolkit",
    "`abdp.agents`",
    "`abdp.scenario`",
    "`examples/`",
]

FORBIDDEN_SNIPPETS: list[str] = [
    "SQLAlchemy",
    "Alembic",
    "Django",
    "Flask",
    "FastAPI",
    "OpenAI",
    "Anthropic",
    "MLflow",
    "Weights & Biases",
    "W&B",
    "real estate",
    "real-estate",
    "mortgage",
    "vacancy rate",
    "korean",
    "Korean",
    "south korea",
    "Q1",
    "Q2",
    "Q3",
    "Q4",
    "2024",
    "2025",
    "2026",
    "2027",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def _read_roadmap_text() -> str:
    return ROADMAP_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: list[str]) -> None:
    position = -1
    for snippet in snippets:
        next_position = text.find(snippet, position + 1)
        assert next_position != -1, f"Missing snippet: {snippet}"
        assert next_position > position, f"Snippet out of order: {snippet}"
        position = next_position


def test_roadmap_file_exists() -> None:
    assert ROADMAP_PATH.is_file(), f"Expected roadmap doc at {ROADMAP_PATH}"


def test_roadmap_has_title_and_single_doc_references() -> None:
    text = _read_roadmap_text()

    assert text.startswith(f"{TITLE}\n"), f"Expected roadmap doc to start with {TITLE!r}"
    assert (
        text.count(ARCHITECTURE_REFERENCE) == 1
    ), f"Expected exactly one architecture reference: {ARCHITECTURE_REFERENCE}"
    assert (
        text.count(AGENT_MODEL_REFERENCE) == 1
    ), f"Expected exactly one agent model reference: {AGENT_MODEL_REFERENCE}"
    assert text.count(EVALUATION_REFERENCE) == 1, f"Expected exactly one evaluation reference: {EVALUATION_REFERENCE}"
    assert (
        text.count(EVIDENCE_REPORTING_REFERENCE) == 1
    ), f"Expected exactly one evidence/reporting reference: {EVIDENCE_REPORTING_REFERENCE}"


def test_roadmap_has_required_section_headings_in_order() -> None:
    text = _read_roadmap_text()

    _assert_snippets_in_order(text, REQUIRED_HEADINGS)


def test_roadmap_sections_include_expected_anchors() -> None:
    text = _read_roadmap_text()

    for index, heading in enumerate(REQUIRED_HEADINGS):
        start = text.index(heading)
        end = len(text)
        if index + 1 < len(REQUIRED_HEADINGS):
            end = text.index(REQUIRED_HEADINGS[index + 1], start + len(heading))
        section_text = text[start:end]

        for anchor in SECTION_ANCHORS[heading]:
            assert anchor in section_text, f"Missing anchor in {heading}: {anchor}"


def test_roadmap_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_roadmap_text()

    for phrase in REQUIRED_PHRASES:
        assert phrase in text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_roadmap_stays_within_line_budget() -> None:
    text = _read_roadmap_text()

    assert len(text.splitlines()) <= MAX_LINE_COUNT, f"Roadmap doc exceeds line budget of {MAX_LINE_COUNT}"
