"""Tests for ``abdp.cli.inspect`` subcommand."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

from abdp.cli.__main__ import main
from abdp.core import Seed
from abdp.inspector import (
    SQLiteTraceStore,
    TraceRecorder,
)


def _populate(db_path: Path, *, seed: Seed = Seed(42), run_id: str = "run-x") -> None:
    store = SQLiteTraceStore(db_path)
    recorder = TraceRecorder(store=store, seed=seed, run_id=run_id)
    recorder.record(event_type="step.begin", step_index=0, attributes={"scenario_key": "demo"})
    recorder.record(
        event_type="decision.evaluate",
        step_index=0,
        attributes={"agent_id": "agent-a", "proposals": 1},
    )
    recorder.record(event_type="step.end", step_index=0, attributes={"proposals": 1, "decisions": 1})
    recorder.record(event_type="step.begin", step_index=1, attributes={"scenario_key": "demo"})
    recorder.record(event_type="step.end", step_index=1, attributes={"proposals": 0, "decisions": 0})
    store.close()


def _decode_lines(blob: bytes) -> list[dict[str, object]]:
    text = blob.decode("utf-8")
    if not text:
        return []
    return [json.loads(line) for line in text.splitlines()]


def test_inspect_emits_jsonl_for_all_events_in_run(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    db = tmp_path / "trace.db"
    _populate(db)

    exit_code = main(["inspect", "run-x", "--db", str(db)])
    captured = capsysbinary.readouterr()

    assert exit_code == 0
    rows = _decode_lines(captured.out)
    assert [r["event_type"] for r in rows] == [
        "step.begin",
        "decision.evaluate",
        "step.end",
        "step.begin",
        "step.end",
    ]
    assert [r["seq"] for r in rows] == [0, 1, 2, 3, 4]
    for row in rows:
        UUID(str(row["event_id"]))
        assert row["run_id"] == "run-x"
        assert row["parent_event_id"] is None


def test_inspect_filters_by_step(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    db = tmp_path / "trace.db"
    _populate(db)

    exit_code = main(["inspect", "run-x", "--db", str(db), "--step", "1"])
    captured = capsysbinary.readouterr()

    assert exit_code == 0
    rows = _decode_lines(captured.out)
    assert [r["seq"] for r in rows] == [3, 4]
    assert all(r["step_index"] == 1 for r in rows)


def test_inspect_filters_by_event_type(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    db = tmp_path / "trace.db"
    _populate(db)

    exit_code = main(["inspect", "run-x", "--db", str(db), "--event-type", "step.begin"])
    captured = capsysbinary.readouterr()

    assert exit_code == 0
    rows = _decode_lines(captured.out)
    assert [r["seq"] for r in rows] == [0, 3]
    assert all(r["event_type"] == "step.begin" for r in rows)


def test_inspect_combined_filters(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    db = tmp_path / "trace.db"
    _populate(db)

    exit_code = main(["inspect", "run-x", "--db", str(db), "--step", "0", "--event-type", "decision.evaluate"])
    captured = capsysbinary.readouterr()

    assert exit_code == 0
    rows = _decode_lines(captured.out)
    assert len(rows) == 1
    assert rows[0]["seq"] == 1
    assert rows[0]["attributes"] == {"agent_id": "agent-a", "proposals": 1}


def test_inspect_unknown_run_id_emits_no_lines_and_exits_zero(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    db = tmp_path / "trace.db"
    _populate(db)

    exit_code = main(["inspect", "missing-run", "--db", str(db)])
    captured = capsysbinary.readouterr()

    assert exit_code == 0
    assert captured.out == b""


def test_inspect_writes_to_output_file_byte_equal(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    db = tmp_path / "trace.db"
    _populate(db)
    out_file = tmp_path / "trace.jsonl"

    exit_code = main(["inspect", "run-x", "--db", str(db), "--output", str(out_file)])
    captured = capsysbinary.readouterr()

    assert exit_code == 0
    assert captured.out == b""

    file_rows = _decode_lines(out_file.read_bytes())
    assert [r["seq"] for r in file_rows] == [0, 1, 2, 3, 4]


def test_inspect_output_matches_stdout_byte_for_byte(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    db = tmp_path / "trace.db"
    _populate(db)
    out_file = tmp_path / "trace.jsonl"

    file_exit = main(["inspect", "run-x", "--db", str(db), "--output", str(out_file)])
    capsysbinary.readouterr()
    stdout_exit = main(["inspect", "run-x", "--db", str(db)])
    captured = capsysbinary.readouterr()

    assert file_exit == 0
    assert stdout_exit == 0
    assert out_file.read_bytes() == captured.out


def test_inspect_missing_db_exits_two(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    missing = tmp_path / "absent.db"
    exit_code = main(["inspect", "run-x", "--db", str(missing)])
    captured = capsysbinary.readouterr()

    assert exit_code == 2
    assert captured.out == b""
    assert captured.err != b""
    assert captured.err.count(b"\n") == 1


def test_inspect_corrupt_db_exits_two(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    bad = tmp_path / "corrupt.db"
    bad.write_bytes(b"not a sqlite database at all")
    exit_code = main(["inspect", "run-x", "--db", str(bad)])
    captured = capsysbinary.readouterr()

    assert exit_code == 2
    assert captured.out == b""
    assert captured.err != b""


def test_inspect_invalid_step_exits_argparse_two() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["inspect", "run-x", "--db", "x.db", "--step", "not-int"])
    assert exc_info.value.code == 2


def test_inspect_negative_step_exits_two(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    db = tmp_path / "trace.db"
    _populate(db)
    exit_code = main(["inspect", "run-x", "--db", str(db), "--step", "-1"])
    captured = capsysbinary.readouterr()

    assert exit_code == 2
    assert captured.out == b""
    assert captured.err != b""


def test_inspect_missing_run_id_exits_argparse_two() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["inspect", "--db", "x.db"])
    assert exc_info.value.code == 2


def test_inspect_missing_db_flag_exits_argparse_two() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["inspect", "run-x"])
    assert exc_info.value.code == 2


def test_inspect_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["inspect", "--help"])
    assert exc_info.value.code == 0


def test_inspect_output_to_missing_parent_directory_exits_two(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    db = tmp_path / "trace.db"
    _populate(db)
    bad_output = tmp_path / "no" / "such" / "dir" / "out.jsonl"

    exit_code = main(["inspect", "run-x", "--db", str(db), "--output", str(bad_output)])
    captured = capsysbinary.readouterr()

    assert exit_code == 2
    assert captured.out == b""
    assert captured.err != b""
    assert not bad_output.exists()


def test_inspect_falls_back_to_text_write_when_stdout_has_no_buffer(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import io
    import sys as _sys

    db = tmp_path / "trace.db"
    _populate(db)

    text_only = io.StringIO()
    monkeypatch.setattr(_sys, "stdout", text_only)
    exit_code = main(["inspect", "run-x", "--db", str(db)])
    capsys.readouterr()

    assert exit_code == 0
    assert text_only.getvalue() != ""
    rows = _decode_lines(text_only.getvalue().encode("utf-8"))
    assert [r["seq"] for r in rows] == [0, 1, 2, 3, 4]


def test_inspect_jsonl_payload_round_trips_attributes_with_uuid_parent(
    tmp_path: Path,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    db = tmp_path / "trace.db"
    store = SQLiteTraceStore(db)
    recorder = TraceRecorder(store=store, seed=Seed(7), run_id="run-y")
    parent = recorder.record(event_type="step.begin", step_index=0, attributes={"scenario_key": "demo"})
    recorder.record(
        event_type="decision.evaluate",
        step_index=0,
        attributes={"agent_id": "a1", "proposals": 2, "ratio": 0.5, "ok": True},
        parent_event_id=parent.event_id,
    )
    store.close()

    exit_code = main(["inspect", "run-y", "--db", str(db)])
    captured = capsysbinary.readouterr()
    rows = _decode_lines(captured.out)

    assert exit_code == 0
    assert rows[0]["parent_event_id"] is None
    assert rows[1]["parent_event_id"] == str(parent.event_id)
    assert rows[1]["attributes"] == {
        "agent_id": "a1",
        "proposals": 2,
        "ratio": 0.5,
        "ok": True,
    }
