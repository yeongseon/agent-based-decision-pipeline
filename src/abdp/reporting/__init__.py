"""Public surface for the ``abdp.reporting`` package.

The reporting package will host audit-log renderers and report
generators introduced over the v0.3 milestone. The surface starts
empty by design; each subsequent issue extends ``__all__`` against
the frozen surface test in
``tests/reporting/test_reporting_public_surface.py``.
"""

__all__: tuple[str, ...] = ()
