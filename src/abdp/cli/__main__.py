"""Argparse entrypoint for the ``abdp`` CLI.

Wires the ``run`` and ``report`` subcommands to :mod:`abdp.cli.run` and
:mod:`abdp.cli.report`. ``main`` is the console-script entry point
referenced by ``[project.scripts] abdp`` in ``pyproject.toml``.
"""

import argparse
from collections.abc import Sequence
from pathlib import Path

from abdp.cli.report import REPORT_FORMATS, report_command
from abdp.cli.run import parse_seed_arg, run_command

__all__ = ["build_parser", "main"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="abdp",
        description="Agent-based decision pipeline CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="{run,report}")
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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "run":
        return run_command(args)
    return report_command(args)


if __name__ == "__main__":
    raise SystemExit(main())
