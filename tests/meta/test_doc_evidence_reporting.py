from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_REPORTING_PATH = REPO_ROOT / "docs" / "evidence-reporting.md"
TITLE = "# Evidence and reporting"
ARCHITECTURE_REFERENCE = "[docs/architecture.md](architecture.md)"
AGENT_MODEL_REFERENCE = "[docs/models/agent-model.md](models/agent-model.md)"
SCENARIO_MODEL_REFERENCE = "[docs/models/scenario-model.md](models/scenario-model.md)"
EVALUATION_REFERENCE = "[docs/evaluation.md](evaluation.md)"
MAX_LINE_COUNT = 70

REQUIRED_HEADINGS: list[str] = [
    "## Scope and layer boundary",
    "## EvidenceRecord, ClaimRecord, and GateResult concepts",
    "## Evidence store expectations",
    "## Markdown and JSON reporting expectations",
    "## SQL DDL note",
]

SECTION_ANCHORS: dict[str, list[str]] = {
    "## Scope and layer boundary": [
        "`abdp.evidence` is the layer 7 boundary for execution traces, observations, and supporting artifacts.",
        "`abdp.reporting` is the layer 8 boundary for presentation-ready `markdown` and `JSON` outputs.",
        ("The schema-vs-implementation boundary is explicit: no abdp.evidence or abdp.reporting code lands in v0.1."),
        (
            "Evidence and reporting consume `metrics`, `gate` outcomes, "
            "and frozen run outputs without mutating `SimulationState`."
        ),
    ],
    "## EvidenceRecord, ClaimRecord, and GateResult concepts": [
        (
            "`EvidenceRecord` is the canonical schema record for a single observed fact, "
            "artifact, or linkage to stored data."
        ),
        (
            "`ClaimRecord` is the canonical schema record for a derived statement that cites "
            "one or more `EvidenceRecord` values."
        ),
        "`GateResult` is the canonical schema record for a `gate` judgment tied to `metrics`, thresholds, and status.",
        "Records may carry `Seed`, `JsonValue`, and `stable_hash` values to preserve deterministic joins across runs.",
        (
            "Records may refer to `SimulationState`, `ActionProposal`, `ScenarioSpec`, "
            "`SnapshotManifest`, and `SnapshotRef` identities."
        ),
    ],
    "## Evidence store expectations": [
        "An `evidence store` preserves immutable records plus references to `bronze`, `silver`, and `gold` artifacts.",
        (
            "Store entries may point at `SnapshotManifest` or `SnapshotRef` metadata "
            "rather than copying large payloads inline."
        ),
        (
            "Store keys should be stable across reruns when `Seed`, scenario identity, "
            "and canonical `JsonValue` content match."
        ),
        (
            "The store contract is schema-oriented: field names, identifiers, "
            "and relations are in scope; file layouts are not."
        ),
    ],
    "## Markdown and JSON reporting expectations": [
        (
            "`abdp.reporting` should render the same underlying records into "
            "human-readable `markdown` and machine-readable `JSON`."
        ),
        (
            "Reports should summarize `metrics`, `GateResult`, and cited "
            "`ClaimRecord` or `EvidenceRecord` entries without new logic."
        ),
        (
            "A report may group by scenario, segment, participant, or run when "
            "those identities already exist in `SimulationState`."
        ),
        (
            "Reporting may include links back to `ActionProposal` and `SnapshotManifest` "
            "records so derived summaries stay auditable."
        ),
    ],
    "## SQL DDL note": [
        "A future `SQL DDL` may declare schema objects for `EvidenceRecord`, `ClaimRecord`, and `GateResult`.",
        (
            "This note is schema-level only: required columns, keys, and relations are in scope, "
            "but migrations and storage engines are not."
        ),
        (
            "Real SQL migrations, concrete database setup, and `abdp.evidence` or "
            "`abdp.reporting` implementation stay `post-v0.1`."
        ),
    ],
}

REQUIRED_PHRASES: list[str] = [
    "`abdp.evidence`",
    "`abdp.reporting`",
    "layer 7",
    "layer 8",
    "`evidence`",
    "`reporting`",
    "`v0.1`",
    "`post-v0.1`",
    "no abdp.evidence or abdp.reporting code lands in v0.1",
    "schema-vs-implementation",
    "`EvidenceRecord`",
    "`ClaimRecord`",
    "`GateResult`",
    "`evidence store`",
    "`markdown`",
    "`JSON`",
    "`SQL DDL`",
    "`metrics`",
    "`gate`",
    "`SnapshotManifest`",
    "`SnapshotRef`",
    "`SimulationState`",
    "`ActionProposal`",
    "`ScenarioSpec`",
    "`Seed`",
    "`JsonValue`",
    "`stable_hash`",
    "`bronze`",
    "`silver`",
    "`gold`",
    "schema-level only",
]

FORBIDDEN_SNIPPETS: list[str] = [
    "SQLAlchemy",
    "Alembic",
    "Django",
    "Flask",
    "FastAPI",
    "CREATE TABLE",
    "Postgres",
    "PostgreSQL",
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
]


def _read_evidence_reporting_text() -> str:
    return EVIDENCE_REPORTING_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: list[str]) -> None:
    position = -1
    for snippet in snippets:
        next_position = text.find(snippet, position + 1)
        assert next_position != -1, f"Missing snippet: {snippet}"
        assert next_position > position, f"Snippet out of order: {snippet}"
        position = next_position


def test_evidence_reporting_file_exists() -> None:
    assert EVIDENCE_REPORTING_PATH.is_file(), f"Expected evidence/reporting doc at {EVIDENCE_REPORTING_PATH}"


def test_evidence_reporting_has_title_and_single_doc_references() -> None:
    text = _read_evidence_reporting_text()

    assert text.startswith(f"{TITLE}\n"), f"Expected evidence/reporting doc to start with {TITLE!r}"
    assert text.count(ARCHITECTURE_REFERENCE) == 1, (
        f"Expected exactly one architecture reference: {ARCHITECTURE_REFERENCE}"
    )
    assert text.count(AGENT_MODEL_REFERENCE) == 1, (
        f"Expected exactly one agent model reference: {AGENT_MODEL_REFERENCE}"
    )
    assert text.count(SCENARIO_MODEL_REFERENCE) == 1, (
        f"Expected exactly one scenario model reference: {SCENARIO_MODEL_REFERENCE}"
    )
    assert text.count(EVALUATION_REFERENCE) == 1, f"Expected exactly one evaluation reference: {EVALUATION_REFERENCE}"


def test_evidence_reporting_has_required_section_headings_in_order() -> None:
    text = _read_evidence_reporting_text()

    _assert_snippets_in_order(text, REQUIRED_HEADINGS)


def test_evidence_reporting_sections_include_expected_anchors() -> None:
    text = _read_evidence_reporting_text()

    for index, heading in enumerate(REQUIRED_HEADINGS):
        start = text.index(heading)
        end = len(text)
        if index + 1 < len(REQUIRED_HEADINGS):
            end = text.index(REQUIRED_HEADINGS[index + 1], start + len(heading))
        section_text = text[start:end]

        for anchor in SECTION_ANCHORS[heading]:
            assert anchor in section_text, f"Missing anchor in {heading}: {anchor}"


def test_evidence_reporting_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_evidence_reporting_text()

    for phrase in REQUIRED_PHRASES:
        assert phrase in text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_evidence_reporting_stays_within_line_budget() -> None:
    text = _read_evidence_reporting_text()

    assert len(text.splitlines()) <= MAX_LINE_COUNT, f"Evidence/reporting doc exceeds line budget of {MAX_LINE_COUNT}"
