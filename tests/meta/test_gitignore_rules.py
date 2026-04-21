from pathlib import Path


def _read_active_gitignore_lines() -> tuple[str, ...]:
    repo_root = Path(__file__).resolve().parents[2]
    gitignore_path = repo_root / ".gitignore"

    assert gitignore_path.is_file()

    return tuple(
        line for line in gitignore_path.read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")
    )


def test_gitignore_contains_required_python_package_rules() -> None:
    active_lines = _read_active_gitignore_lines()

    for pattern in (
        "__pycache__/",
        ".venv/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".ruff_cache/",
        ".coverage",
        "build/",
        "dist/",
    ):
        assert pattern in active_lines, pattern


def test_gitignore_does_not_contain_overly_broad_repository_rules() -> None:
    active_lines = _read_active_gitignore_lines()

    for pattern in (
        "/",
        "*",
        "/*",
        "**",
        "/**",
        "src/",
        "/src/",
        "tests/",
        "/tests/",
        "*.py",
    ):
        assert pattern not in active_lines, pattern
