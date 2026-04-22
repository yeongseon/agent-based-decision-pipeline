"""``abdp run`` subcommand: load a factory, build the audit log, render JSON."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

from abdp.cli.loader import LoaderError, load_audit_log_factory
from abdp.core import Seed, validate_seed
from abdp.evaluation import GateStatus
from abdp.reporting import render_json_report

__all__ = ["parse_seed_arg", "run", "run_command"]

_WARN_STDERR_MESSAGE = "warning: audit completed with WARN status"


def parse_seed_arg(value: str) -> Seed:
    return validate_seed(int(value))


def run(spec: str, *, seed: Seed, output: Path | None = None) -> int:
    try:
        factory = load_audit_log_factory(spec)
        audit = factory(seed)
    except LoaderError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    content = render_json_report(audit)
    _write_output(content, output)
    if audit.summary.overall_status is GateStatus.WARN:
        print(_WARN_STDERR_MESSAGE, file=sys.stderr)
    return _exit_code_for_status(audit.summary.overall_status)


def run_command(args: argparse.Namespace) -> int:
    spec = cast(str, args.spec)
    seed = cast(Seed, args.seed)
    raw_output = cast("Path | None", args.output)
    return run(spec, seed=seed, output=raw_output)


def _write_output(content: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(content)
    else:
        output.write_text(content, encoding="utf-8")


def _exit_code_for_status(status: GateStatus) -> int:
    if status is GateStatus.FAIL:
        return 1
    return 0
