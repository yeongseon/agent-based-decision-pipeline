"""Test fixtures for ``abdp.cli`` loader tests."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from abdp.core import Seed
from abdp.evaluation import EvaluationSummary, GateStatus
from abdp.evidence import AuditLog
from abdp.scenario import ScenarioRun
from abdp.simulation import ActionProposal, ParticipantState, SegmentState, SimulationState
from abdp.simulation.snapshot_ref import SnapshotRef


NOT_CALLABLE: int = 42


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


def _build(seed: Seed, status: GateStatus) -> AuditLog[Any, Any, Any]:
    run = ScenarioRun[SegmentState, ParticipantState, ActionProposal](
        scenario_key="cli-fixture",
        seed=seed,
        steps=(),
        final_state=_state(),
    )
    summary = EvaluationSummary(metrics=(), gates=(), overall_status=status)
    return AuditLog[SegmentState, ParticipantState, ActionProposal](
        scenario_key="cli-fixture",
        seed=seed,
        run=run,
        summary=summary,
        evidence=(),
        claims=(),
    )


def build_audit_log(seed: Seed) -> AuditLog[Any, Any, Any]:
    return _build(seed, GateStatus.PASS)


def build_warn_audit_log(seed: Seed) -> AuditLog[Any, Any, Any]:
    return _build(seed, GateStatus.WARN)


def build_fail_audit_log(seed: Seed) -> AuditLog[Any, Any, Any]:
    return _build(seed, GateStatus.FAIL)


def build_unicode_audit_log(seed: Seed) -> AuditLog[Any, Any, Any]:
    run = ScenarioRun[SegmentState, ParticipantState, ActionProposal](
        scenario_key="한글-시나리오-✓",
        seed=seed,
        steps=(),
        final_state=_state(),
    )
    summary = EvaluationSummary(metrics=(), gates=(), overall_status=GateStatus.PASS)
    return AuditLog[SegmentState, ParticipantState, ActionProposal](
        scenario_key="한글-시나리오-✓",
        seed=seed,
        run=run,
        summary=summary,
        evidence=(),
        claims=(),
    )


def build_not_audit_log(seed: Seed) -> object:
    _ = seed
    return {"not": "audit"}


def _created_at() -> datetime:
    return datetime(2026, 1, 1, tzinfo=UTC)
