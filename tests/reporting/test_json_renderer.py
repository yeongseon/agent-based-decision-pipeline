"""Tests for ``abdp.reporting.render_json_report``."""

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import pytest

from abdp.core import Seed
from abdp.evaluation import EvaluationSummary, GateStatus
from abdp.evaluation.gate import GateResult
from abdp.evaluation.metric import MetricResult
from abdp.evidence import AuditLog, ClaimRecord, EvidenceRecord
from abdp.reporting import render_json_report
from abdp.scenario import ScenarioRun
from abdp.scenario.step import ScenarioStep
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState
from abdp.simulation.snapshot_ref import SnapshotRef


@dataclass(frozen=True, slots=True)
class _Segment:
    """SegmentState dataclass with an extra field that must be projected away."""

    segment_id: str
    participant_ids: tuple[str, ...]
    extra_segment_field: str = "should-not-appear"


@dataclass(frozen=True, slots=True)
class _Participant:
    """ParticipantState dataclass with an extra field that must be projected away."""

    participant_id: str
    extra_participant_field: str = "should-not-appear"


@dataclass(frozen=True, slots=True)
class _Action:
    """ActionProposal dataclass with an extra field that must be projected away."""

    proposal_id: str
    actor_id: str
    action_key: str
    payload: Any
    extra_action_field: str = "should-not-appear"


@dataclass(frozen=True, slots=True)
class _Decision:
    """AgentDecision dataclass with an extra field that must be projected away."""

    agent_id: str
    proposals: tuple[_Action, ...]
    extra_decision_field: str = "should-not-appear"


def _state(
    *,
    segments: tuple[_Segment, ...] = (),
    participants: tuple[_Participant, ...] = (),
    pending_actions: tuple[_Action, ...] = (),
) -> SimulationState[SegmentState, ParticipantState, ActionProposal]:
    return SimulationState[SegmentState, ParticipantState, ActionProposal](
        step_index=0,
        seed=Seed(0),
        snapshot_ref=SnapshotRef(
            snapshot_id=UUID("00000000-0000-0000-0000-000000000001"),
            tier="bronze",
            storage_key="snapshots/run",
        ),
        segments=segments,
        participants=participants,
        pending_actions=pending_actions,
    )


def _run(
    *,
    steps: tuple[ScenarioStep[SegmentState, ParticipantState, ActionProposal], ...] = (),
) -> ScenarioRun[SegmentState, ParticipantState, ActionProposal]:
    return ScenarioRun[SegmentState, ParticipantState, ActionProposal](
        scenario_key="k",
        seed=Seed(0),
        steps=steps,
        final_state=_state(),
    )


def _summary() -> EvaluationSummary:
    return EvaluationSummary(
        metrics=(MetricResult(metric_id="m", value=1, details={}),),
        gates=(GateResult(gate_id="g", status=GateStatus.PASS, reason="ok", details={}),),
        overall_status=GateStatus.PASS,
    )


def _evidence() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=UUID(int=1),
        evidence_key="ek",
        step_index=0,
        agent_id="agent",
        payload={"x": 1},
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _claim() -> ClaimRecord:
    return ClaimRecord(
        claim_id=UUID(int=100),
        statement="s",
        evidence_ids=(UUID(int=1),),
        confidence=0.5,
        metadata={},
    )


def _audit(
    *,
    run: ScenarioRun[SegmentState, ParticipantState, ActionProposal] | None = None,
) -> AuditLog[SegmentState, ParticipantState, ActionProposal]:
    return AuditLog[SegmentState, ParticipantState, ActionProposal](
        scenario_key="k",
        seed=Seed(0),
        run=run if run is not None else _run(),
        summary=_summary(),
        evidence=(_evidence(),),
        claims=(_claim(),),
    )


def test_render_json_report_is_deterministic() -> None:
    audit = _audit()
    assert render_json_report(audit) == render_json_report(audit)


def test_render_json_report_sorts_keys() -> None:
    rendered = render_json_report(_audit())
    parsed = json.loads(rendered)
    top_keys = [line.split('"')[1] for line in rendered.splitlines() if line.startswith('  "')]
    assert top_keys == sorted(parsed.keys())


def test_render_json_report_round_trip_preserves_structure() -> None:
    audit = _audit()
    parsed = json.loads(render_json_report(audit))
    assert parsed["scenario_key"] == "k"
    assert parsed["seed"] == 0
    assert parsed["summary"]["overall_status"] == "pass"
    assert parsed["evidence"][0]["evidence_key"] == "ek"
    assert parsed["claims"][0]["statement"] == "s"


def test_render_json_report_serializes_uuid_as_canonical_string() -> None:
    parsed = json.loads(render_json_report(_audit()))
    assert parsed["evidence"][0]["evidence_id"] == "00000000-0000-0000-0000-000000000001"


def test_render_json_report_serializes_utc_datetime_as_iso8601() -> None:
    parsed = json.loads(render_json_report(_audit()))
    assert parsed["evidence"][0]["created_at"] == "2026-01-01T00:00:00+00:00"


def test_render_json_report_rejects_naive_datetime() -> None:
    @dataclass(frozen=True, slots=True)
    class _Wrap:
        when: datetime

    naive = _Wrap(when=datetime(2026, 1, 1))
    with pytest.raises(ValueError, match="UTC"):
        render_json_report(naive)  # type: ignore[arg-type]


def test_render_json_report_rejects_non_utc_datetime() -> None:
    @dataclass(frozen=True, slots=True)
    class _Wrap:
        when: datetime

    other = _Wrap(when=datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=9))))
    with pytest.raises(ValueError, match="UTC"):
        render_json_report(other)  # type: ignore[arg-type]


def test_render_json_report_serializes_tuple_as_list() -> None:
    parsed = json.loads(render_json_report(_audit()))
    assert isinstance(parsed["evidence"], list)
    assert isinstance(parsed["claims"][0]["evidence_ids"], list)


def test_render_json_report_serializes_gate_status_as_string() -> None:
    parsed = json.loads(render_json_report(_audit()))
    assert parsed["summary"]["gates"][0]["status"] == "pass"
    assert parsed["summary"]["overall_status"] == "pass"


def test_render_json_report_default_indent_is_two() -> None:
    rendered = render_json_report(_audit())
    assert '\n  "scenario_key"' in rendered


def test_render_json_report_indent_zero_still_uses_newlines() -> None:
    rendered = render_json_report(_audit(), indent=0)
    assert "\n" in rendered


def test_render_json_report_projects_action_proposal_protocol_only() -> None:
    action = _Action(proposal_id="p", actor_id="a", action_key="k", payload={"v": 1})
    state = _state(pending_actions=(action,))
    run = _run(
        steps=(
            ScenarioStep[SegmentState, ParticipantState, ActionProposal](
                state=state,
                decisions=(),
                proposals=(action,),
            ),
        )
    )
    rendered = render_json_report(_audit(run=run))
    assert "extra_action_field" not in rendered


def test_render_json_report_projects_segment_state_protocol_only() -> None:
    seg = _Segment(segment_id="s1", participant_ids=("p1",))
    state = _state(segments=(seg,))
    run = _run(
        steps=(ScenarioStep[SegmentState, ParticipantState, ActionProposal](state=state, decisions=(), proposals=()),)
    )
    rendered = render_json_report(_audit(run=run))
    assert "extra_segment_field" not in rendered


def test_render_json_report_projects_participant_state_protocol_only() -> None:
    part = _Participant(participant_id="p1")
    state = _state(participants=(part,))
    run = _run(
        steps=(ScenarioStep[SegmentState, ParticipantState, ActionProposal](state=state, decisions=(), proposals=()),)
    )
    rendered = render_json_report(_audit(run=run))
    assert "extra_participant_field" not in rendered


def test_render_json_report_projects_agent_decision_protocol_only() -> None:
    action = _Action(proposal_id="p", actor_id="a", action_key="k", payload=None)
    decision = _Decision(agent_id="ag", proposals=(action,))
    state = _state(pending_actions=(action,))
    run = _run(
        steps=(
            ScenarioStep[SegmentState, ParticipantState, ActionProposal](
                state=state, decisions=(decision,), proposals=(action,)
            ),
        )
    )
    rendered = render_json_report(_audit(run=run))
    assert "extra_decision_field" not in rendered


def test_render_json_report_rejects_unsupported_type() -> None:
    class Opaque:
        pass

    with pytest.raises(TypeError, match="cannot serialize"):
        render_json_report(Opaque())  # type: ignore[arg-type]


def test_render_json_report_rejects_non_string_dict_key() -> None:
    @dataclass(frozen=True, slots=True)
    class _Wrap:
        m: dict[Any, Any]

    with pytest.raises(TypeError, match="dict key"):
        render_json_report(_Wrap(m={1: "v"}))  # type: ignore[arg-type]


def test_render_json_report_rejects_nan_float() -> None:
    @dataclass(frozen=True, slots=True)
    class _Wrap:
        v: float

    with pytest.raises(ValueError):
        render_json_report(_Wrap(v=float("nan")))  # type: ignore[arg-type]


def test_render_json_report_golden_vector() -> None:
    rendered = render_json_report(_audit())
    expected = (
        "{\n"
        '  "claims": [\n'
        "    {\n"
        '      "claim_id": "00000000-0000-0000-0000-000000000064",\n'
        '      "confidence": 0.5,\n'
        '      "evidence_ids": [\n'
        '        "00000000-0000-0000-0000-000000000001"\n'
        "      ],\n"
        '      "metadata": {},\n'
        '      "statement": "s"\n'
        "    }\n"
        "  ],\n"
        '  "evidence": [\n'
        "    {\n"
        '      "agent_id": "agent",\n'
        '      "created_at": "2026-01-01T00:00:00+00:00",\n'
        '      "evidence_id": "00000000-0000-0000-0000-000000000001",\n'
        '      "evidence_key": "ek",\n'
        '      "payload": {\n'
        '        "x": 1\n'
        "      },\n"
        '      "step_index": 0\n'
        "    }\n"
        "  ],\n"
        '  "run": {\n'
        '    "final_state": {\n'
        '      "participants": [],\n'
        '      "pending_actions": [],\n'
        '      "seed": 0,\n'
        '      "segments": [],\n'
        '      "snapshot_ref": {\n'
        '        "snapshot_id": "00000000-0000-0000-0000-000000000001",\n'
        '        "storage_key": "snapshots/run",\n'
        '        "tier": "bronze"\n'
        "      },\n"
        '      "step_index": 0\n'
        "    },\n"
        '    "scenario_key": "k",\n'
        '    "seed": 0,\n'
        '    "steps": []\n'
        "  },\n"
        '  "scenario_key": "k",\n'
        '  "seed": 0,\n'
        '  "summary": {\n'
        '    "gates": [\n'
        "      {\n"
        '        "details": {},\n'
        '        "gate_id": "g",\n'
        '        "reason": "ok",\n'
        '        "status": "pass"\n'
        "      }\n"
        "    ],\n"
        '    "metrics": [\n'
        "      {\n"
        '        "details": {},\n'
        '        "metric_id": "m",\n'
        '        "value": 1\n'
        "      }\n"
        "    ],\n"
        '    "overall_status": "pass"\n'
        "  }\n"
        "}"
    )
    assert rendered == expected
