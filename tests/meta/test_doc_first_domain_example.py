import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = REPO_ROOT / "docs" / "examples" / "first-domain-example.md"

TITLE = "# First domain example"
MAX_LINE_COUNT = 105

DOC_REFERENCE_COUNTS = {
    "[docs/architecture.md](../architecture.md)": 1,
    "[docs/models/scenario-model.md](../models/scenario-model.md)": 1,
    "[docs/plugin-system.md](../plugin-system.md)": 1,
}

REQUIRED_HEADINGS = [
    "## Overview",
    "## Domain framing",
    "## Mapping participants and segments",
    "## Mapping action proposals",
    "## Mapping snapshots and scenario",
    "## Plugin packaging boundary",
    "## Comparison to the second-domain proof",
]

SECTION_ANCHORS = {
    "## Overview": [
        "This is the first canonical domain example for ABDP v0.1.",
        (
            "It shows how one credit underwriting workflow maps onto the existing "
            "contracts without extending the framework."
        ),
        "The goal is contract mapping, not plugin implementation.",
    ],
    "## Domain framing": [
        "The domain is a neutral credit underwriting workflow for one loan application.",
        (
            "The applicant is the focal business entity in the example, but the framework "
            "still sees only neutral simulation contracts."
        ),
        "An underwriting job is one run through ordered review segments.",
        "The example stays in credit underwriting and keeps domain meaning outside the framework.",
    ],
    "## Mapping participants and segments": [
        "An applicant maps to `ParticipantState` via `participant_id`.",
        ("A review stage such as intake, verification, or approval maps to `SegmentState` via `segment_id`."),
        ("`SegmentState.participant_ids` lists the participants active in that stage of the underwriting job."),
        ("The framework does not know why a segment exists; it only preserves stable identities and membership."),
    ],
    "## Mapping action proposals": [
        "A recommended next step maps to `ActionProposal`.",
        (
            "`proposal_id` identifies the recommendation, `actor_id` identifies who proposed "
            "it, and `action_key` names the neutral action."
        ),
        ("`payload` carries domain details such as requested documents, risk notes, or a proposed disposition."),
        "The proposal stays a candidate action until the simulation decides what to record next.",
    ],
    "## Mapping snapshots and scenario": [
        "A case extract for the underwriting job is stored as a `SnapshotManifest` in the data layer.",
        ("`SnapshotRef.from_manifest(SnapshotManifest)` gives simulation a lightweight pointer to that case snapshot."),
        (
            "A single underwriting job is represented by one `SimulationState` value with "
            "`step_index`, `snapshot_ref`, `segments`, `participants`, and `pending_actions`."
        ),
        (
            "A domain `ScenarioSpec` sets `scenario_key`, carries `seed`, and "
            "`build_initial_state()` returns the initial `SimulationState`."
        ),
    ],
    "## Plugin packaging boundary": [
        "In real use, this example belongs in a separate plugin package.",
        "Its domain classes live outside `src/abdp/` and outside `src/abdp/simulation/`.",
        "The framework keeps domain concepts out of `src/abdp/`.",
        ("If credit underwriting needs extra fields, the plugin adds them without changing the core contracts."),
    ],
    "## Comparison to the second-domain proof": [
        "This is the first domain proof for the v0.1 contracts.",
        "Issue #046 adds a queue scheduling example as the second domain proof.",
        (
            "If credit underwriting and queue scheduling both fit the same contracts, the "
            "framework boundary is earning its place."
        ),
        "One domain example explains the mapping; the second checks that the contracts stay domain-neutral.",
    ],
}

REQUIRED_PHRASES = [
    "`ParticipantState`",
    "`SegmentState`",
    "`ActionProposal`",
    "`SnapshotRef`",
    "`SimulationState`",
    "`ScenarioSpec`",
    "`SnapshotManifest`",
    "`participant_id`",
    "`segment_id`",
    "`participant_ids`",
    "`proposal_id`",
    "`actor_id`",
    "`action_key`",
    "`payload`",
    "`step_index`",
    "`scenario_key`",
    "`seed`",
    "`build_initial_state()`",
    "`SnapshotRef.from_manifest(SnapshotManifest)`",
    "credit underwriting",
    "In real use, this example belongs in a separate plugin package.",
    "The framework keeps domain concepts out of `src/abdp/`.",
    "Issue #046",
    "queue scheduling",
]

FORBIDDEN_SNIPPETS = [
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
    "housing",
    "tenant",
    "landlord",
    "apartment",
    "condo",
    "lease",
    "rental yield",
    "cap rate",
    "insurance",
]


def _read_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _section_texts(text: str) -> dict[str, str]:
    ordered_positions = [(heading, text.index(heading)) for heading in REQUIRED_HEADINGS]
    ordered_positions.sort(key=lambda item: item[1])

    sections: dict[str, str] = {}
    for index, (heading, start) in enumerate(ordered_positions):
        end = ordered_positions[index + 1][1] if index + 1 < len(ordered_positions) else len(text)
        sections[heading] = _normalize(text[start:end])

    return sections


def test_first_domain_example_file_exists() -> None:
    assert DOC_PATH.is_file()


def test_first_domain_example_has_title_and_single_doc_references() -> None:
    text = _read_text()

    assert text.startswith(f"{TITLE}\n")
    assert text.count(TITLE) == 1

    for reference, expected_count in DOC_REFERENCE_COUNTS.items():
        assert text.count(reference) == expected_count


def test_first_domain_example_has_required_section_headings_in_order() -> None:
    text = _read_text()
    cursor = 0

    for heading in REQUIRED_HEADINGS:
        position = text.find(heading, cursor)
        assert position != -1, f"Missing heading: {heading}"
        cursor = position + len(heading)


def test_first_domain_example_sections_include_expected_anchors() -> None:
    text = _read_text()
    sections = _section_texts(text)

    for heading, anchors in SECTION_ANCHORS.items():
        section_text = sections[heading]
        for anchor in anchors:
            assert _normalize(anchor) in section_text, f"Missing anchor in {heading}: {anchor}"


def test_first_domain_example_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_text()
    normalized_text = _normalize(text)

    for phrase in REQUIRED_PHRASES:
        assert _normalize(phrase) in normalized_text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_first_domain_example_stays_within_line_budget() -> None:
    line_count = len(_read_text().splitlines())
    assert line_count <= MAX_LINE_COUNT
