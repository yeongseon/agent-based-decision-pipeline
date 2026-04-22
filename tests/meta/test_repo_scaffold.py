from importlib import import_module
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_README_TEXT = (
    "# agent-based-decision-pipeline\n\nA Python framework for reproducible agent-based decision simulation"
)

REQUIRED_SCAFFOLD_PATHS = (
    "src/abdp/__init__.py",
    "src/abdp/core/__init__.py",
    "src/abdp/data/__init__.py",
    "src/abdp/simulation/__init__.py",
    "src/abdp/py.typed",
)

PACKAGE_MODULES_WITH_EMPTY_DOCSTRING = (
    "abdp",
    "abdp.data",
    "abdp.simulation",
)


def test_readme_contains_only_project_name_and_tagline() -> None:
    readme = REPO_ROOT / "README.md"

    assert readme.is_file()
    assert readme.read_text(encoding="utf-8").strip() == EXPECTED_README_TEXT


def test_required_scaffold_files_exist() -> None:
    for relative_path in REQUIRED_SCAFFOLD_PATHS:
        assert (REPO_ROOT / relative_path).is_file(), relative_path


def test_package_imports_succeed_and_module_docstrings_are_empty() -> None:
    for module_name in PACKAGE_MODULES_WITH_EMPTY_DOCSTRING:
        module = import_module(module_name)
        assert module.__doc__ == "", module_name
