"""Shared assertion helpers for audit-flow integration tests (#125).

Three invariants are identical across every domain audit flow: selected
proposal coverage per decision step, byte-for-byte determinism for a
fixed seed, and CLI parity with the public ``render_json_report`` surface.
Domain-specific scenario keys, loader specs, and payload schemas remain
local to each test module.
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from abdp.core.types import Seed
from abdp.evidence import AuditLog, EvidenceRecord
from abdp.reporting import render_json_report

REPO_ROOT = Path(__file__).resolve().parents[2]
SELECTED_PROPOSAL_KEY = "selected_proposal"


def assert_selected_proposal_per_decision_step(audit: AuditLog[Any, Any, Any]) -> tuple[EvidenceRecord, ...]:
    decision_step_indices = tuple(step.state.step_index for step in audit.run.steps if step.proposals)
    selected_records = tuple(record for record in audit.evidence if record.evidence_key == SELECTED_PROPOSAL_KEY)
    assert len(selected_records) == len(decision_step_indices)
    assert tuple(record.step_index for record in selected_records) == decision_step_indices
    return selected_records


def assert_audit_is_deterministic(
    factory: Callable[[Seed], AuditLog[Any, Any, Any]],
    seed: Seed,
) -> None:
    assert factory(seed) == factory(seed)


def assert_cli_run_matches_direct_render(
    factory: Callable[[Seed], AuditLog[Any, Any, Any]],
    loader_spec: str,
    seed: Seed,
) -> None:
    expected = render_json_report(factory(seed)).encode("utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "abdp", "run", loader_spec, "--seed", str(int(seed))],
        capture_output=True,
        check=False,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    assert result.stdout == expected
