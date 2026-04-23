"""Argparse entrypoint for the ``abdp`` CLI.

Wires the ``run``, ``report``, and ``inspect`` subcommands to their
respective modules. ``main`` is the console-script entry point referenced
by ``[project.scripts] abdp`` in ``pyproject.toml``.
"""

import argparse
from collections.abc import Sequence
from pathlib import Path

from abdp.cli.inspect import inspect_command
from abdp.cli.report import REPORT_FORMATS, report_command
from abdp.cli.run import parse_seed_arg, run_command

__all__ = ["build_parser", "main"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="abdp",
        description="Agent-based decision pipeline CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="{run,report,inspect}")
    run_parser = subparsers.add_parser("run", help="Run a scenario and emit an AuditLog.")
    run_parser.add_argument("spec", help="module.path:callable spec.")
    run_parser.add_argument(
        "--seed",
        required=True,
        type=parse_seed_arg,
        metavar="N",
        help="Non-negative integer seed (uint32).",
    )
    run_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        metavar="FILE",
        help="Write the JSON report to FILE instead of stdout.",
    )
    report_parser = subparsers.add_parser("report", help="Render a report from a saved AuditLog.")
    report_parser.add_argument("path", type=Path, help="Path to a serialized AuditLog JSON file.")
    report_parser.add_argument(
        "--format",
        required=True,
        choices=REPORT_FORMATS,
        help="Output format.",
    )
    report_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        metavar="FILE",
        help="Write the report to FILE instead of stdout.",
    )
    inspect_parser = subparsers.add_parser("inspect", help="Query a SQLite trace store and emit JSON Lines.")
    inspect_parser.add_argument("run_id", help="Run identifier to query.")
    inspect_parser.add_argument(
        "--db",
        required=True,
        type=Path,
        metavar="PATH",
        help="Path to a SQLite trace database.",
    )
    inspect_parser.add_argument(
        "--step",
        type=int,
        default=None,
        metavar="N",
        help="Only emit events whose step_index equals N.",
    )
    inspect_parser.add_argument(
        "--event-type",
        dest="event_type",
        type=str,
        default=None,
        metavar="TYPE",
        help="Only emit events whose event_type equals TYPE.",
    )
    inspect_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        metavar="FILE",
        help="Write JSON Lines to FILE instead of stdout.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "run":
        return run_command(args)
    if args.command == "inspect":
        return inspect_command(args)
    return report_command(args)


if __name__ == "__main__":
    raise SystemExit(main())
