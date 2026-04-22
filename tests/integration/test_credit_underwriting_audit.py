"""Integration test for the credit underwriting audit factory (#124).

Verifies that ``examples.credit_underwriting.audit.build_audit_log`` produces
a deterministic ``AuditLog`` whose evidence contains the reserved
``selected_proposal`` key for every decision step, whose evaluation summary
passes its gates, and whose JSON/Markdown reports round-trip cleanly through
both the public renderers and the ``abdp`` CLI subcommands.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from abdp.core.types import Seed
from abdp.evaluation import EvaluationSummary, GateStatus
from abdp.evidence import AuditLog, EvidenceRecord
from abdp.reporting import render_json_report, render_markdown_report

from examples.credit_underwriting.audit import (
    _DECISION_STEP_METRIC_ID,
    _SELECTED_EVIDENCE_METRIC_ID,
    build_audit_log,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SEED = Seed(7)
SCENARIO_KEY = "credit-underwriting-baseline"
SELECTED_PROPOSAL_KEY = "selected_proposal"
LOADER_SPEC = "examples.credit_underwriting.audit:build_audit_log"


def test_build_audit_log_returns_audit_log_with_matching_seed_and_key() -> None:
    audit = build_audit_log(SEED)
    assert isinstance(audit, AuditLog)
    assert audit.scenario_key == SCENARIO_KEY
    assert audit.seed == SEED
    assert audit.run.scenario_key == SCENARIO_KEY
    assert audit.run.seed == SEED


def test_build_audit_log_emits_one_selected_proposal_per_decision_step() -> None:
    audit = build_audit_log(SEED)
    decision_step_indices = tuple(step.state.step_index for step in audit.run.steps if step.proposals)
    selected_records = tuple(record for record in audit.evidence if record.evidence_key == SELECTED_PROPOSAL_KEY)
    assert len(selected_records) == len(decision_step_indices)
    assert tuple(record.step_index for record in selected_records) == decision_step_indices
    for record, step in zip(
        selected_records,
        (step for step in audit.run.steps if step.proposals),
        strict=True,
    ):
        assert isinstance(record, EvidenceRecord)
        first = step.proposals[0]
        assert record.agent_id == first.actor_id
        assert isinstance(record.payload, dict)
        assert record.payload["proposal_id"] == first.proposal_id
        assert record.payload["actor_id"] == first.actor_id
        assert record.payload["action_key"] == first.action_key


def test_build_audit_log_evidence_ids_are_unique() -> None:
    audit = build_audit_log(SEED)
    ids = [record.evidence_id for record in audit.evidence]
    assert len(ids) == len(set(ids))


def test_build_audit_log_summary_passes_gates() -> None:
    audit = build_audit_log(SEED)
    assert isinstance(audit.summary, EvaluationSummary)
    assert audit.summary.gates
    assert audit.summary.overall_status is GateStatus.PASS


def test_decision_step_metric_is_derived_from_run_independently_of_evidence() -> None:
    audit = build_audit_log(SEED)
    metric_values = {m.metric_id: m.value for m in audit.summary.metrics}
    expected_decision_steps = sum(1 for step in audit.run.steps if step.proposals)
    assert metric_values[_DECISION_STEP_METRIC_ID] == expected_decision_steps
    assert metric_values[_SELECTED_EVIDENCE_METRIC_ID] == sum(
        1 for record in audit.evidence if record.evidence_key == "selected_proposal"
    )
    assert metric_values[_DECISION_STEP_METRIC_ID] == metric_values[_SELECTED_EVIDENCE_METRIC_ID]


def test_build_audit_log_is_deterministic_for_fixed_seed() -> None:
    assert build_audit_log(SEED) == build_audit_log(SEED)


def test_build_audit_log_renders_markdown_without_error() -> None:
    rendered = render_markdown_report(build_audit_log(SEED))
    assert isinstance(rendered, str)
    assert rendered
    assert SCENARIO_KEY in rendered
    assert SELECTED_PROPOSAL_KEY in rendered


def test_cli_run_stdout_matches_direct_render() -> None:
    expected = render_json_report(build_audit_log(SEED)).encode("utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "abdp",
            "run",
            LOADER_SPEC,
            "--seed",
            str(int(SEED)),
        ],
        capture_output=True,
        check=False,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    assert result.stdout == expected
