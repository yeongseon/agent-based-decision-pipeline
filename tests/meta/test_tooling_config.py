import tomllib
from configparser import ConfigParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_ruff_configuration_matches_project_policy() -> None:
    ruff_path = REPO_ROOT / ".ruff.toml"
    assert ruff_path.is_file()
    with ruff_path.open("rb") as config_file:
        ruff_config = tomllib.load(config_file)
    assert ruff_config["target-version"] == "py312"
    assert ruff_config["line-length"] == 120
    assert tuple(ruff_config["lint"]["select"]) == ("E", "F", "W", "UP", "B")
    assert tuple(ruff_config["lint"].get("ignore", [])) == ()
    assert ruff_config["format"]["quote-style"] == "double"
    assert ruff_config["format"]["indent-style"] == "space"
    assert ruff_config["format"]["line-ending"] == "lf"


def test_mypy_configuration_enables_strict_type_checking_for_src_and_tests() -> None:
    mypy_path = REPO_ROOT / "mypy.ini"
    assert mypy_path.is_file()
    mypy_config = ConfigParser(interpolation=None)
    assert mypy_config.read(mypy_path, encoding="utf-8") == [str(mypy_path)]
    assert tuple(mypy_config.sections()) == ("mypy",)
    assert mypy_config["mypy"]["python_version"] == "3.12"
    files_value = mypy_config["mypy"]["files"]
    files_parsed = tuple(
        part.strip() for part in files_value.split(",") if part.strip()
    )
    assert files_parsed == ("src/abdp", "tests")
    assert mypy_config.getboolean("mypy", "strict") is True
    assert mypy_config.getboolean("mypy", "warn_unused_configs") is True


def test_pytest_configuration_enables_strict_collection_and_coverage_defaults() -> None:
    pytest_path = REPO_ROOT / "pytest.ini"
    assert pytest_path.is_file()
    pytest_config = ConfigParser(interpolation=None)
    assert pytest_config.read(pytest_path, encoding="utf-8") == [str(pytest_path)]
    assert tuple(pytest_config.sections()) == ("pytest",)
    assert pytest_config["pytest"]["minversion"] == "9.0"
    assert (
        pytest_config["pytest"]["addopts"]
        == "--cov=src/abdp --cov-branch --cov-report=term-missing"
    )
    testpaths_value = pytest_config["pytest"]["testpaths"]
    testpaths_parsed = tuple(
        line.strip() for line in testpaths_value.splitlines() if line.strip()
    )
    assert testpaths_parsed == ("tests",)
    pythonpath_value = pytest_config["pytest"]["pythonpath"]
    pythonpath_parsed = tuple(
        line.strip() for line in pythonpath_value.splitlines() if line.strip()
    )
    assert pythonpath_parsed == ("src",)
    assert pytest_config.getboolean("pytest", "strict_config") is True
    assert pytest_config.getboolean("pytest", "strict_markers") is True
    assert pytest_config.getboolean("pytest", "xfail_strict") is True
    assert pytest_config["pytest"]["console_output_style"] == "progress"


def test_coverage_configuration_requires_full_branch_coverage_for_package_code() -> (
    None
):
    coverage_path = REPO_ROOT / ".coveragerc"
    assert coverage_path.is_file()
    coverage_config = ConfigParser(interpolation=None)
    assert coverage_config.read(coverage_path, encoding="utf-8") == [str(coverage_path)]
    assert tuple(coverage_config.sections()) == ("run", "report")
    assert coverage_config.getboolean("run", "branch") is True
    source_value = coverage_config["run"]["source"]
    source_parsed = tuple(
        line.strip() for line in source_value.splitlines() if line.strip()
    )
    assert source_parsed == ("src/abdp",)
    assert coverage_config.getint("report", "fail_under") == 100
    assert coverage_config.getboolean("report", "show_missing") is True
    assert coverage_config.getboolean("report", "skip_covered") is True
    exclude_value = coverage_config["report"]["exclude_lines"]
    exclude_parsed = tuple(
        line.strip() for line in exclude_value.splitlines() if line.strip()
    )
    assert exclude_parsed == (
        "pragma: no cover",
        'if __name__ == "__main__":',
        "if TYPE_CHECKING:",
    )


def test_pyproject_dev_extras_include_required_tooling_dependencies() -> None:
    pyproject_path = REPO_ROOT / "pyproject.toml"
    assert pyproject_path.is_file()
    with pyproject_path.open("rb") as config_file:
        project = tomllib.load(config_file)["project"]
    assert project["dependencies"] == []
    assert set(project["optional-dependencies"]) == {"dev"}
    assert tuple(project["optional-dependencies"]["dev"]) == (
        "build>=1.0.0",
        "hypothesis>=6.0.0",
        "mutmut>=3.0.0",
        "mypy>=1.20.1",
        "pytest>=9.0.3",
        "pytest-cov>=7.1.0",
        "ruff>=0.15.11",
    )
