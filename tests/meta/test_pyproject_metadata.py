from pathlib import Path
from typing import Any
import tomllib


REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

EXPECTED_PROJECT_NAME = "abdp"
EXPECTED_PROJECT_VERSION = "0.3.0"
EXPECTED_PROJECT_DESCRIPTION = "A Python framework for reproducible agent-based decision simulation"
EXPECTED_PROJECT_README = "README.md"
EXPECTED_PROJECT_REQUIRES_PYTHON = ">=3.12"
EXPECTED_PROJECT_LICENSE = {"file": "LICENSE"}
EXPECTED_PROJECT_DEPENDENCIES: list[str] = []

EXPECTED_BUILD_SYSTEM_REQUIRES = ["setuptools>=61"]
EXPECTED_BUILD_BACKEND = "setuptools.build_meta"


def _load_pyproject() -> dict[str, Any]:
    assert PYPROJECT_PATH.is_file()

    with PYPROJECT_PATH.open("rb") as pyproject_file:
        return tomllib.load(pyproject_file)


def test_pyproject_declares_required_project_metadata() -> None:
    project = _load_pyproject()["project"]

    assert project["name"] == EXPECTED_PROJECT_NAME
    assert project["version"] == EXPECTED_PROJECT_VERSION
    assert project["description"] == EXPECTED_PROJECT_DESCRIPTION
    assert project["readme"] == EXPECTED_PROJECT_README
    assert project["requires-python"] == EXPECTED_PROJECT_REQUIRES_PYTHON
    assert project["license"] == EXPECTED_PROJECT_LICENSE
    assert project["dependencies"] == EXPECTED_PROJECT_DEPENDENCIES


def test_pyproject_uses_setuptools_build_backend() -> None:
    build_system = _load_pyproject()["build-system"]

    assert build_system["requires"] == EXPECTED_BUILD_SYSTEM_REQUIRES
    assert build_system["build-backend"] == EXPECTED_BUILD_BACKEND


def test_project_name_matches_src_layout_package_directory() -> None:
    package_root = REPO_ROOT / "src" / EXPECTED_PROJECT_NAME

    assert _load_pyproject()["project"]["name"] == package_root.name
    assert package_root.is_dir()
    assert (package_root / "__init__.py").is_file()


def test_runtime_version_matches_declared_project_version() -> None:
    from abdp import __version__, get_version

    declared_version = _load_pyproject()["project"]["version"]

    assert declared_version == EXPECTED_PROJECT_VERSION
    assert get_version() == declared_version
    assert __version__ == declared_version
