"""Tests for ``abdp.cli`` argparse help/skeleton."""

from __future__ import annotations

import subprocess
import sys

import pytest

from abdp.cli.__main__ import main


def test_main_with_no_args_prints_help_and_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "run" in captured.out
    assert "report" in captured.out


def test_main_with_help_flag_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "run" in captured.out
    assert "report" in captured.out


def test_main_run_subcommand_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["run", "--help"])
    assert exc_info.value.code == 0


def test_main_report_subcommand_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["report", "--help"])
    assert exc_info.value.code == 0


def test_main_run_subcommand_returns_two_with_not_implemented_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["run"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "not implemented" in captured.err.lower()


def test_main_report_subcommand_returns_two_with_not_implemented_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["report"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "not implemented" in captured.err.lower()


def test_python_dash_m_abdp_help_exits_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "abdp", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "run" in result.stdout
    assert "report" in result.stdout


def test_python_dash_m_abdp_cli_help_exits_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "abdp.cli", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "run" in result.stdout
    assert "report" in result.stdout
