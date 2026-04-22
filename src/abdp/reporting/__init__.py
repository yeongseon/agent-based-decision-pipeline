"""Public surface for the ``abdp.reporting`` package.

The reporting package hosts audit-log renderers and report generators
introduced over the v0.3 milestone. ``render_json_report`` is the
deterministic JSON renderer for an :class:`abdp.evidence.AuditLog`;
subsequent issues extend ``__all__`` against the frozen surface test in
``tests/reporting/test_reporting_public_surface.py``.
"""

from abdp.reporting.json_renderer import render_json_report

globals().pop("json_renderer", None)

__all__: tuple[str, ...] = ("render_json_report",)
