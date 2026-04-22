"""Deterministic JSON renderer for :class:`abdp.evidence.AuditLog`.

``render_json_report`` walks an :class:`~abdp.evidence.AuditLog` (or any
JSON-serializable abdp value) and emits a stable, sorted-key JSON string
through the shared :mod:`abdp.reporting._normalize` invariants.
``indent`` must be a non-bool ``int``.
"""

import json
from typing import Any

from abdp.reporting._normalize import to_jsonable

__all__ = ["render_json_report"]


def render_json_report(value: Any, *, indent: int = 2) -> str:
    """Render ``value`` to a deterministic JSON string."""
    if isinstance(indent, bool) or not isinstance(indent, int):
        raise TypeError(f"indent must be int, got {type(indent).__name__}")
    payload = to_jsonable(value)
    return json.dumps(
        payload,
        indent=indent,
        sort_keys=True,
        separators=(",", ": "),
        ensure_ascii=False,
        allow_nan=False,
    )
