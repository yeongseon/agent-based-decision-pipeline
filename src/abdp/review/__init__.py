"""Public surface for the ``abdp.review`` package."""

from abdp.review.policy import CorrectionPolicy

globals().pop("policy", None)

__all__: tuple[str, ...] = ("CorrectionPolicy",)
