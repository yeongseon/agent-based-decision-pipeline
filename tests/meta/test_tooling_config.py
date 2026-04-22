from configparser import ConfigParser
from pathlib import Path
from typing import Any
import tomllib

REPO_ROOT = Path(__file__).resolve().parents[2]
RUFF_PATH = REPO_ROOT / ".ruff.toml"
MYPY_PATH = REPO_ROOT / "mypy.ini"
PYTEST_PATH = REPO_ROOT / "pytest.ini"
COVERAGE_PATH = REPO_ROOT / ".coveragerc"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

EXPECTED_RUFF_TARGET_VERSION = "py312"
EXPECTED_RUFF_LINE_LENGTH = 120
EXPECTED_RUFF_SELECT = ("E", "F", "W", "UP", "B")
EXPECTED_RUFF_IGNORE: tuple[str, ...] = ()
EXPECTED_RUFF_QUOTE_STYLE = "double"
EXPECTED_RUFF_INDENT_STYLE = "space"
EXPECTED_RUFF_LINE_ENDING = "lf"

EXPECTED_MYPY_SECTIONS = ("mypy",)
EXPECTED_MYPY_PYTHON_VERSION = "3.12"
EXPECTED_MYPY_FILES = ("src/abdp", "tests")

EXPECTED_PYTEST_SECTIONS = ("pytest",)
EXPECTED_PYTEST_MINVERSION = "9.0"
EXPECTED_PYTEST_ADDOPTS = "--cov=src/abdp --cov-branch --cov-report=term-missing"
EXPECTED_PYTEST_TESTPATHS = ("tests",)
EXPECTED_PYTEST_PYTHONPATH = ("src", ".")
EXPECTED_PYTEST_CONSOLE_OUTPUT_STYLE = "progress"

EXPECTED_COVERAGE_SECTIONS = ("run", "report")
EXPECTED_COVERAGE_SOURCE = ("src/abdp",)
EXPECTED_COVERAGE_EXCLUDE_LINES = (
    "pragma: no cover",
    'if __name__ == "__main__":',
    "if TYPE_CHECKING:",
    r"^\s*\.\.\.\s*$",
)
EXPECTED_COVERAGE_PARTIAL_BRANCHES = (
    "pragma: no branch",
    r"^\s*(?:async\s+def|def)\b.*:\s*\.\.\.\s*$",
)

EXPECTED_RUNTIME_DEPENDENCIES: list[str] = []
EXPECTED_OPTIONAL_DEPENDENCY_GROUPS = {"dev"}
EXPECTED_DEV_DEPENDENCIES = (
    "build>=1.0.0",
    "hypothesis>=6.0.0",
    "mutmut>=3.0.0",
    "mypy>=1.20.1",
    "pytest>=9.0.3",
    "pytest-cov>=7.1.0",
    "ruff>=0.15.11",
)


def _load_toml(path: Path) -> dict[str, Any]:
    assert path.is_file(), path

    with path.open("rb") as config_file:
        return tomllib.load(config_file)


def _load_ini(path: Path) -> ConfigParser:
    assert path.is_file(), path

    config = ConfigParser(interpolation=None)
    read_files = config.read(path, encoding="utf-8")

    assert read_files == [str(path)]

    return config


def _split_csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _split_lines(value: str) -> tuple[str, ...]:
    return tuple(line.strip() for line in value.splitlines() if line.strip())


def test_ruff_configuration_matches_project_policy() -> None:
    ruff_config = _load_toml(RUFF_PATH)

    assert ruff_config["target-version"] == EXPECTED_RUFF_TARGET_VERSION
    assert ruff_config["line-length"] == EXPECTED_RUFF_LINE_LENGTH
    assert tuple(ruff_config["lint"]["select"]) == EXPECTED_RUFF_SELECT
    assert tuple(ruff_config["lint"].get("ignore", [])) == EXPECTED_RUFF_IGNORE
    assert ruff_config["format"]["quote-style"] == EXPECTED_RUFF_QUOTE_STYLE
    assert ruff_config["format"]["indent-style"] == EXPECTED_RUFF_INDENT_STYLE
    assert ruff_config["format"]["line-ending"] == EXPECTED_RUFF_LINE_ENDING


def test_mypy_configuration_enables_strict_type_checking_for_src_and_tests() -> None:
    mypy_config = _load_ini(MYPY_PATH)

    assert tuple(mypy_config.sections()) == EXPECTED_MYPY_SECTIONS
    assert mypy_config["mypy"]["python_version"] == EXPECTED_MYPY_PYTHON_VERSION
    assert _split_csv(mypy_config["mypy"]["files"]) == EXPECTED_MYPY_FILES
    assert mypy_config.getboolean("mypy", "strict") is True
    assert mypy_config.getboolean("mypy", "warn_unused_configs") is True


def test_pytest_configuration_enables_strict_collection_and_coverage_defaults() -> None:
    pytest_config = _load_ini(PYTEST_PATH)

    assert tuple(pytest_config.sections()) == EXPECTED_PYTEST_SECTIONS
    assert pytest_config["pytest"]["minversion"] == EXPECTED_PYTEST_MINVERSION
    assert pytest_config["pytest"]["addopts"] == EXPECTED_PYTEST_ADDOPTS
    assert _split_lines(pytest_config["pytest"]["testpaths"]) == EXPECTED_PYTEST_TESTPATHS
    assert _split_lines(pytest_config["pytest"]["pythonpath"]) == EXPECTED_PYTEST_PYTHONPATH
    assert pytest_config.getboolean("pytest", "strict_config") is True
    assert pytest_config.getboolean("pytest", "strict_markers") is True
    assert pytest_config.getboolean("pytest", "xfail_strict") is True
    assert pytest_config["pytest"]["console_output_style"] == EXPECTED_PYTEST_CONSOLE_OUTPUT_STYLE


def test_coverage_configuration_requires_full_branch_coverage_for_package_code() -> None:
    coverage_config = _load_ini(COVERAGE_PATH)

    assert tuple(coverage_config.sections()) == EXPECTED_COVERAGE_SECTIONS
    assert coverage_config.getboolean("run", "branch") is True
    assert _split_lines(coverage_config["run"]["source"]) == EXPECTED_COVERAGE_SOURCE
    assert coverage_config.getint("report", "fail_under") == 100
    assert coverage_config.getboolean("report", "show_missing") is True
    assert coverage_config.getboolean("report", "skip_covered") is True
    assert _split_lines(coverage_config["report"]["exclude_lines"]) == EXPECTED_COVERAGE_EXCLUDE_LINES
    assert _split_lines(coverage_config["report"]["partial_branches"]) == EXPECTED_COVERAGE_PARTIAL_BRANCHES


def test_pyproject_dev_extras_include_required_tooling_dependencies() -> None:
    project = _load_toml(PYPROJECT_PATH)["project"]

    assert project["dependencies"] == EXPECTED_RUNTIME_DEPENDENCIES
    assert set(project["optional-dependencies"]) == EXPECTED_OPTIONAL_DEPENDENCY_GROUPS
    assert tuple(project["optional-dependencies"]["dev"]) == EXPECTED_DEV_DEPENDENCIES
