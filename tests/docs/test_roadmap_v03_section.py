"""Verification of the v0.3 roadmap section."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROADMAP_PATH = REPO_ROOT / "docs" / "roadmap.md"

V03_ISSUE_NUMBERS: tuple[int, ...] = tuple(range(106, 126))

REQUIRED_AREA_HEADINGS: tuple[str, ...] = (
    "abdp.evaluation",
    "abdp.evidence",
    "abdp.reporting",
    "abdp.cli",
)

RESERVED_EVIDENCE_KEY = "selected_proposal"

NON_GOAL_TERMS: tuple[str, ...] = (
    "remote storage",
    "plugin system",
    "web UI",
    "src/abdp",
)

ISSUE_BULLET_PATTERN = re.compile(
    r"^- `#(?P<num>\d+)` — `(?P<title>[^`]+)`: (?P<goal>.+\.)$",
)


def _read_roadmap_body() -> str:
    return ROADMAP_PATH.read_text(encoding="utf-8")


def _bullet_lines_by_issue() -> dict[int, str]:
    bullets: dict[int, str] = {}
    for line in _read_roadmap_body().splitlines():
        match = ISSUE_BULLET_PATTERN.match(line)
        if match is None:
            continue
        bullets[int(match.group("num"))] = line
    return bullets


def test_roadmap_has_v03_section_heading() -> None:
    assert "## v0.3 milestone scope" in _read_roadmap_body()


def test_roadmap_v03_section_lists_all_twenty_issue_numbers() -> None:
    body = _read_roadmap_body()
    for number in V03_ISSUE_NUMBERS:
        assert f"#{number}" in body, f"missing roadmap entry for #{number}"


def test_roadmap_v03_each_issue_has_individual_bullet_with_one_line_goal() -> None:
    bullets = _bullet_lines_by_issue()
    for number in V03_ISSUE_NUMBERS:
        assert number in bullets, f"issue #{number} must have its own '- `#{number}` — `<title>`: <goal>.' bullet"
        match = ISSUE_BULLET_PATTERN.match(bullets[number])
        assert match is not None
        goal = match.group("goal").strip()
        assert len(goal) >= 10, f"issue #{number} goal text is too short: {goal!r}"


def test_roadmap_v03_section_mentions_each_v03_area() -> None:
    body = _read_roadmap_body()
    for area in REQUIRED_AREA_HEADINGS:
        assert area in body, f"missing v0.3 area: {area}"


def test_roadmap_reserves_selected_proposal_evidence_key() -> None:
    body = _read_roadmap_body()
    assert RESERVED_EVIDENCE_KEY in body
    assert "Reserved evidence keys" in body or "reserved evidence key" in body


def test_roadmap_v03_section_has_non_goals_subsection() -> None:
    body = _read_roadmap_body()
    assert "## Explicit non-goals for v0.3" in body
    for term in NON_GOAL_TERMS:
        assert term in body, f"missing v0.3 non-goal term: {term}"
