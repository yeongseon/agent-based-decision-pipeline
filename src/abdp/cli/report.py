"""``abdp report`` subcommand: load a serialized AuditLog, render JSON or Markdown.

The reconstructor rebuilds an :class:`abdp.evidence.AuditLog` instance from
the JSON representation produced by :func:`abdp.reporting.render_json_report`.
Protocol-typed fields (``decisions``, ``proposals``, ``segments``,
``participants``, ``pending_actions``) are rehydrated into private frozen
dataclass carriers that satisfy the corresponding ``runtime_checkable``
``Protocol`` shapes; this guarantees that
:func:`abdp.reporting.render_markdown_report` and
:func:`abdp.reporting.render_json_report` produce byte-identical output for
the reconstructed audit. The subcommand always returns ``0`` on success
regardless of ``summary.overall_status``; loader, parse, and shape errors
return ``2`` with a single-line stderr message.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Final, Literal, cast
from uuid import UUID

from abdp.agents import AgentDecision
from abdp.core import Seed, validate_seed
from abdp.core.types import JsonObject, JsonValue
from abdp.data.snapshot_manifest import SnapshotTier
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

__all__ = ["ReportError", "ReportFormat", "REPORT_FORMATS", "report", "report_command"]

ReportFormat = Literal["json", "markdown"]
REPORT_FORMATS: Final[tuple[ReportFormat, ...]] = ("json", "markdown")

_EXIT_OK = 0
_EXIT_ERROR = 2


class ReportError(Exception):
    """Raised when a serialized audit cannot be parsed or reconstructed."""


def report(path: Path, *, format: ReportFormat, output: Path | None = None) -> int:
    try:
        text = path.read_text(encoding="utf-8")
        loaded = json.loads(text)
        audit = _audit_log_from_jsonable(loaded)
        if format == "json":
            rendered = render_json_report(audit)
        else:
            rendered = render_markdown_report(audit)
        _write_output(rendered, output)
    except (OSError, json.JSONDecodeError, ReportError) as exc:
        print(str(exc).splitlines()[0] if str(exc) else type(exc).__name__, file=sys.stderr)
        return _EXIT_ERROR
    return _EXIT_OK


def report_command(args: argparse.Namespace) -> int:
    return report(
        cast(Path, args.path),
        format=cast(ReportFormat, args.format),
        output=cast("Path | None", args.output),
    )


def _write_output(content: str, output: Path | None) -> None:
    encoded = content.encode("utf-8")
    if output is None:
        buffer = getattr(sys.stdout, "buffer", None)
        if buffer is None:
            sys.stdout.write(content)
        else:
            buffer.write(encoded)
    else:
        output.write_bytes(encoded)


@dataclass(frozen=True, slots=True)
class _SegmentCarrier:
    segment_id: str
    participant_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _ParticipantCarrier:
    participant_id: str


@dataclass(frozen=True, slots=True)
class _ActionProposalCarrier:
    proposal_id: str
    actor_id: str
    action_key: str
    payload: JsonValue


@dataclass(frozen=True, slots=True)
class _AgentDecisionCarrier:
    agent_id: str
    proposals: tuple[_ActionProposalCarrier, ...]


def _audit_log_from_jsonable(data: Any) -> AuditLog[Any, Any, Any]:
    obj = _require_object(data, "audit log")
    scenario_key = _require_str(obj, "scenario_key")
    seed = _require_seed(obj, "seed")
    try:
        return AuditLog[SegmentState, ParticipantState, ActionProposal](
            scenario_key=scenario_key,
            seed=seed,
            run=_scenario_run_from_jsonable(_require_field(obj, "run")),
            summary=_evaluation_summary_from_jsonable(_require_field(obj, "summary")),
            evidence=tuple(_evidence_record_from_jsonable(item) for item in _require_list(obj, "evidence")),
            claims=tuple(_claim_record_from_jsonable(item) for item in _require_list(obj, "claims")),
        )
    except (TypeError, ValueError) as exc:
        raise ReportError(f"invalid audit log: {exc}") from exc


def _scenario_run_from_jsonable(
    data: Any,
) -> ScenarioRun[SegmentState, ParticipantState, ActionProposal]:
    obj = _require_object(data, "run")
    return ScenarioRun[SegmentState, ParticipantState, ActionProposal](
        scenario_key=_require_str(obj, "scenario_key"),
        seed=_require_seed(obj, "seed"),
        steps=tuple(_scenario_step_from_jsonable(item) for item in _require_list(obj, "steps")),
        final_state=_simulation_state_from_jsonable(_require_field(obj, "final_state")),
    )


def _scenario_step_from_jsonable(
    data: Any,
) -> ScenarioStep[SegmentState, ParticipantState, ActionProposal]:
    obj = _require_object(data, "step")
    return ScenarioStep[SegmentState, ParticipantState, ActionProposal](
        state=_simulation_state_from_jsonable(_require_field(obj, "state")),
        decisions=cast(
            "tuple[AgentDecision[ActionProposal], ...]",
            tuple(_agent_decision_from_jsonable(item) for item in _require_list(obj, "decisions")),
        ),
        proposals=cast(
            "tuple[ActionProposal, ...]",
            tuple(_action_proposal_from_jsonable(item) for item in _require_list(obj, "proposals")),
        ),
    )


def _simulation_state_from_jsonable(
    data: Any,
) -> SimulationState[SegmentState, ParticipantState, ActionProposal]:
    obj = _require_object(data, "simulation state")
    return SimulationState[SegmentState, ParticipantState, ActionProposal](
        step_index=_require_int(obj, "step_index", "simulation state.step_index"),
        seed=_require_seed(obj, "seed"),
        snapshot_ref=_snapshot_ref_from_jsonable(_require_field(obj, "snapshot_ref")),
        segments=cast(
            "tuple[SegmentState, ...]",
            tuple(_segment_from_jsonable(item) for item in _require_list(obj, "segments")),
        ),
        participants=cast(
            "tuple[ParticipantState, ...]",
            tuple(_participant_from_jsonable(item) for item in _require_list(obj, "participants")),
        ),
        pending_actions=cast(
            "tuple[ActionProposal, ...]",
            tuple(_action_proposal_from_jsonable(item) for item in _require_list(obj, "pending_actions")),
        ),
    )


def _snapshot_ref_from_jsonable(data: Any) -> SnapshotRef:
    obj = _require_object(data, "snapshot_ref")
    tier = _require_str(obj, "tier")
    if tier not in ("bronze", "silver", "gold"):
        raise ReportError(f"snapshot_ref.tier must be bronze/silver/gold, got {tier!r}")
    return SnapshotRef(
        snapshot_id=_require_uuid(obj, "snapshot_id"),
        tier=cast(SnapshotTier, tier),
        storage_key=_require_str(obj, "storage_key"),
    )


def _evaluation_summary_from_jsonable(data: Any) -> EvaluationSummary:
    obj = _require_object(data, "summary")
    overall = _require_str(obj, "overall_status")
    try:
        status = GateStatus(overall)
    except ValueError as exc:
        raise ReportError(f"summary.overall_status must be a valid GateStatus: {overall!r}") from exc
    return EvaluationSummary(
        metrics=tuple(_metric_result_from_jsonable(item) for item in _require_list(obj, "metrics")),
        gates=tuple(_gate_result_from_jsonable(item) for item in _require_list(obj, "gates")),
        overall_status=status,
    )


def _metric_result_from_jsonable(data: Any) -> MetricResult:
    obj = _require_object(data, "metric")
    return MetricResult(
        metric_id=_require_str(obj, "metric_id"),
        value=cast(JsonValue, _require_field(obj, "value")),
        details=_require_object_field(obj, "details"),
    )


def _gate_result_from_jsonable(data: Any) -> GateResult:
    obj = _require_object(data, "gate")
    status_raw = _require_str(obj, "status")
    try:
        status = GateStatus(status_raw)
    except ValueError as exc:
        raise ReportError(f"gate.status must be a valid GateStatus: {status_raw!r}") from exc
    return GateResult(
        gate_id=_require_str(obj, "gate_id"),
        status=status,
        reason=_require_str(obj, "reason"),
        details=_require_object_field(obj, "details"),
    )


def _evidence_record_from_jsonable(data: Any) -> EvidenceRecord:
    obj = _require_object(data, "evidence")
    return EvidenceRecord(
        evidence_id=_require_uuid(obj, "evidence_id"),
        evidence_key=_require_str(obj, "evidence_key"),
        step_index=_require_int(obj, "step_index", "evidence.step_index"),
        agent_id=_require_str(obj, "agent_id"),
        payload=cast(JsonValue, _require_field(obj, "payload")),
        created_at=_require_datetime(obj, "created_at"),
    )


def _claim_record_from_jsonable(data: Any) -> ClaimRecord:
    obj = _require_object(data, "claim")
    confidence_raw = _require_field(obj, "confidence")
    if isinstance(confidence_raw, bool) or not isinstance(confidence_raw, (int, float)):
        raise ReportError("claim.confidence must be a number")
    return ClaimRecord(
        claim_id=_require_uuid(obj, "claim_id"),
        statement=_require_str(obj, "statement"),
        evidence_ids=tuple(_uuid_from_jsonable(item, "evidence_ids[]") for item in _require_list(obj, "evidence_ids")),
        confidence=float(confidence_raw),
        metadata=_require_object_field(obj, "metadata"),
    )


def _segment_from_jsonable(data: Any) -> _SegmentCarrier:
    obj = _require_object(data, "segment")
    participant_ids_raw = _require_list(obj, "participant_ids")
    return _SegmentCarrier(
        segment_id=_require_str(obj, "segment_id"),
        participant_ids=tuple(_require_str_value(item, "participant_ids[]") for item in participant_ids_raw),
    )


def _participant_from_jsonable(data: Any) -> _ParticipantCarrier:
    obj = _require_object(data, "participant")
    return _ParticipantCarrier(participant_id=_require_str(obj, "participant_id"))


def _action_proposal_from_jsonable(data: Any) -> _ActionProposalCarrier:
    obj = _require_object(data, "action proposal")
    return _ActionProposalCarrier(
        proposal_id=_require_str(obj, "proposal_id"),
        actor_id=_require_str(obj, "actor_id"),
        action_key=_require_str(obj, "action_key"),
        payload=cast(JsonValue, _require_field(obj, "payload")),
    )


def _agent_decision_from_jsonable(data: Any) -> _AgentDecisionCarrier:
    obj = _require_object(data, "agent decision")
    return _AgentDecisionCarrier(
        agent_id=_require_str(obj, "agent_id"),
        proposals=tuple(_action_proposal_from_jsonable(item) for item in _require_list(obj, "proposals")),
    )


def _require_object(data: Any, label: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ReportError(f"{label} must be an object")
    return cast(dict[str, Any], data)


def _require_field(obj: dict[str, Any], name: str) -> Any:
    if name not in obj:
        raise ReportError(f"missing required field {name!r}")
    return obj[name]


def _require_str(obj: dict[str, Any], name: str) -> str:
    value = _require_field(obj, name)
    if not isinstance(value, str):
        raise ReportError(f"field {name!r} must be a string")
    return value


def _require_str_value(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise ReportError(f"{label} must be a string")
    return value


def _require_list(obj: dict[str, Any], name: str) -> list[Any]:
    value = _require_field(obj, name)
    if not isinstance(value, list):
        raise ReportError(f"field {name!r} must be a list")
    return value


def _require_object_field(obj: dict[str, Any], name: str) -> JsonObject:
    value = _require_field(obj, name)
    if not isinstance(value, dict):
        raise ReportError(f"field {name!r} must be an object")
    return cast(JsonObject, value)


def _require_seed(obj: dict[str, Any], name: str) -> Seed:
    value = _require_field(obj, name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ReportError(f"field {name!r} must be an int seed")
    try:
        return validate_seed(value)
    except (TypeError, ValueError) as exc:
        raise ReportError(f"field {name!r} is not a valid seed: {exc}") from exc


def _require_int(obj: dict[str, Any], name: str, label: str) -> int:
    value = _require_field(obj, name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ReportError(f"{label} must be int")
    return int(value)


def _require_uuid(obj: dict[str, Any], name: str) -> UUID:
    return _uuid_from_jsonable(_require_field(obj, name), name)


def _require_datetime(obj: dict[str, Any], name: str) -> datetime:
    return _datetime_from_jsonable(_require_field(obj, name), name)


def _uuid_from_jsonable(value: Any, label: str) -> UUID:
    if not isinstance(value, str):
        raise ReportError(f"{label} must be a UUID string")
    try:
        return UUID(value)
    except ValueError as exc:
        raise ReportError(f"{label} is not a valid UUID: {value!r}") from exc


def _datetime_from_jsonable(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise ReportError(f"{label} must be an ISO 8601 string")
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ReportError(f"{label} is not a valid ISO 8601 datetime: {value!r}") from exc
