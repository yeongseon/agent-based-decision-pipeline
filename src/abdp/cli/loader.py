"""Loader resolving ``module.path:callable`` specs to audit-log factories.

The loader accepts a strict ``module.path:callable`` spec (single colon,
no whitespace, no empty parts), imports the named module, retrieves the
named attribute, and returns a wrapper callable that invokes the resolved
factory with a :class:`abdp.core.Seed` and validates that the result is
an :class:`abdp.evidence.AuditLog`. All loader-domain errors raise
:class:`LoaderError`; the underlying ``ImportError``/``AttributeError`` is
chained via ``raise ... from``.
"""

import importlib
from collections.abc import Callable
from typing import Any, cast

from abdp.core import Seed
from abdp.evidence import AuditLog

__all__ = ["LoaderError", "load_audit_log_factory"]

_AuditLogFactory = Callable[[Seed], AuditLog[Any, Any, Any]]


class LoaderError(Exception):
    """Raised when a CLI loader spec cannot be resolved to a valid factory."""


def load_audit_log_factory(spec: str) -> _AuditLogFactory:
    module_name, attr_name = _parse_spec(spec)
    factory = _resolve_callable(module_name, attr_name)
    return _wrap_factory(factory, spec)


def _parse_spec(spec: str) -> tuple[str, str]:
    if not isinstance(spec, str) or spec != spec.strip() or ":" not in spec:
        raise LoaderError(_invalid_spec(spec, "expected 'module.path:callable' format"))
    parts = spec.split(":")
    if len(parts) != 2:
        raise LoaderError(_invalid_spec(spec, "expected exactly one ':' separator"))
    module_name, attr_name = parts
    if not module_name or not attr_name:
        raise LoaderError(_invalid_spec(spec, "module and callable parts must be non-empty"))
    if module_name != module_name.strip() or attr_name != attr_name.strip():
        raise LoaderError(_invalid_spec(spec, "module and callable parts must not contain whitespace"))
    return module_name, attr_name


def _invalid_spec(spec: object, reason: str) -> str:
    return f"Invalid loader spec {spec!r}: {reason}."


def _resolve_callable(module_name: str, attr_name: str) -> Callable[..., object]:
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise LoaderError(f"Cannot import module {module_name!r}: {exc}") from exc
    if not hasattr(module, attr_name):
        raise LoaderError(f"Module {module_name!r} has no attribute {attr_name!r}.")
    obj = getattr(module, attr_name)
    if not callable(obj):
        raise LoaderError(f"{module_name}:{attr_name} is not callable (got {type(obj).__name__}).")
    return cast(Callable[..., object], obj)


def _wrap_factory(factory: Callable[..., object], spec: str) -> _AuditLogFactory:
    def _invoke(seed: Seed) -> AuditLog[Any, Any, Any]:
        result = factory(seed)
        if not isinstance(result, AuditLog):
            raise LoaderError(f"Loader spec {spec!r} returned {type(result).__name__}, expected AuditLog.")
        return result

    return _invoke
