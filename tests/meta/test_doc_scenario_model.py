from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_MODEL_PATH = REPO_ROOT / "docs" / "models" / "scenario-model.md"
TITLE = "# Scenario model"
ARCHITECTURE_REFERENCE = "[docs/architecture.md](../architecture.md)"
DOMAIN_MODEL_REFERENCE = "[docs/models/domain-model.md](domain-model.md)"
MAX_LINE_COUNT = 70

REQUIRED_HEADINGS: list[str] = [
    "## Scope and reused primitives",
    "## Scenario and execution concepts",
    "## Relationship model",
    "## Seed-awareness expectation",
]

SECTION_ANCHORS: dict[str, list[str]] = {
    "## Scope and reused primitives": [
        ("This model defines neutral simulation vocabulary that `data` and `simulation` may encode without layer 5."),
        ("This document reuses `subject`, `participant`, `segment`, `action`, and `snapshot` from the domain model."),
        ("It introduces `scenario`, `action proposal`, and `simulation step` without redefining existing primitives."),
        "A `scenario` adds runnable structure and execution ordering, not domain meaning.",
    ],
    "## Scenario and execution concepts": [
        "A `scenario` binds one or more `subject` instances, participants, segments, and an entry `snapshot`.",
        ("An `action proposal` is a candidate next `action` considered during a `simulation step` before recording."),
        "A `simulation step` is the smallest ordered execution unit in a scenario run.",
        (
            "A step reads the current `snapshot`, evaluates available `action proposal` values, "
            "and may record an `action`."
        ),
    ],
    "## Relationship model": [
        "A `scenario` contains one or more ordered `segment` values.",
        "Each `segment` contains zero or more ordered `simulation step` values.",
        "A `participant` may appear in one or more segments within the same scenario.",
        ("A scenario may track one `subject` or multiple `subject` instances with stable identities across the run."),
        "Recorded `action` and resulting `snapshot` values stay associated with segment and subject identities.",
    ],
    "## Seed-awareness expectation": [
        (
            "Scenario execution must be seed-aware whenever randomness affects proposals, "
            "action choice, or state transition."
        ),
        (
            "The same scenario inputs and same seed must produce the same ordered steps, "
            "`action` values, and `snapshot` values."
        ),
        ("Different seeds may change outcomes only where the simulation contract explicitly allows random variation."),
        (
            "Seed-awareness constrains execution semantics here, not shock specifications "
            "or layer 5 agent implementations."
        ),
    ],
}

REQUIRED_PHRASES: list[str] = [
    "`scenario`",
    "`subject`",
    "`participant`",
    "`segment`",
    "`action`",
    "`snapshot`",
    "`action proposal`",
    "`simulation step`",
    "`data`",
    "`simulation`",
    "seed-aware",
    "same seed",
    "shock specifications",
    "layer 5",
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


def _read_scenario_model_text() -> str:
    return SCENARIO_MODEL_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: list[str]) -> None:
    position = -1
    for snippet in snippets:
        next_position = text.find(snippet, position + 1)
        assert next_position != -1, f"Missing snippet: {snippet}"
        assert next_position > position, f"Snippet out of order: {snippet}"
        position = next_position


def test_scenario_model_file_exists() -> None:
    assert SCENARIO_MODEL_PATH.is_file(), f"Expected scenario model doc at {SCENARIO_MODEL_PATH}"


def test_scenario_model_has_title_and_single_references() -> None:
    text = _read_scenario_model_text()

    assert text.startswith(f"{TITLE}\n"), f"Expected scenario model doc to start with {TITLE!r}"
    assert text.count(ARCHITECTURE_REFERENCE) == 1, (
        f"Expected exactly one architecture reference: {ARCHITECTURE_REFERENCE}"
    )
    assert text.count(DOMAIN_MODEL_REFERENCE) == 1, (
        f"Expected exactly one domain model reference: {DOMAIN_MODEL_REFERENCE}"
    )


def test_scenario_model_has_required_section_headings_in_order() -> None:
    text = _read_scenario_model_text()

    _assert_snippets_in_order(text, REQUIRED_HEADINGS)


def test_scenario_model_sections_include_expected_anchors() -> None:
    text = _read_scenario_model_text()

    for index, heading in enumerate(REQUIRED_HEADINGS):
        start = text.index(heading)
        end = len(text)
        if index + 1 < len(REQUIRED_HEADINGS):
            end = text.index(REQUIRED_HEADINGS[index + 1], start + len(heading))
        section_text = text[start:end]

        for anchor in SECTION_ANCHORS[heading]:
            assert anchor in section_text, f"Missing anchor in {heading}: {anchor}"


def test_scenario_model_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_scenario_model_text()

    for phrase in REQUIRED_PHRASES:
        assert phrase in text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_scenario_model_stays_within_line_budget() -> None:
    text = _read_scenario_model_text()

    assert len(text.splitlines()) <= MAX_LINE_COUNT, f"Scenario model doc exceeds line budget of {MAX_LINE_COUNT}"
