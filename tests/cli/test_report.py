"""Tests for ``abdp.cli.report`` subcommand."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest

from abdp.cli.__main__ import main
from abdp.core import Seed
from abdp.evaluation import EvaluationSummary, GateResult, GateStatus, MetricResult
from abdp.evidence import AuditLog, ClaimRecord, EvidenceRecord
from abdp.reporting import render_json_report, render_markdown_report
from abdp.scenario import ScenarioRun, ScenarioStep
from abdp.simulation import (
    ActionProposal,
    ParticipantState,
    SegmentState,
    SimulationState,
)
from abdp.simulation.snapshot_ref import SnapshotRef
from tests.cli._fixtures import build_audit_log


_UUID_A = UUID("11111111-1111-1111-1111-111111111111")
_UUID_B = UUID("22222222-2222-2222-2222-222222222222")
_UUID_C = UUID("33333333-3333-3333-3333-333333333333")


def _rich_audit_log(seed: Seed) -> AuditLog[Any, Any, Any]:
    snapshot = SnapshotRef(snapshot_id=_UUID_A, tier="silver", storage_key="snap/key")
    state = SimulationState[SegmentState, ParticipantState, ActionProposal](
        step_index=0,
        seed=seed,
        snapshot_ref=snapshot,
        segments=(),
        participants=(),
        pending_actions=(),
    )
    step = ScenarioStep[SegmentState, ParticipantState, ActionProposal](
        state=state,
        decisions=(),
        proposals=(),
    )
    run = ScenarioRun[SegmentState, ParticipantState, ActionProposal](
        scenario_key="rich-✓",
        seed=seed,
        steps=(step, step),
        final_state=state,
    )
    metrics = (
        MetricResult(metric_id="m1", value=1, details={"k": "v"}),
        MetricResult(metric_id="m2", value=2.5, details={}),
    )
    gates = (
        GateResult(gate_id="g1", status=GateStatus.PASS, reason="ok", details={}),
        GateResult(gate_id="g2", status=GateStatus.WARN, reason="meh", details={"x": 1}),
    )
    summary = EvaluationSummary(metrics=metrics, gates=gates, overall_status=GateStatus.WARN)
    evidence = (
        EvidenceRecord(
            evidence_id=_UUID_B,
            evidence_key="ek",
            step_index=0,
            agent_id="agent-1",
            payload={"data": [1, 2, 3]},
            created_at=datetime(2026, 4, 1, 12, 0, tzinfo=UTC),
        ),
    )
    claims = (
        ClaimRecord(
            claim_id=_UUID_C,
            statement="claim-✓",
            evidence_ids=(_UUID_B,),
            confidence=0.75,
            metadata={"k": "v"},
        ),
    )
    return AuditLog[SegmentState, ParticipantState, ActionProposal](
        scenario_key="rich-✓",
        seed=seed,
        run=run,
        summary=summary,
        evidence=evidence,
        claims=claims,
    )


def build_rich_audit_log(seed: Seed) -> AuditLog[Any, Any, Any]:
    return _rich_audit_log(seed)


def _write_json(audit: AuditLog[Any, Any, Any], path: Path) -> None:
    path.write_bytes(render_json_report(audit).encode("utf-8"))


def test_report_json_round_trip_is_byte_identical(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    audit = build_rich_audit_log(Seed(42))
    src = tmp_path / "in.json"
    _write_json(audit, src)
    expected = src.read_bytes()

    exit_code = main(["report", str(src), "--format", "json"])
    captured = capsysbinary.readouterr()

    assert exit_code == 0
    assert captured.out == expected


def test_report_markdown_matches_direct_renderer_call(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    audit = build_rich_audit_log(Seed(7))
    src = tmp_path / "in.json"
    _write_json(audit, src)
    expected = render_markdown_report(audit).encode("utf-8")

    exit_code = main(["report", str(src), "--format", "markdown"])
    captured = capsysbinary.readouterr()

    assert exit_code == 0
    assert captured.out == expected


def test_report_with_output_writes_file_byte_equal(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    audit = build_rich_audit_log(Seed(0))
    src = tmp_path / "in.json"
    _write_json(audit, src)
    out = tmp_path / "out.json"

    exit_code = main(["report", str(src), "--format", "json", "--output", str(out)])
    captured = capsysbinary.readouterr()

    assert exit_code == 0
    assert captured.out == b""
    assert out.read_bytes() == src.read_bytes()


def test_report_markdown_with_output_writes_file_byte_equal(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    audit = build_rich_audit_log(Seed(1))
    src = tmp_path / "in.json"
    _write_json(audit, src)
    out = tmp_path / "out.md"

    exit_code = main(["report", str(src), "--format", "markdown", "--output", str(out)])
    captured = capsysbinary.readouterr()

    assert exit_code == 0
    assert captured.out == b""
    assert out.read_bytes() == render_markdown_report(audit).encode("utf-8")


@pytest.mark.parametrize("status", [GateStatus.PASS, GateStatus.WARN, GateStatus.FAIL])
def test_report_returns_zero_regardless_of_overall_status(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
    status: GateStatus,
) -> None:
    audit = build_audit_log(Seed(0))
    src = tmp_path / "in.json"
    payload = json.loads(render_json_report(audit))
    payload["summary"]["overall_status"] = status.value
    src.write_bytes(json.dumps(payload).encode("utf-8"))

    exit_code = main(["report", str(src), "--format", "json"])
    capsysbinary.readouterr()
    assert exit_code == 0


def test_report_missing_file_exits_two(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    missing = tmp_path / "nope.json"
    exit_code = main(["report", str(missing), "--format", "json"])
    captured = capsysbinary.readouterr()
    assert exit_code == 2
    assert captured.out == b""
    assert captured.err != b""


def test_report_invalid_json_exits_two(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    src = tmp_path / "bad.json"
    src.write_text("not json {", encoding="utf-8")
    exit_code = main(["report", str(src), "--format", "json"])
    captured = capsysbinary.readouterr()
    assert exit_code == 2
    assert captured.out == b""
    assert captured.err != b""


def test_report_invalid_audit_shape_exits_two(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    src = tmp_path / "shape.json"
    src.write_bytes(b'{"scenario_key": "x"}')
    exit_code = main(["report", str(src), "--format", "markdown"])
    captured = capsysbinary.readouterr()
    assert exit_code == 2
    assert captured.out == b""
    assert captured.err != b""


def test_report_missing_format_exits_argparse_two() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["report", "any.json"])
    assert exc_info.value.code == 2


def test_report_missing_path_exits_argparse_two() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["report", "--format", "json"])
    assert exc_info.value.code == 2


def test_report_invalid_format_exits_argparse_two() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["report", "any.json", "--format", "yaml"])
    assert exc_info.value.code == 2


def test_report_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["report", "--help"])
    assert exc_info.value.code == 0


def test_report_output_to_missing_parent_directory_exits_two(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    audit = build_rich_audit_log(Seed(0))
    src = tmp_path / "in.json"
    _write_json(audit, src)
    bad_output = tmp_path / "does" / "not" / "exist" / "out.json"

    exit_code = main(["report", str(src), "--format", "json", "--output", str(bad_output)])
    captured = capsysbinary.readouterr()

    assert exit_code == 2
    assert captured.out == b""
    assert captured.err != b""
    assert captured.err.count(b"\n") == 1
    assert not bad_output.exists()


def test_report_falls_back_to_text_write_when_stdout_has_no_buffer(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import io
    import sys

    audit = build_rich_audit_log(Seed(0))
    src = tmp_path / "in.json"
    _write_json(audit, src)

    text_only = io.StringIO()
    monkeypatch.setattr(sys, "stdout", text_only)
    exit_code = main(["report", str(src), "--format", "json"])
    capsys.readouterr()

    assert exit_code == 0
    assert text_only.getvalue() == render_json_report(audit)
