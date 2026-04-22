"""Tests for ``abdp.cli.run`` subcommand."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import pytest

from abdp.cli.__main__ import main
from abdp.reporting import render_json_report
from tests.cli._fixtures import (
    build_audit_log,
    build_fail_audit_log,
    build_warn_audit_log,
)

PASS_SPEC = "tests.cli._fixtures:build_audit_log"
WARN_SPEC = "tests.cli._fixtures:build_warn_audit_log"
FAIL_SPEC = "tests.cli._fixtures:build_fail_audit_log"
NOT_AUDIT_SPEC = "tests.cli._fixtures:build_not_audit_log"
UNICODE_SPEC = "tests.cli._fixtures:build_unicode_audit_log"


def test_run_pass_writes_json_report_to_stdout_with_exit_zero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["run", PASS_SPEC, "--seed", "0"])
    captured = capsys.readouterr()
    expected = render_json_report(build_audit_log(__import__("abdp.core", fromlist=["Seed"]).Seed(0)))
    assert exit_code == 0
    assert captured.out == expected
    assert captured.err == ""


def test_run_warn_exits_zero_and_emits_stderr_warning(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["run", WARN_SPEC, "--seed", "1"])
    captured = capsys.readouterr()
    from abdp.core import Seed

    expected = render_json_report(build_warn_audit_log(Seed(1)))
    assert exit_code == 0
    assert captured.out == expected
    assert "warning" in captured.err.lower()
    assert "warn" in captured.err.lower()


def test_run_fail_exits_one_without_stderr_warning(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["run", FAIL_SPEC, "--seed", "2"])
    captured = capsys.readouterr()
    from abdp.core import Seed

    expected = render_json_report(build_fail_audit_log(Seed(2)))
    assert exit_code == 1
    assert captured.out == expected
    assert captured.err == ""


def test_run_with_output_writes_file_byte_equal_to_stdout(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "report.json"
    exit_code = main(["run", PASS_SPEC, "--seed", "0", "--output", str(output)])
    captured = capsys.readouterr()
    from abdp.core import Seed

    expected = render_json_report(build_audit_log(Seed(0)))
    assert exit_code == 0
    assert captured.out == ""
    assert output.read_text(encoding="utf-8") == expected


def test_run_with_output_for_warn_writes_file_and_emits_stderr(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "warn.json"
    exit_code = main(["run", WARN_SPEC, "--seed", "0", "--output", str(output)])
    captured = capsys.readouterr()
    from abdp.core import Seed

    expected = render_json_report(build_warn_audit_log(Seed(0)))
    assert exit_code == 0
    assert captured.out == ""
    assert output.read_text(encoding="utf-8") == expected
    assert "warning" in captured.err.lower()


def test_run_with_malformed_spec_returns_two_with_stderr_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["run", "no-colon-spec", "--seed", "0"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert "no-colon-spec" in captured.err or "loader" in captured.err.lower()


def test_run_with_non_audit_factory_returns_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["run", NOT_AUDIT_SPEC, "--seed", "0"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert captured.err != ""


def test_run_missing_seed_exits_argparse_two() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["run", PASS_SPEC])
    assert exc_info.value.code == 2


def test_run_missing_spec_exits_argparse_two() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["run", "--seed", "0"])
    assert exc_info.value.code == 2


def test_run_negative_seed_exits_argparse_two() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["run", PASS_SPEC, "--seed", "-1"])
    assert exc_info.value.code == 2


def test_run_seed_zero_is_accepted(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["run", PASS_SPEC, "--seed", "0"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out != ""


def test_python_dash_m_abdp_run_pass_writes_stdout(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "abdp", "run", PASS_SPEC, "--seed", "7"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(Path(__file__).resolve().parents[2]),
    )
    assert result.returncode == 0
    assert result.stdout != ""
    assert "scenario_key" in result.stdout


def test_run_help_lists_seed_and_output_flags() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["run", "--help"])
    assert exc_info.value.code == 0


def test_run_unicode_stdout_bytes_match_file_bytes_exact_utf8(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    output = tmp_path / "unicode.json"
    file_exit = main(["run", UNICODE_SPEC, "--seed", "0", "--output", str(output)])
    file_bytes = output.read_bytes()
    capsysbinary.readouterr()

    stdout_exit = main(["run", UNICODE_SPEC, "--seed", "0"])
    captured = capsysbinary.readouterr()

    from abdp.core import Seed
    from tests.cli._fixtures import build_unicode_audit_log

    expected = render_json_report(build_unicode_audit_log(Seed(0))).encode("utf-8")
    assert file_exit == 0
    assert stdout_exit == 0
    assert file_bytes == expected
    assert captured.out == expected
    assert captured.out == file_bytes
    assert b"\xed\x95\x9c" in captured.out


def test_run_falls_back_to_text_write_when_stdout_has_no_buffer(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import io

    text_only = io.StringIO()
    monkeypatch.setattr(sys, "stdout", text_only)
    exit_code = main(["run", PASS_SPEC, "--seed", "0"])
    capsys.readouterr()

    from abdp.core import Seed

    expected = render_json_report(build_audit_log(Seed(0)))
    assert exit_code == 0
    assert text_only.getvalue() == expected
