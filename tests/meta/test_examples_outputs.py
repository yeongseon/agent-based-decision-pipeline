from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from abdp.core.types import Seed
from abdp.reporting import render_json_report
from examples.credit_underwriting.audit import build_audit_log as build_credit_audit
from examples.queue_scheduling.audit import build_audit_log as build_queue_audit

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS_DIR = REPO_ROOT / "docs" / "examples" / "outputs"
CREDIT_OUTPUT_PATH = OUTPUTS_DIR / "credit_underwriting_report.json"
QUEUE_OUTPUT_PATH = OUTPUTS_DIR / "queue_scheduling_report.json"

CREDIT_SEED = Seed(7)
QUEUE_SEED = Seed(11)
SELECTED_PROPOSAL_KEY = "selected_proposal"


def _load_committed(path: Path) -> tuple[str, dict[str, Any]]:
    assert path.is_file(), path
    text = path.read_text(encoding="utf-8")
    return text, json.loads(text)


def test_credit_underwriting_frozen_output_matches_fresh_render() -> None:
    committed_text, committed_obj = _load_committed(CREDIT_OUTPUT_PATH)
    fresh_text = render_json_report(build_credit_audit(CREDIT_SEED))

    assert committed_text == fresh_text, (
        "credit_underwriting_report.json is stale; regenerate from build_audit_log(Seed(7))"
    )
    assert committed_obj["scenario_key"] == "credit-underwriting-baseline"
    assert committed_obj["seed"] == int(CREDIT_SEED)


def test_queue_scheduling_frozen_output_matches_fresh_render() -> None:
    committed_text, committed_obj = _load_committed(QUEUE_OUTPUT_PATH)
    fresh_text = render_json_report(build_queue_audit(QUEUE_SEED))

    assert committed_text == fresh_text, (
        "queue_scheduling_report.json is stale; regenerate from build_audit_log(Seed(11))"
    )
    assert committed_obj["scenario_key"] == "latency-baseline"
    assert committed_obj["seed"] == int(QUEUE_SEED)


def test_each_frozen_output_contains_selected_proposal_evidence() -> None:
    for path in (CREDIT_OUTPUT_PATH, QUEUE_OUTPUT_PATH):
        _text, obj = _load_committed(path)
        evidence = obj["evidence"]
        assert isinstance(evidence, list) and evidence, f"{path.name}: evidence must be non-empty"
        keys = {record["evidence_key"] for record in evidence}
        assert SELECTED_PROPOSAL_KEY in keys, f"{path.name}: missing reserved evidence_key {SELECTED_PROPOSAL_KEY!r}"
