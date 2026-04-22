"""Deterministic Markdown renderer for :class:`abdp.evidence.AuditLog`.

``render_markdown_report`` produces a byte-stable Markdown audit report.
Sections appear in a fixed order (Header, Summary, Metrics, Gates,
Evidence, Claims) with one blank line between them and a trailing
newline at end of document. All scalar values flow through
:mod:`abdp.reporting._normalize` so UTC, NaN, and dict-key invariants
match :func:`abdp.reporting.render_json_report`. Inline JSON inside
table cells and bullet lines uses a compact ``json.dumps`` with sorted
keys. Pipe characters in table cells are escaped as ``\\|`` and raw
newlines in single-line contexts are replaced with ``<br>``.
"""

import json
from collections.abc import Iterable, Sequence
from typing import Any

from abdp.evidence import AuditLog, ClaimRecord, EvidenceRecord
from abdp.evaluation.gate import GateResult
from abdp.evaluation.metric import MetricResult
from abdp.reporting._normalize import to_jsonable

__all__ = ["render_markdown_report"]


def render_markdown_report(audit: AuditLog[Any, Any, Any]) -> str:
    """Render ``audit`` to a deterministic Markdown audit report."""
    if not isinstance(audit, AuditLog):
        raise TypeError(f"render_markdown_report expects AuditLog, got {type(audit).__name__}")
    sections = (
        _section_header(audit),
        _section_summary(audit),
        _section_metrics_table(audit.summary.metrics),
        _section_gates_table(audit.summary.gates),
        _section_evidence_list(audit.evidence),
        _section_claims_list(audit.claims),
    )
    return "\n\n".join(sections) + "\n"


def _section_header(audit: AuditLog[Any, Any, Any]) -> str:
    return (
        "# Audit Report\n"
        "\n"
        f"- Scenario: {audit.scenario_key}\n"
        f"- Seed: {int(audit.seed)}\n"
        f"- Steps: {audit.run.step_count}"
    )


def _section_summary(audit: AuditLog[Any, Any, Any]) -> str:
    summary = audit.summary
    return (
        "## Summary\n"
        "\n"
        f"- Overall status: {summary.overall_status.value}\n"
        f"- Metrics: {len(summary.metrics)}\n"
        f"- Gates: {len(summary.gates)}\n"
        f"- Evidence: {len(audit.evidence)}\n"
        f"- Claims: {len(audit.claims)}"
    )


def _section_metrics_table(metrics: tuple[MetricResult, ...]) -> str:
    return _render_table(
        title="## Metrics",
        headers=("Metric ID", "Value", "Details"),
        rows=((metric.metric_id, _inline_json(metric.value), _inline_json(metric.details)) for metric in metrics),
    )


def _section_gates_table(gates: tuple[GateResult, ...]) -> str:
    return _render_table(
        title="## Gates",
        headers=("Gate ID", "Status", "Reason", "Details"),
        rows=((gate.gate_id, gate.status.value, gate.reason, _inline_json(gate.details)) for gate in gates),
    )


def _section_evidence_list(evidence: tuple[EvidenceRecord, ...]) -> str:
    lines = ["## Evidence", ""]
    for record in evidence:
        created_at = to_jsonable(record.created_at)
        payload = _inline_json(record.payload)
        lines.append(
            f"- {record.evidence_id} [{created_at}] step={record.step_index}"
            f" agent={record.agent_id} key={record.evidence_key} payload={payload}"
        )
    return "\n".join(lines)


def _section_claims_list(claims: tuple[ClaimRecord, ...]) -> str:
    lines = ["## Claims", ""]
    for claim in claims:
        statement = _inline_json(claim.statement)
        evidence_ids = _inline_json(list(claim.evidence_ids))
        metadata = _inline_json(claim.metadata)
        lines.append(
            f"- {claim.claim_id} statement={statement} confidence={claim.confidence}"
            f" evidence={evidence_ids} metadata={metadata}"
        )
    return "\n".join(lines)


def _render_table(*, title: str, headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    lines = [
        title,
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_table_cell(cell) for cell in row) + " |")
    return "\n".join(lines)


def _inline_json(value: Any) -> str:
    return json.dumps(
        to_jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _table_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", "<br>")
