from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_MODEL_PATH = REPO_ROOT / "docs" / "models" / "agent-model.md"
TITLE = "# Agent model"
ARCHITECTURE_REFERENCE = "[docs/architecture.md](../architecture.md)"
SCENARIO_MODEL_REFERENCE = "[docs/models/scenario-model.md](scenario-model.md)"
MAX_LINE_COUNT = 70

REQUIRED_HEADINGS: list[str] = [
    "## Scope and layer boundary",
    "## Observation, decision, and action lifecycle",
    "## Agent contract boundary",
    "## Relationship to ActionProposal and ScenarioSpec",
]

SECTION_ANCHORS: dict[str, list[str]] = {
    "## Scope and layer boundary": [
        "An agent observes `SimulationState`, decides under a policy boundary, and emits `ActionProposal` values.",
        "The agent layer owns proposal generation, not state mutation or scenario assembly.",
        "Domain plugins may supply their own agents without changing `abdp.simulation`.",
        "Concrete model providers, prompt wiring, and transport adapters stay outside this model.",
    ],
    "## Observation, decision, and action lifecycle": [
        "Observation reads the current `SimulationState` as input and does not mutate it.",
        "Decision applies a rule-based, model-based, or hybrid policy behind the agent boundary.",
        "Action emission returns zero or more `ActionProposal` values for the current step.",
        (
            "Simulation consumes emitted proposals later; the agent does not record an `action` "
            "or write a `snapshot` directly."
        ),
    ],
    "## Agent contract boundary": [
        "The minimal agent boundary is observe current state, decide, and propose next actions.",
        "An agent contract may depend on `SimulationState` and return `ActionProposal` values only.",
        ("The boundary does not include provider clients, prompt formats, tool registries, or persistence APIs."),
        ("Agents stay pluggable per domain because domain meaning lives in the plugin, not in the framework contract."),
    ],
    "## Relationship to ActionProposal and ScenarioSpec": [
        (
            "Every emitted proposal must satisfy `ActionProposal` with `proposal_id`, `actor_id`, "
            "`action_key`, and `payload`."
        ),
        "`payload` stays a `JsonValue`, so agent outputs remain domain-neutral at the framework boundary.",
        (
            "`ScenarioSpec` remains responsible for `scenario_key`, `seed`, and `build_initial_state()` "
            "before observation begins."
        ),
        (
            "Agents consume the seeded initial state and may surface proposals via `pending_actions` "
            "in `SimulationState`."
        ),
    ],
}

REQUIRED_PHRASES: list[str] = [
    "`abdp.agents`",
    "layer 4",
    "v0.1",
    "`agents`",
    "`abdp.simulation`",
    "`SimulationState`",
    "`ActionProposal`",
    "`ScenarioSpec`",
    "`proposal_id`",
    "`actor_id`",
    "`action_key`",
    "`payload`",
    "`JsonValue`",
    "`scenario_key`",
    "`seed`",
    "`build_initial_state()`",
    "`pending_actions`",
    "`action`",
    "`snapshot`",
    "Domain plugins",
    "policy boundary",
]

FORBIDDEN_SNIPPETS: list[str] = [
    "OpenAI",
    "Anthropic",
    "LangChain",
    "LiteLLM",
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


def _read_agent_model_text() -> str:
    return AGENT_MODEL_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: list[str]) -> None:
    position = -1
    for snippet in snippets:
        next_position = text.find(snippet, position + 1)
        assert next_position != -1, f"Missing snippet: {snippet}"
        assert next_position > position, f"Snippet out of order: {snippet}"
        position = next_position


def test_agent_model_file_exists() -> None:
    assert AGENT_MODEL_PATH.is_file(), f"Expected agent model doc at {AGENT_MODEL_PATH}"


def test_agent_model_has_title_and_single_references() -> None:
    text = _read_agent_model_text()

    assert text.startswith(f"{TITLE}\n"), f"Expected agent model doc to start with {TITLE!r}"
    assert text.count(ARCHITECTURE_REFERENCE) == 1, (
        f"Expected exactly one architecture reference: {ARCHITECTURE_REFERENCE}"
    )
    assert text.count(SCENARIO_MODEL_REFERENCE) == 1, (
        f"Expected exactly one scenario model reference: {SCENARIO_MODEL_REFERENCE}"
    )


def test_agent_model_has_required_section_headings_in_order() -> None:
    text = _read_agent_model_text()

    _assert_snippets_in_order(text, REQUIRED_HEADINGS)


def test_agent_model_sections_include_expected_anchors() -> None:
    text = _read_agent_model_text()

    for index, heading in enumerate(REQUIRED_HEADINGS):
        start = text.index(heading)
        end = len(text)
        if index + 1 < len(REQUIRED_HEADINGS):
            end = text.index(REQUIRED_HEADINGS[index + 1], start + len(heading))
        section_text = text[start:end]

        for anchor in SECTION_ANCHORS[heading]:
            assert anchor in section_text, f"Missing anchor in {heading}: {anchor}"


def test_agent_model_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_agent_model_text()

    for phrase in REQUIRED_PHRASES:
        assert phrase in text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_agent_model_stays_within_line_budget() -> None:
    text = _read_agent_model_text()

    assert len(text.splitlines()) <= MAX_LINE_COUNT, f"Agent model doc exceeds line budget of {MAX_LINE_COUNT}"
