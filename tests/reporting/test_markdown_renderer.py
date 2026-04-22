"""Tests for ``abdp.reporting.render_markdown_report``."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import pytest

from abdp.core import Seed
from abdp.evaluation import EvaluationSummary, GateStatus
from abdp.evaluation.gate import GateResult
from abdp.evaluation.metric import MetricResult
from abdp.evidence import AuditLog, ClaimRecord, EvidenceRecord
from abdp.reporting import render_markdown_report
from abdp.scenario import ScenarioRun
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState
from abdp.simulation.snapshot_ref import SnapshotRef


def _state() -> SimulationState[SegmentState, ParticipantState, ActionProposal]:
    return SimulationState[SegmentState, ParticipantState, ActionProposal](
        step_index=0,
        seed=Seed(0),
        snapshot_ref=SnapshotRef(
            snapshot_id=UUID("00000000-0000-0000-0000-000000000001"),
            tier="bronze",
            storage_key="snapshots/run",
        ),
        segments=(),
        participants=(),
        pending_actions=(),
    )


def _run() -> ScenarioRun[SegmentState, ParticipantState, ActionProposal]:
    return ScenarioRun[SegmentState, ParticipantState, ActionProposal](
        scenario_key="k",
        seed=Seed(0),
        steps=(),
        final_state=_state(),
    )


def _summary(
    *,
    metrics: tuple[MetricResult, ...] = (),
    gates: tuple[GateResult, ...] = (),
    overall_status: GateStatus = GateStatus.PASS,
) -> EvaluationSummary:
    return EvaluationSummary(metrics=metrics, gates=gates, overall_status=overall_status)


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
    summary: EvaluationSummary | None = None,
    evidence: tuple[EvidenceRecord, ...] | None = None,
    claims: tuple[ClaimRecord, ...] | None = None,
) -> AuditLog[SegmentState, ParticipantState, ActionProposal]:
    return AuditLog[SegmentState, ParticipantState, ActionProposal](
        scenario_key="k",
        seed=Seed(0),
        run=_run(),
        summary=summary if summary is not None else _summary(),
        evidence=evidence if evidence is not None else (_evidence(),),
        claims=claims if claims is not None else (_claim(),),
    )


def test_render_markdown_report_is_deterministic() -> None:
    audit = _audit()
    assert render_markdown_report(audit) == render_markdown_report(audit)


def test_render_markdown_report_rejects_non_audit_log() -> None:
    with pytest.raises(TypeError, match="AuditLog"):
        render_markdown_report({"not": "audit"})  # type: ignore[arg-type]


def test_render_markdown_report_ends_with_newline() -> None:
    rendered = render_markdown_report(_audit())
    assert rendered.endswith("\n")


def test_render_markdown_report_includes_all_sections_in_order() -> None:
    rendered = render_markdown_report(_audit())
    positions = [
        rendered.index("# Audit Report"),
        rendered.index("## Summary"),
        rendered.index("## Metrics"),
        rendered.index("## Gates"),
        rendered.index("## Evidence"),
        rendered.index("## Claims"),
    ]
    assert positions == sorted(positions)


def test_render_markdown_report_header_has_scenario_seed_steps() -> None:
    rendered = render_markdown_report(_audit())
    assert "- Scenario: k" in rendered
    assert "- Seed: 0" in rendered
    assert "- Steps: 0" in rendered


def test_render_markdown_report_summary_has_overall_status() -> None:
    rendered = render_markdown_report(_audit())
    assert "- Overall status: pass" in rendered


def test_render_markdown_report_metrics_table_uses_pipe_syntax() -> None:
    metric = MetricResult(metric_id="m1", value=42, details={"k": "v"})
    rendered = render_markdown_report(_audit(summary=_summary(metrics=(metric,))))
    assert "| Metric ID | Value | Details |" in rendered
    assert "| --- | --- | --- |" in rendered
    assert "| m1 | 42 |" in rendered


def test_render_markdown_report_gates_table_uses_pipe_syntax() -> None:
    gate = GateResult(gate_id="g1", status=GateStatus.WARN, reason="r", details={})
    rendered = render_markdown_report(_audit(summary=_summary(gates=(gate,), overall_status=GateStatus.WARN)))
    assert "| Gate ID | Status | Reason | Details |" in rendered
    assert "| --- | --- | --- | --- |" in rendered
    assert "| g1 | warn | r |" in rendered


def test_render_markdown_report_empty_metrics_table_has_header_and_separator() -> None:
    rendered = render_markdown_report(_audit(summary=_summary()))
    metrics_section = rendered.split("## Metrics", 1)[1].split("##", 1)[0]
    assert "| Metric ID | Value | Details |" in metrics_section
    assert "| --- | --- | --- |" in metrics_section


def test_render_markdown_report_escapes_pipe_in_table_cells() -> None:
    gate = GateResult(gate_id="g", status=GateStatus.FAIL, reason="a|b", details={})
    rendered = render_markdown_report(_audit(summary=_summary(gates=(gate,), overall_status=GateStatus.FAIL)))
    assert "a\\|b" in rendered


def test_render_markdown_report_replaces_newlines_in_cells_with_br() -> None:
    gate = GateResult(gate_id="g", status=GateStatus.FAIL, reason="line1\nline2", details={})
    rendered = render_markdown_report(_audit(summary=_summary(gates=(gate,), overall_status=GateStatus.FAIL)))
    assert "line1<br>line2" in rendered


def test_render_markdown_report_evidence_list_includes_id_and_iso_datetime() -> None:
    rendered = render_markdown_report(_audit())
    assert "00000000-0000-0000-0000-000000000001" in rendered
    assert "2026-01-01T00:00:00+00:00" in rendered


def test_render_markdown_report_claims_list_uses_json_string_for_statement() -> None:
    claim = ClaimRecord(
        claim_id=UUID(int=200),
        statement='has "quotes" in it',
        evidence_ids=(UUID(int=1),),
        confidence=0.9,
        metadata={},
    )
    rendered = render_markdown_report(_audit(claims=(claim,)))
    assert '\\"quotes\\"' in rendered


def test_render_markdown_report_rejects_non_utc_datetime_in_evidence() -> None:
    bad_evidence = EvidenceRecord.__new__(EvidenceRecord)
    object.__setattr__(bad_evidence, "evidence_id", UUID(int=2))
    object.__setattr__(bad_evidence, "evidence_key", "k")
    object.__setattr__(bad_evidence, "step_index", 0)
    object.__setattr__(bad_evidence, "agent_id", "a")
    object.__setattr__(bad_evidence, "payload", {})
    object.__setattr__(bad_evidence, "created_at", datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=9))))
    with pytest.raises(ValueError, match="UTC"):
        render_markdown_report(_audit(evidence=(bad_evidence,)))


def test_render_markdown_report_golden_vector() -> None:
    rendered = render_markdown_report(
        _audit(
            summary=_summary(
                metrics=(MetricResult(metric_id="m", value=1, details={}),),
                gates=(GateResult(gate_id="g", status=GateStatus.PASS, reason="ok", details={}),),
            )
        )
    )
    expected = (
        "# Audit Report\n"
        "\n"
        "- Scenario: k\n"
        "- Seed: 0\n"
        "- Steps: 0\n"
        "\n"
        "## Summary\n"
        "\n"
        "- Overall status: pass\n"
        "- Metrics: 1\n"
        "- Gates: 1\n"
        "- Evidence: 1\n"
        "- Claims: 1\n"
        "\n"
        "## Metrics\n"
        "\n"
        "| Metric ID | Value | Details |\n"
        "| --- | --- | --- |\n"
        "| m | 1 | {} |\n"
        "\n"
        "## Gates\n"
        "\n"
        "| Gate ID | Status | Reason | Details |\n"
        "| --- | --- | --- | --- |\n"
        "| g | pass | ok | {} |\n"
        "\n"
        "## Evidence\n"
        "\n"
        '- 00000000-0000-0000-0000-000000000001 [2026-01-01T00:00:00+00:00] step=0 agent=agent key=ek payload={"x":1}\n'
        "\n"
        "## Claims\n"
        "\n"
        '- 00000000-0000-0000-0000-000000000064 statement="s" confidence=0.5 evidence=["00000000-0000-0000-0000-000000000001"] metadata={}\n'
    )
    assert rendered == expected


def test_render_markdown_report_handles_payload_with_non_string_dict_key() -> None:
    bad_metric = MetricResult(metric_id="m", value={1: "v"}, details={})  # type: ignore[dict-item]
    with pytest.raises(TypeError, match="dict key"):
        render_markdown_report(_audit(summary=_summary(metrics=(bad_metric,))))
