import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRIBUTING_PATH = REPO_ROOT / "CONTRIBUTING.md"

TITLE = "# Contributing"
MAX_LINE_COUNT = 155

DOC_REFERENCE_COUNTS = {
    "[AGENTS.md](AGENTS.md)": 1,
}

REQUIRED_HEADINGS = [
    "## Overview",
    "## Issue intake and sizing",
    "## Branch and commit conventions",
    "## TDD workflow",
    "## Oracle consult and review",
    "## Local verification and CI gate",
    "## Docstring and type rules",
    "## Pull request structure",
]

SECTION_ANCHORS = {
    "## Overview": [
        "This guide is the operating manual for day-to-day contribution work in this repository.",
        (
            "The file-and-test workflow is: pick one issue, add the failing test, make the "
            "smallest change that passes, verify locally, and open one focused PR."
        ),
        "If a change needs broader design discussion, pause and get the Oracle consult before you code.",
    ],
    "## Issue intake and sizing": [
        "one issue -> one focused pull request.",
        "do not bundle concepts into one PR.",
        (
            "If a task spans unrelated concerns or cannot fit in one RED -> GREEN -> "
            "REFACTOR cycle, split it before coding."
        ),
    ],
    "## Branch and commit conventions": [
        "Create branches as `<type>/<NNN>-<slug>`.",
        "Use Conventional Commits for commit subjects.",
        "Every commit message references the issue number as `(#NN)`.",
    ],
    "## TDD workflow": [
        "TDD is strict: RED -> GREEN -> REFACTOR.",
        "RED means write or update the smallest failing test first.",
        (
            "For documentation work, start with a meta test that fails on the missing "
            "guidance, then expand the document until the test passes."
        ),
    ],
    "## Oracle consult and review": [
        (
            "Request an Oracle consult before implementation when the change affects "
            "design, contributor workflow, contracts, or scoring expectations."
        ),
        "oracle review score = 100/100.",
        (
            "The oracle scoring rubric is Correctness 30, Test quality 25, API design 20, "
            "Documentation 10, Type strictness 10, and Conventions/process 5."
        ),
    ],
    "## Local verification and CI gate": [
        "Formatting and linting use ruff format strict with line-length 120.",
        "CI gate means the protected main branch must be green before merge.",
        "Do not use `--no-verify` to bypass hooks or checks.",
    ],
    "## Docstring and type rules": [
        "No `Any` without justification.",
        "No `# type: ignore`; use `typing.cast` when narrowing is required.",
        "Prefer `@runtime_checkable` Protocol contracts with an anchored module docstring.",
    ],
    "## Pull request structure": [
        "The PR body should use this structure:",
        "`TDD evidence` with the RED commit and GREEN commit, plus REFACTOR when used",
        ("PRs are squash-merged after review, and the merge flow deletes the branch with `--delete-branch`."),
    ],
}

REQUIRED_PHRASES = [
    "file-and-test workflow",
    "one issue -> one focused pull request",
    "do not bundle concepts into one PR",
    "Create branches as `<type>/<NNN>-<slug>`",
    "Conventional Commits",
    "RED",
    "GREEN",
    "REFACTOR",
    "oracle review score = 100/100",
    "oracle scoring rubric",
    "ruff format .",
    "ruff check .",
    "mypy --strict src tests",
    "pytest --cov",
    "CI gate",
    "--no-verify",
    "No `Any` without justification.",
    "No `# type: ignore`; use `typing.cast` when narrowing is required.",
    "Use PEP 695 syntax",
    "@runtime_checkable",
    "`Closes #N`",
    "Mutmut policy",
    "--delete-branch",
    "100% line coverage on new code is required.",
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
    "code of conduct",
    "governance policy",
    "release policy",
]


def _read_text() -> str:
    return CONTRIBUTING_PATH.read_text(encoding="utf-8")


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


def test_contributing_file_exists() -> None:
    assert CONTRIBUTING_PATH.is_file()


def test_contributing_has_title_and_single_doc_references() -> None:
    text = _read_text()

    assert text.startswith(f"{TITLE}\n")
    assert text.count(TITLE) == 1

    for reference, expected_count in DOC_REFERENCE_COUNTS.items():
        assert text.count(reference) == expected_count


def test_contributing_has_required_section_headings_in_order() -> None:
    text = _read_text()
    cursor = 0

    for heading in REQUIRED_HEADINGS:
        position = text.find(heading, cursor)
        assert position != -1, f"Missing heading: {heading}"
        cursor = position + len(heading)


def test_contributing_sections_include_expected_anchors() -> None:
    text = _read_text()
    sections = _section_texts(text)

    for heading, anchors in SECTION_ANCHORS.items():
        section_text = sections[heading]
        for anchor in anchors:
            assert _normalize(anchor) in section_text, f"Missing anchor in {heading}: {anchor}"


def test_contributing_includes_required_phrases_and_omits_forbidden_snippets() -> None:
    text = _read_text()
    normalized_text = _normalize(text)

    for phrase in REQUIRED_PHRASES:
        assert _normalize(phrase) in normalized_text, f"Missing required phrase: {phrase}"

    for snippet in FORBIDDEN_SNIPPETS:
        assert snippet not in text, f"Forbidden snippet present: {snippet}"


def test_contributing_stays_within_line_budget() -> None:
    line_count = len(_read_text().splitlines())
    assert line_count <= MAX_LINE_COUNT
