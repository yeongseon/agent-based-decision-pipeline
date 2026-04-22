"""Public surface for the ``abdp.evaluation`` package.

The evaluation package owns the v0.3 metric, gate, and summary contracts.
The surface is intentionally empty in #107 so subsequent v0.3 issues can
extend ``__all__`` symbol-by-symbol against the frozen surface test in
``tests/evaluation/test_evaluation_public_surface.py``.
"""

__all__: tuple[str, ...] = ()
