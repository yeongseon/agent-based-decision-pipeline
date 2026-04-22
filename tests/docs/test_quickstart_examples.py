"""Verification of the modeling quickstart guide."""

from __future__ import annotations

import re
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
QUICKSTART_PATH = REPO_ROOT / "docs" / "quickstart.md"
README_PATH = REPO_ROOT / "README.md"
ROADMAP_PATH = REPO_ROOT / "docs" / "roadmap.md"

REQUIRED_SECTIONS: tuple[str, ...] = (
    "## Install",
    "## Domain types",
    "## Agent",
    "## Resolver",
    "## ScenarioSpec",
    "## Run",
    "## Inspect",
)

PYTHON_BLOCK_PATTERN = re.compile(r"```python\n(.*?)```", re.DOTALL)


def _read_python_blocks() -> list[str]:
    body = QUICKSTART_PATH.read_text(encoding="utf-8")
    return PYTHON_BLOCK_PATTERN.findall(body)


def test_quickstart_file_exists_and_is_non_empty() -> None:
    assert QUICKSTART_PATH.is_file()
    assert QUICKSTART_PATH.read_text(encoding="utf-8").strip()


def test_quickstart_contains_all_required_sections_in_order() -> None:
    body = QUICKSTART_PATH.read_text(encoding="utf-8")
    positions = [body.find(section) for section in REQUIRED_SECTIONS]
    assert all(pos >= 0 for pos in positions), dict(zip(REQUIRED_SECTIONS, positions, strict=True))
    assert positions == sorted(positions)


def test_quickstart_python_blocks_compile() -> None:
    blocks = _read_python_blocks()
    assert blocks, "expected at least one ```python``` block"
    for index, source in enumerate(blocks):
        compile(source, f"<quickstart-block-{index}>", "exec")


def test_quickstart_python_blocks_execute_end_to_end() -> None:
    program = "\n".join(_read_python_blocks())
    module_name = "_abdp_quickstart_exec"
    module = types.ModuleType(module_name)
    sys.modules[module_name] = module
    try:
        exec(compile(program, "<quickstart>", "exec"), module.__dict__)
        run = module.__dict__["run"]
        assert run.scenario_key == "quickstart-baseline"
        assert int(run.seed) == 7
        assert run.step_count == 2
    finally:
        sys.modules.pop(module_name, None)


def test_readme_links_to_quickstart() -> None:
    assert "docs/quickstart.md" in README_PATH.read_text(encoding="utf-8")


def test_roadmap_links_to_quickstart() -> None:
    assert "quickstart.md" in ROADMAP_PATH.read_text(encoding="utf-8")


def test_quickstart_references_credit_underwriting_example() -> None:
    body = QUICKSTART_PATH.read_text(encoding="utf-8")
    assert "examples.credit_underwriting" in body or "examples/credit_underwriting" in body


def test_quickstart_referenced_example_runs() -> None:
    from examples.credit_underwriting.__main__ import main

    main()
