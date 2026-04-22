from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_PATH = REPO_ROOT / "docs" / "evaluation.md"
TITLE = "# Evaluation"
ARCHITECTURE_REFERENCE = "[docs/architecture.md](architecture.md)"
AGENT_MODEL_REFERENCE = "[docs/models/agent-model.md](models/agent-model.md)"
SCENARIO_MODEL_REFERENCE = "[docs/models/scenario-model.md](models/scenario-model.md)"
MAX_LINE_COUNT = 70

REQUIRED_HEADINGS: list[str] = [
    "## Scope and layer boundary",
    "## Metrics and gate evaluation",
    "## Result aggregation",
    "## Inputs consumed from simulation and data outputs",
]

SECTION_ANCHORS: dict[str, list[str]] = {
    "## Scope and layer boundary": [
        "`abdp.evaluation` is the layer 6 boundary for post-run `metrics`, `gate` evaluation, and `aggregation`.",
        "In `v0.1`, evaluation is documented only; `post-v0.1` work may implement code against frozen contracts.",
        "Evaluation reads simulation and data outputs after execution and does not mutate `abdp.simulation` state.",
        "Evidence collection and reporting formats stay outside this document.",
    ],
    "## Metrics and gate evaluation": [
        (
            "Evaluation computes `metrics` from deterministic run outputs rather than inventing new "
            "domain-specific score names."
        ),
        "A `gate` is a rule that interprets one or more metric results against documented thresholds or predicates.",
        (
            "Gate evaluation may yield pass, fail, or similar neutral judgments without changing the "
            "recorded run artifacts."
        ),
        "Metric and gate definitions stay domain-neutral in the framework; domain meaning belongs in plugins.",
    ],
    "## Result aggregation": [
        "`aggregation` combines metric results and gate outcomes into a run-level or comparison-level summary.",
        (
            "Aggregation may group by scenario, segment, participant, or repeated run set when those "
            "identities already exist."
        ),
        (
            "Aggregation records derived outcomes, not new simulation actions, and does not replace "
            "evidence or reporting."
        ),
        (
            "If multiple runs are compared, aggregation should preserve which scenario identity and `Seed` "
            "produced each result."
        ),
    ],
    "## Inputs consumed from simulation and data outputs": [
        (
            "Evaluation may consume `SimulationState` outputs such as `step_index`, `segments`, "
            "`participants`, and `pending_actions`."
        ),
        (
            "Evaluation may inspect emitted `ActionProposal` values, including `proposal_id`, "
            "`actor_id`, `action_key`, and `payload`."
        ),
        (
            "Evaluation may read `SnapshotManifest`, `SnapshotRef`, and tiered `bronze`, `silver`, "
            "and `gold` outputs from `abdp.data`."
        ),
        (
            "Shared inputs may include `ScenarioSpec` metadata such as `scenario_key`, plus `Seed`, "
            "`JsonValue`, and `stable_hash` values used to join records."
        ),
    ],
}

REQUIRED_PHRASES: list[str] = [
    "`abdp.evaluation`",
    "layer 6",
    "`evaluation`",
    "`v0.1`",
    "`post-v0.1`",
    "`SimulationState`",
    "`ActionProposal`",
    "`SnapshotManifest`",
    "`SnapshotRef`",
    "`ScenarioSpec`",
    "`scenario_key`",
    "`Seed`",
    "`JsonValue`",
    "`stable_hash`",
    "`proposal_id`",
    "`actor_id`",
    "`action_key`",
    "`payload`",
    "`step_index`",
    "`segments`",
    "`participants`",
    "`pending_actions`",
    "`bronze`",
    "`silver`",
    "`gold`",
    "`abdp.simulation`",
    "`abdp.data`",
    "`metrics`",
    "`gate`",
    "`aggregation`",
    "domain-specific score names",
    "evidence",
    "reporting",
]

FORBIDDEN_SNIPPETS: list[str] = [
    "OpenAI",
    "Anthropic",
    "LangChain",
    "LiteLLM",
    "MLflow",
    "Weights & Biases",
    "W&B",
    "ROI",
    "vacancy rate",
    "rental yield",
    "cap rate",
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


def _read_evaluation_text() -> str:
    return EVALUATION_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: list[str]) -> None:
    position = -1
    for snippet in snippets:
        next_position = text.find(snippet, position + 1)
        assert next_position != -1, f"Missing snippet: {snippet}"
        assert next_position > position, f"Snippet out of order: {snippet}"
        position = next_position


def test_evaluation_file_exists() -> None:
    assert EVALUATION_PATH.is_file(), f"Expected evaluation doc at {EVALUATION_PATH}"


def test_evaluation_has_title_and_single_doc_references() -> None:
    text = _read_evaluation_text()

    assert text.startswith(f"{TITLE}\n"), f"Expected evaluation doc to start with {TITLE!r}"
    assert text.count(ARCHITECTURE_REFERENCE) == 1, (
        f"Expected exactly one architecture reference: {ARCHITECTURE_REFERENCE}"
    )
    assert text.count(AGENT_MODEL_REFERENCE) == 1, (
        f"Expected exactly one agent model reference: {AGENT_MODEL_REFERENCE}"
    )
    assert text.count(SCENARIO_MODEL_REFERENCE) == 1, (
        f"Expected exactly one scenario model reference: {SCENARIO_MODEL_REFERENCE}"
    )


def test_evaluation_has_required_section_headings_in_order() -> None:
    text = _read_evaluation_text()

    _assert_snippets_in_order(text, REQUIRED_HEADINGS)


def test_evaluation_sections_include_expected_anchors() -> None:
    text = _read_evaluation_text()

    for index, heading in enumerate(REQUIRED_HEADINGS):
        start = text.index(heading)
        end = len(text)
        if index + 1 < len(REQUIRED_HEADINGS):
            end = text.index(REQUIRED_HEADINGS[index + 1], start + len(heading))
        section_text = text[start:end]

        for anchor in SECTION_ANCHORS[heading]:
            assert anchor in section_text, f"Missing anchor in {heading}: {anchor}"


def test_evaluation_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_evaluation_text()

    for phrase in REQUIRED_PHRASES:
        assert phrase in text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_evaluation_stays_within_line_budget() -> None:
    text = _read_evaluation_text()

    assert len(text.splitlines()) <= MAX_LINE_COUNT, f"Evaluation doc exceeds line budget of {MAX_LINE_COUNT}"
