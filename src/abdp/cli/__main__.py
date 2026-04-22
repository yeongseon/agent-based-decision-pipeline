"""Argparse entrypoint for the ``abdp`` CLI.

Provides ``run`` and ``report`` subcommands as stubs returning exit code
2 with a 'not implemented' stderr message; subsequent issues fill the
subcommand bodies. ``main`` is the console-script entry point referenced
by ``[project.scripts] abdp`` in ``pyproject.toml``.
"""

import argparse
import sys
from collections.abc import Sequence

__all__ = ["build_parser", "main"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="abdp",
        description="Agent-based decision pipeline CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="{run,report}")
    run_parser = subparsers.add_parser("run", help="Run a scenario and emit an AuditLog.")
    run_parser.add_argument("spec", nargs="?", help="module.path:callable spec.")
    report_parser = subparsers.add_parser("report", help="Render a report from a saved AuditLog.")
    report_parser.add_argument("path", nargs="?", help="Path to a serialized AuditLog.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    print(f"abdp {args.command}: not implemented yet.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
