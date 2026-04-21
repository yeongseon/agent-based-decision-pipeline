from pathlib import Path
from typing import Any
import tomllib


def _load_pyproject() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    pyproject_path = repo_root / "pyproject.toml"

    assert pyproject_path.is_file()

    with pyproject_path.open("rb") as pyproject_file:
        return tomllib.load(pyproject_file)


def test_pyproject_declares_required_project_metadata() -> None:
    project = _load_pyproject()["project"]

    assert project["name"] == "abdp"
    assert project["version"] == "0.1.0.dev0"
    assert project["description"] == "A Python framework for reproducible agent-based decision simulation"
    assert project["readme"] == "README.md"
    assert project["requires-python"] == ">=3.12"
    assert project["license"] == {"file": "LICENSE"}
    assert project["dependencies"] == []


def test_pyproject_uses_setuptools_build_backend() -> None:
    build_system = _load_pyproject()["build-system"]

    assert build_system["requires"] == ["setuptools>=61"]
    assert build_system["build-backend"] == "setuptools.build_meta"


def test_project_name_matches_src_layout_package_directory() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    project = _load_pyproject()["project"]
    package_root = repo_root / "src" / project["name"]

    assert project["name"] == package_root.name
    assert package_root.is_dir()
    assert (package_root / "__init__.py").is_file()
