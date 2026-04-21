from importlib import import_module
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_readme_contains_only_project_name_and_tagline() -> None:
    readme = REPO_ROOT / "README.md"

    assert readme.is_file()
    assert readme.read_text(encoding="utf-8").strip() == (
        "# agent-based-decision-pipeline\n\n" "A Python framework for reproducible agent-based decision simulation"
    )


def test_required_scaffold_files_exist() -> None:
    assert (REPO_ROOT / "src/abdp/__init__.py").is_file()
    assert (REPO_ROOT / "src/abdp/core/__init__.py").is_file()
    assert (REPO_ROOT / "src/abdp/data/__init__.py").is_file()
    assert (REPO_ROOT / "src/abdp/simulation/__init__.py").is_file()
    assert (REPO_ROOT / "src/abdp/py.typed").is_file()


def test_package_imports_succeed_and_module_docstrings_are_empty() -> None:
    abdp = import_module("abdp")
    core = import_module("abdp.core")
    data = import_module("abdp.data")
    simulation = import_module("abdp.simulation")

    assert abdp.__doc__ == ""
    assert core.__doc__ == ""
    assert data.__doc__ == ""
    assert simulation.__doc__ == ""
