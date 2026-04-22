"""``AuditLog`` aggregate exposed by ``abdp.evidence``.

An :class:`AuditLog` bundles a completed scenario run with its
evaluation summary and the evidence and claim records produced during
that run. ``scenario_key`` and ``seed`` are kept as first-class fields
and validated against ``run`` in ``__post_init__`` to guarantee that
the bundle describes a single coherent execution. ``evidence`` and
``claims`` are stored as tuples and preserve caller-supplied order;
``AuditLog`` does not impose canonical ordering.
"""

from dataclasses import dataclass

from abdp.core import Seed
from abdp.evaluation import EvaluationSummary
from abdp.evidence.claim import ClaimRecord
from abdp.evidence.record import EvidenceRecord
from abdp.scenario import ScenarioRun
from abdp.simulation import ActionProposal, ParticipantState, SegmentState

__all__ = ["AuditLog"]


@dataclass(frozen=True, slots=True)
class AuditLog[S: SegmentState, P: ParticipantState, A: ActionProposal]:
    """Auditable bundle of a scenario run, its evaluation, and supporting facts.

    ``__post_init__`` enforces that ``scenario_key`` and ``seed`` match
    the corresponding fields on ``run``; collection ordering for
    ``evidence`` and ``claims`` is preserved exactly as supplied.
    """

    scenario_key: str
    seed: Seed
    run: ScenarioRun[S, P, A]
    summary: EvaluationSummary
    evidence: tuple[EvidenceRecord, ...]
    claims: tuple[ClaimRecord, ...]

    def __post_init__(self) -> None:
        if self.scenario_key != self.run.scenario_key:
            raise ValueError("scenario_key must match run.scenario_key")
        if self.seed != self.run.seed:
            raise ValueError("seed must match run.seed")
