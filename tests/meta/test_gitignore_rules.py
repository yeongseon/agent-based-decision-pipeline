from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
GITIGNORE_PATH = REPO_ROOT / ".gitignore"

REQUIRED_PATTERNS = (
    "__pycache__/",
    ".venv/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".coverage",
    "build/",
    "dist/",
)

FORBIDDEN_PATTERNS = (
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
)


def _read_active_gitignore_lines() -> tuple[str, ...]:
    assert GITIGNORE_PATH.is_file()

    return tuple(
        line
        for line in GITIGNORE_PATH.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    )


def test_gitignore_contains_required_python_package_rules() -> None:
    active_lines = _read_active_gitignore_lines()

    for pattern in REQUIRED_PATTERNS:
        assert pattern in active_lines, pattern


def test_gitignore_does_not_contain_overly_broad_repository_rules() -> None:
    active_lines = _read_active_gitignore_lines()

    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in active_lines, pattern
