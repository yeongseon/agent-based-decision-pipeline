from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOMAIN_MODEL_PATH = REPO_ROOT / "docs" / "models" / "domain-model.md"
TITLE = "# Domain model"
ARCHITECTURE_REFERENCE = "[docs/architecture.md](../architecture.md)"
MAX_LINE_COUNT = 70

REQUIRED_HEADINGS: list[str] = [
    "## Framework concepts vs. domain concepts",
    "## Primitive invariants",
    "## Abstraction admission rule",
]

SECTION_ANCHORS: dict[str, list[str]] = {
    "## Framework concepts vs. domain concepts": [
        "Framework concepts describe reusable decision-model structure without assuming a business field.",
        "Domain concepts describe field-specific meaning and stay outside `abdp.core`.",
        "Domain plugins map their own objects onto framework primitives without changing the core framework.",
        "A domain concept gives field-specific meaning to a subject, participant, segment, action, or snapshot.",
    ],
    "## Primitive invariants": [
        "`subject` is the focal unit of state for a run and keeps a stable identity across segments and snapshots.",
        "`participant` is an actor or system role with a stable identity for a run and is not a subject by default.",
        (
            "`segment` is an ordered slice of a run that groups related actions and snapshots "
            "without adding domain meaning."
        ),
        "`action` is a recorded decision step in a segment and is treated as an append-only fact for that run.",
        "`snapshot` is an immutable state view that stays reproducible for the same inputs and seed-aware execution.",
    ],
    "## Abstraction admission rule": [
        "A new framework abstraction is justified only when the same need is evidenced in at least two domains.",
        "One domain-specific use case is not enough to add a new primitive to `abdp.core`.",
        (
            "If the evidence is weaker than two domains, keep the concept in the domain plugin "
            "and map it onto existing primitives."
        ),
        (
            "Generic contracts belong in the framework only after the same boundary and invariants "
            "hold in at least two domains."
        ),
    ],
}

REQUIRED_PHRASES: list[str] = [
    "`abdp.core`",
    "`subject`",
    "`participant`",
    "`segment`",
    "`action`",
    "`snapshot`",
    "framework concepts",
    "domain concepts",
    "domain plugins",
    "at least two domains",
    "generic contracts",
    "seed-aware",
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


def _read_domain_model_text() -> str:
    return DOMAIN_MODEL_PATH.read_text(encoding="utf-8")


def _assert_snippets_in_order(text: str, snippets: list[str]) -> None:
    position = -1
    for snippet in snippets:
        next_position = text.find(snippet, position + 1)
        assert next_position != -1, f"Missing snippet: {snippet}"
        assert next_position > position, f"Snippet out of order: {snippet}"
        position = next_position


def test_domain_model_file_exists() -> None:
    assert DOMAIN_MODEL_PATH.is_file(), f"Expected domain model doc at {DOMAIN_MODEL_PATH}"


def test_domain_model_has_title_and_single_architecture_reference() -> None:
    text = _read_domain_model_text()

    assert text.startswith(f"{TITLE}\n"), f"Expected domain model doc to start with {TITLE!r}"
    assert text.count(ARCHITECTURE_REFERENCE) == 1, (
        f"Expected exactly one architecture reference: {ARCHITECTURE_REFERENCE}"
    )


def test_domain_model_has_required_section_headings_in_order() -> None:
    text = _read_domain_model_text()

    _assert_snippets_in_order(text, REQUIRED_HEADINGS)


def test_domain_model_sections_include_expected_anchors() -> None:
    text = _read_domain_model_text()

    for index, heading in enumerate(REQUIRED_HEADINGS):
        start = text.index(heading)
        end = len(text)
        if index + 1 < len(REQUIRED_HEADINGS):
            end = text.index(REQUIRED_HEADINGS[index + 1], start + len(heading))
        section_text = text[start:end]

        for anchor in SECTION_ANCHORS[heading]:
            assert anchor in section_text, f"Missing anchor in {heading}: {anchor}"


def test_domain_model_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_domain_model_text()

    for phrase in REQUIRED_PHRASES:
        assert phrase in text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_domain_model_stays_within_line_budget() -> None:
    text = _read_domain_model_text()

    assert len(text.splitlines()) <= MAX_LINE_COUNT, f"Domain model doc exceeds line budget of {MAX_LINE_COUNT}"
