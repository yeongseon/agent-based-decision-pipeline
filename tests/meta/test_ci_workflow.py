from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"

EXPECTED_WORKFLOW_HEADER = "name: ci"

EXPECTED_TRIGGER_BLOCK = "\n".join(
    (
        "on:",
        "  push:",
        "    branches:",
        "      - main",
        "  pull_request:",
        "    branches:",
        "      - main",
    )
)

EXPECTED_PERMISSION_BLOCK = "\n".join(
    (
        "permissions:",
        "  contents: read",
    )
)

EXPECTED_CONCURRENCY_BLOCK = "\n".join(
    (
        "concurrency:",
        "  group: ci-${{ github.workflow }}-${{ github.ref }}",
        "  cancel-in-progress: true",
    )
)

EXPECTED_JOB_BLOCK = "\n".join(
    (
        "jobs:",
        "  ci:",
        "    name: ci",
        "    runs-on: ubuntu-latest",
    )
)

EXPECTED_STEP_BLOCKS = (
    "\n".join(
        (
            "      - name: Checkout repository",
            "        uses: actions/checkout@v4",
        )
    ),
    "\n".join(
        (
            "      - name: Setup Python 3.12",
            "        uses: actions/setup-python@v5",
            "        with:",
            '          python-version: "3.12"',
            '          cache: "pip"',
            "          cache-dependency-path: pyproject.toml",
        )
    ),
    "\n".join(
        (
            "      - name: Install dependencies",
            "        run: python -m pip install -e .[dev]",
        )
    ),
    "\n".join(
        (
            "      - name: Ruff format check",
            "        run: ruff format --check .",
        )
    ),
    "\n".join(
        (
            "      - name: Ruff check",
            "        run: ruff check .",
        )
    ),
    "\n".join(
        (
            "      - name: Mypy strict",
            "        run: mypy --strict --config-file mypy.ini src/abdp tests",
        )
    ),
    "\n".join(
        (
            "      - name: Pytest with coverage",
            "        run: pytest",
        )
    ),
    "\n".join(
        (
            "      - name: Mutmut",
            "        run: mutmut run",
        )
    ),
    "\n".join(
        (
            "      - name: Build package",
            "        run: python -m build",
        )
    ),
)


def test_ci_workflow_file_exists() -> None:
    assert WORKFLOW_PATH.is_file()


def test_ci_workflow_declares_expected_top_level_configuration() -> None:
    assert WORKFLOW_PATH.is_file()
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert EXPECTED_WORKFLOW_HEADER in workflow_text
    assert EXPECTED_TRIGGER_BLOCK in workflow_text
    assert EXPECTED_PERMISSION_BLOCK in workflow_text
    assert EXPECTED_CONCURRENCY_BLOCK in workflow_text
    assert EXPECTED_JOB_BLOCK in workflow_text


def test_ci_workflow_declares_required_steps_in_order() -> None:
    assert WORKFLOW_PATH.is_file()
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")

    start = 0
    for snippet in EXPECTED_STEP_BLOCKS:
        index = workflow_text.find(snippet, start)
        assert index >= 0, snippet
        start = index + len(snippet)
