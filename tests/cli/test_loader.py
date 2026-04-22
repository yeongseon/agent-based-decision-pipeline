"""Tests for ``abdp.cli.loader``."""

from __future__ import annotations

import pytest

from abdp.cli.loader import LoaderError, load_audit_log_factory
from abdp.core import Seed


def test_load_audit_log_factory_resolves_valid_spec() -> None:
    factory = load_audit_log_factory("tests.cli._fixtures:build_audit_log")
    assert callable(factory)


def test_loaded_factory_returns_audit_log_when_invoked() -> None:
    from abdp.evidence import AuditLog

    factory = load_audit_log_factory("tests.cli._fixtures:build_audit_log")
    result = factory(Seed(0))
    assert isinstance(result, AuditLog)


def test_loaded_factory_rejects_non_audit_log_return() -> None:
    factory = load_audit_log_factory("tests.cli._fixtures:build_not_audit_log")
    with pytest.raises(LoaderError, match="AuditLog"):
        factory(Seed(0))


@pytest.mark.parametrize(
    "spec",
    [
        "no_colon",
        "module:",
        ":callable",
        "module::callable",
        "module:callable:extra",
        " module:callable",
        "module:callable ",
        "module: callable",
        "",
        "tests.cli. _fixtures:build_audit_log",
        "tests.cli._fixtures:build audit_log",
        "module\twith\ttabs:func",
        ".os:path",
        "..pkg.mod:func",
        "pkg.:func",
        "pkg..mod:func",
        "pkg/mod:func",
        "pkg\\mod:func",
    ],
)
def test_load_audit_log_factory_rejects_malformed_spec(spec: str) -> None:
    with pytest.raises(LoaderError, match="spec"):
        load_audit_log_factory(spec)


def test_load_audit_log_factory_rejects_missing_module() -> None:
    with pytest.raises(LoaderError, match="module"):
        load_audit_log_factory("nonexistent_module_xyz:func")


def test_load_audit_log_factory_rejects_missing_attribute() -> None:
    with pytest.raises(LoaderError, match="attribute"):
        load_audit_log_factory("tests.cli._fixtures:does_not_exist")


def test_load_audit_log_factory_rejects_non_callable_attribute() -> None:
    with pytest.raises(LoaderError, match="callable"):
        load_audit_log_factory("tests.cli._fixtures:NOT_CALLABLE")


def test_loader_error_is_exception_subclass() -> None:
    assert issubclass(LoaderError, Exception)
