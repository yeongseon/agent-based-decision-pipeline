"""Coverage tests for ``abdp.cli.report`` reconstruction validators."""

from __future__ import annotations

import json
from pathlib import Path

from typing import cast

import pytest

from abdp.cli.__main__ import main
from abdp.cli.report import ReportError, _audit_log_from_jsonable
from abdp.core import Seed
from abdp.reporting import render_json_report
from tests.cli._fixtures import build_audit_log


def _baseline_payload() -> dict[str, object]:
    audit = build_audit_log(Seed(0))
    return cast(dict[str, object], json.loads(render_json_report(audit)))


def _set(payload: dict[str, object], path: list[str], value: object) -> dict[str, object]:
    cursor: object = payload
    for key in path[:-1]:
        assert isinstance(cursor, dict)
        cursor = cursor[key]
    assert isinstance(cursor, dict)
    cursor[path[-1]] = value
    return payload


def _write(tmp_path: Path, payload: dict[str, object]) -> Path:
    out = tmp_path / "audit.json"
    out.write_bytes(json.dumps(payload).encode("utf-8"))
    return out


def test_audit_log_must_be_object() -> None:
    with pytest.raises(ReportError, match="audit log must be an object"):
        _audit_log_from_jsonable(["not", "an", "object"])


def test_missing_required_field_raises() -> None:
    with pytest.raises(ReportError, match="missing required field 'scenario_key'"):
        _audit_log_from_jsonable({})


def test_invalid_seed_type_raises() -> None:
    payload = _baseline_payload()
    _set(payload, ["seed"], "not-an-int")
    with pytest.raises(ReportError, match="seed.*must be an int seed"):
        _audit_log_from_jsonable(payload)


def test_invalid_seed_value_raises() -> None:
    payload = _baseline_payload()
    _set(payload, ["seed"], -1)
    _set(payload, ["run", "seed"], -1)
    with pytest.raises(ReportError, match="not a valid seed"):
        _audit_log_from_jsonable(payload)


def test_audit_log_post_init_mismatch_wrapped() -> None:
    payload = _baseline_payload()
    _set(payload, ["scenario_key"], "different")
    with pytest.raises(ReportError, match="invalid audit log"):
        _audit_log_from_jsonable(payload)


def test_step_index_must_be_int() -> None:
    payload = _baseline_payload()
    _set(payload, ["run", "final_state", "step_index"], "zero")
    with pytest.raises(ReportError, match="simulation state.step_index must be int"):
        _audit_log_from_jsonable(payload)


def test_invalid_snapshot_tier_raises() -> None:
    payload = _baseline_payload()
    _set(payload, ["run", "final_state", "snapshot_ref", "tier"], "platinum")
    with pytest.raises(ReportError, match="snapshot_ref.tier"):
        _audit_log_from_jsonable(payload)


def test_invalid_overall_status_raises() -> None:
    payload = _baseline_payload()
    _set(payload, ["summary", "overall_status"], "unknown")
    with pytest.raises(ReportError, match="summary.overall_status"):
        _audit_log_from_jsonable(payload)


def test_invalid_gate_status_raises() -> None:
    payload = _baseline_payload()
    payload_summary = payload["summary"]
    assert isinstance(payload_summary, dict)
    payload_summary["gates"] = [
        {"gate_id": "g1", "status": "yikes", "reason": "x", "details": {}},
    ]
    with pytest.raises(ReportError, match="gate.status"):
        _audit_log_from_jsonable(payload)


def test_evidence_step_index_must_be_int() -> None:
    payload = _baseline_payload()
    payload["evidence"] = [
        {
            "evidence_id": "11111111-1111-1111-1111-111111111111",
            "evidence_key": "k",
            "step_index": "zero",
            "agent_id": "a",
            "payload": {},
            "created_at": "2026-04-01T00:00:00+00:00",
        }
    ]
    with pytest.raises(ReportError, match="evidence.step_index must be int"):
        _audit_log_from_jsonable(payload)


def test_claim_confidence_must_be_number() -> None:
    payload = _baseline_payload()
    payload["claims"] = [
        {
            "claim_id": "11111111-1111-1111-1111-111111111111",
            "statement": "s",
            "evidence_ids": ["22222222-2222-2222-2222-222222222222"],
            "confidence": "high",
            "metadata": {},
        }
    ]
    with pytest.raises(ReportError, match="claim.confidence"):
        _audit_log_from_jsonable(payload)


def test_string_field_type_validation() -> None:
    payload = _baseline_payload()
    _set(payload, ["scenario_key"], 42)
    with pytest.raises(ReportError, match="scenario_key.*must be a string"):
        _audit_log_from_jsonable(payload)


def test_list_field_type_validation() -> None:
    payload = _baseline_payload()
    _set(payload, ["evidence"], "not-a-list")
    with pytest.raises(ReportError, match="evidence.*must be a list"):
        _audit_log_from_jsonable(payload)


def test_object_field_type_validation() -> None:
    payload = _baseline_payload()
    payload_summary = payload["summary"]
    assert isinstance(payload_summary, dict)
    payload_summary["metrics"] = [{"metric_id": "m", "value": 1, "details": "not-object"}]
    with pytest.raises(ReportError, match="details.*must be an object"):
        _audit_log_from_jsonable(payload)


def test_uuid_must_be_string() -> None:
    payload = _baseline_payload()
    payload["evidence"] = [
        {
            "evidence_id": 42,
            "evidence_key": "k",
            "step_index": 0,
            "agent_id": "a",
            "payload": {},
            "created_at": "2026-04-01T00:00:00+00:00",
        }
    ]
    with pytest.raises(ReportError, match="evidence_id must be a UUID string"):
        _audit_log_from_jsonable(payload)


def test_uuid_invalid_string_raises() -> None:
    payload = _baseline_payload()
    payload["evidence"] = [
        {
            "evidence_id": "not-a-uuid",
            "evidence_key": "k",
            "step_index": 0,
            "agent_id": "a",
            "payload": {},
            "created_at": "2026-04-01T00:00:00+00:00",
        }
    ]
    with pytest.raises(ReportError, match="evidence_id is not a valid UUID"):
        _audit_log_from_jsonable(payload)


def test_datetime_must_be_string() -> None:
    payload = _baseline_payload()
    payload["evidence"] = [
        {
            "evidence_id": "11111111-1111-1111-1111-111111111111",
            "evidence_key": "k",
            "step_index": 0,
            "agent_id": "a",
            "payload": {},
            "created_at": 0,
        }
    ]
    with pytest.raises(ReportError, match="created_at must be an ISO 8601 string"):
        _audit_log_from_jsonable(payload)


def test_datetime_invalid_string_raises() -> None:
    payload = _baseline_payload()
    payload["evidence"] = [
        {
            "evidence_id": "11111111-1111-1111-1111-111111111111",
            "evidence_key": "k",
            "step_index": 0,
            "agent_id": "a",
            "payload": {},
            "created_at": "yesterday",
        }
    ]
    with pytest.raises(ReportError, match="created_at is not a valid"):
        _audit_log_from_jsonable(payload)


def test_segment_carrier_satisfies_protocol(tmp_path: Path) -> None:
    payload = _baseline_payload()
    final_state = payload["run"]
    assert isinstance(final_state, dict)
    fs = final_state["final_state"]
    assert isinstance(fs, dict)
    fs["segments"] = [{"segment_id": "s1", "participant_ids": ["p1", "p2"]}]
    fs["participants"] = [{"participant_id": "p1"}]
    fs["pending_actions"] = [{"proposal_id": "pr", "actor_id": "a", "action_key": "k", "payload": {}}]
    final_state["steps"] = [
        {
            "state": fs,
            "decisions": [
                {
                    "agent_id": "agent",
                    "proposals": [{"proposal_id": "pr", "actor_id": "a", "action_key": "k", "payload": {}}],
                }
            ],
            "proposals": [{"proposal_id": "pr", "actor_id": "a", "action_key": "k", "payload": {}}],
        }
    ]

    src = _write(tmp_path, payload)
    out = tmp_path / "out.json"
    exit_code = main(["report", str(src), "--format", "json", "--output", str(out)])
    assert exit_code == 0
    assert out.exists()
    rebuilt = json.loads(out.read_bytes())
    assert isinstance(rebuilt, dict)
    rebuilt_run = rebuilt["run"]
    assert isinstance(rebuilt_run, dict)
    assert len(rebuilt_run["steps"]) == 1


def test_participant_id_must_be_string() -> None:
    payload = _baseline_payload()
    final_state = payload["run"]
    assert isinstance(final_state, dict)
    fs = final_state["final_state"]
    assert isinstance(fs, dict)
    fs["segments"] = [{"segment_id": "s", "participant_ids": [42]}]
    with pytest.raises(ReportError, match="participant_ids.*must be a string"):
        _audit_log_from_jsonable(payload)
