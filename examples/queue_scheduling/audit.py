"""Audit factory wiring the queue scheduling example into a full ``AuditLog`` (#125).

``build_audit_log`` runs the queue scheduling scenario via the public
``ScenarioRunner`` surface, captures one ``selected_proposal`` evidence
record for every non-empty proposal step, and folds a minimal pair of
metric/gate computations into an :class:`abdp.evidence.AuditLog`. All
timestamps derive from a fixed UTC epoch plus the step index, keeping
every audit deterministic for a given seed.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final, cast

from abdp.core.types import JsonValue, Seed
from abdp.evaluation import (
    Gate,
    GateResult,
    GateStatus,
    Metric,
    MetricResult,
    aggregate_results,
    evaluate_gates,
    evaluate_metrics,
)
from abdp.evidence import AuditLog, EvidenceRecord, make_evidence_record
from abdp.scenario import ScenarioRun, ScenarioRunner

from examples.queue_scheduling.agents import QueueWorkerAgent
from examples.queue_scheduling.domain import QueueProposal, QueueScenario, Slot, Worker
from examples.queue_scheduling.resolver import QueueResolver

__all__ = ["build_audit_log"]

SELECTED_PROPOSAL_KEY: Final = "selected_proposal"
_EPOCH: Final = datetime(2026, 1, 1, tzinfo=UTC)
_MAX_STEPS: Final = 3
_SCENARIO_KEY: Final = "latency-baseline"
_DECISION_STEP_METRIC_ID: Final = "decision_step_count"
_SELECTED_EVIDENCE_METRIC_ID: Final = "selected_proposal_evidence_count"
_TERMINAL_PENDING_METRIC_ID: Final = "terminal_pending_action_count"
_COVERAGE_GATE_ID: Final = "selected_proposal_coverage"
_TERMINAL_PENDING_GATE_ID: Final = "terminal_pending_drained"

_QueueRun = ScenarioRun[Slot, Worker, QueueProposal]
_QueueAudit = AuditLog[Slot, Worker, QueueProposal]


def build_audit_log(seed: Seed) -> _QueueAudit:
    run = _build_runner().run(QueueScenario(scenario_key=_SCENARIO_KEY, seed=seed))
    evidence = _emit_selected_proposal_evidence(run, seed)
    metrics = evaluate_metrics(_build_metrics(evidence), run)
    gates = evaluate_gates(_build_gates(), metrics)
    summary = aggregate_results(metrics, gates)
    return AuditLog[Slot, Worker, QueueProposal](
        scenario_key=run.scenario_key,
        seed=run.seed,
        run=run,
        summary=summary,
        evidence=evidence,
        claims=(),
    )


def _build_runner() -> ScenarioRunner[Slot, Worker, QueueProposal]:
    return ScenarioRunner[Slot, Worker, QueueProposal](
        agents=(
            QueueWorkerAgent(agent_id="worker-fast", queue_id="expedite"),
            QueueWorkerAgent(agent_id="worker-flex", queue_id="standard"),
        ),
        resolver=QueueResolver(),
        max_steps=_MAX_STEPS,
    )


def _emit_selected_proposal_evidence(run: _QueueRun, seed: Seed) -> tuple[EvidenceRecord, ...]:
    return tuple(
        make_evidence_record(
            seed=seed,
            evidence_key=SELECTED_PROPOSAL_KEY,
            step_index=step.state.step_index,
            agent_id=step.proposals[0].actor_id,
            payload=_proposal_payload(step.proposals[0]),
            created_at=_EPOCH + timedelta(seconds=step.state.step_index),
        )
        for step in run.steps
        if step.proposals
    )


def _proposal_payload(proposal: QueueProposal) -> JsonValue:
    return {
        "proposal_id": proposal.proposal_id,
        "actor_id": proposal.actor_id,
        "action_key": proposal.action_key,
        "payload": proposal.payload,
    }


@dataclass(frozen=True)
class _DecisionStepMetric:
    metric_id: str = _DECISION_STEP_METRIC_ID

    def evaluate(self, run: _QueueRun) -> MetricResult:
        value = sum(1 for step in run.steps if step.proposals)
        return MetricResult(metric_id=self.metric_id, value=value, details={})


@dataclass(frozen=True)
class _SelectedEvidenceMetric:
    value: int
    metric_id: str = _SELECTED_EVIDENCE_METRIC_ID

    def evaluate(self, run: _QueueRun) -> MetricResult:
        return MetricResult(metric_id=self.metric_id, value=self.value, details={})


@dataclass(frozen=True)
class _PendingActionMetric:
    metric_id: str = _TERMINAL_PENDING_METRIC_ID

    def evaluate(self, run: _QueueRun) -> MetricResult:
        return MetricResult(
            metric_id=self.metric_id,
            value=len(run.final_state.pending_actions),
            details={},
        )


@dataclass(frozen=True)
class _CoverageGate:
    gate_id: str = _COVERAGE_GATE_ID

    def evaluate(self, metrics: Iterable[MetricResult]) -> GateResult:
        decision = _int_metric(metrics, _DECISION_STEP_METRIC_ID)
        selected = _int_metric(metrics, _SELECTED_EVIDENCE_METRIC_ID)
        passed = decision is not None and selected is not None and decision == selected and decision > 0
        return GateResult(
            gate_id=self.gate_id,
            status=GateStatus.PASS if passed else GateStatus.FAIL,
            reason=(
                "selected_proposal evidence covers every decision step"
                if passed
                else "selected_proposal evidence does not cover all decision steps"
            ),
            details={"decision_steps": decision, "selected_evidence": selected},
        )


@dataclass(frozen=True)
class _TerminalPendingGate:
    gate_id: str = _TERMINAL_PENDING_GATE_ID

    def evaluate(self, metrics: Iterable[MetricResult]) -> GateResult:
        pending = _int_metric(metrics, _TERMINAL_PENDING_METRIC_ID)
        passed = pending == 0
        return GateResult(
            gate_id=self.gate_id,
            status=GateStatus.PASS if passed else GateStatus.FAIL,
            reason=(
                "terminal state has no pending actions" if passed else "terminal state still carries pending actions"
            ),
            details={"terminal_pending_actions": pending},
        )


def _int_metric(metrics: Iterable[MetricResult], metric_id: str) -> int | None:
    for metric in metrics:
        if metric.metric_id == metric_id and isinstance(metric.value, int):
            return metric.value
    return None


def _build_metrics(
    evidence: tuple[EvidenceRecord, ...],
) -> tuple[Metric[_QueueRun], ...]:
    selected_count = sum(1 for record in evidence if record.evidence_key == SELECTED_PROPOSAL_KEY)
    return cast(
        "tuple[Metric[_QueueRun], ...]",
        (
            _DecisionStepMetric(),
            _SelectedEvidenceMetric(value=selected_count),
            _PendingActionMetric(),
        ),
    )


def _build_gates() -> tuple[Gate, ...]:
    return cast("tuple[Gate, ...]", (_CoverageGate(), _TerminalPendingGate()))
