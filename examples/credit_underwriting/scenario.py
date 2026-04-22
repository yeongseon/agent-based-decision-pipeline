"""Credit underwriting scenario builder over the abdp v0.2 simulation contracts."""

from __future__ import annotations

from typing import override
from uuid import UUID

from abdp.core.types import Seed
from abdp.data.snapshot_manifest import SnapshotTier
from abdp.simulation import ScenarioSpec, SimulationState, SnapshotRef

from examples.credit_underwriting.domain import (
    ACTION_ESCALATE,
    Borrower,
    CreditAction,
    RiskTier,
)

SCENARIO_KEY = "credit-underwriting-baseline"
SNAPSHOT_UUID = UUID("33333333-3333-3333-3333-333333333333")
SNAPSHOT_TIER: SnapshotTier = "bronze"
SNAPSHOT_STORAGE_KEY = "snapshots/bronze/credit-underwriting-initial.json"


class CreditScenario(ScenarioSpec[RiskTier, Borrower, CreditAction]):
    def __init__(self, *, scenario_key: str = SCENARIO_KEY, seed: Seed) -> None:
        self._scenario_key = scenario_key
        self._seed = seed

    @property
    def scenario_key(self) -> str:
        return self._scenario_key

    @property
    def seed(self) -> Seed:
        return self._seed

    @override
    def build_initial_state(self) -> SimulationState[RiskTier, Borrower, CreditAction]:
        borrowers = (
            Borrower(
                participant_id="borrower-alice",
                credit_score=780,
                requested_amount_cents=3_000_000,
                debt_to_income_bps=2500,
            ),
            Borrower(
                participant_id="borrower-bob",
                credit_score=700,
                requested_amount_cents=4_000_000,
                debt_to_income_bps=3500,
            ),
            Borrower(
                participant_id="borrower-frank",
                credit_score=750,
                requested_amount_cents=6_000_000,
                debt_to_income_bps=3000,
            ),
            Borrower(
                participant_id="borrower-carol",
                credit_score=620,
                requested_amount_cents=800_000,
                debt_to_income_bps=4000,
            ),
            Borrower(
                participant_id="borrower-dave",
                credit_score=550,
                requested_amount_cents=1_200_000,
                debt_to_income_bps=4500,
            ),
            Borrower(
                participant_id="borrower-grace",
                credit_score=600,
                requested_amount_cents=1_500_000,
                debt_to_income_bps=4200,
            ),
        )
        tiers = (
            RiskTier(
                segment_id="tier-prime",
                participant_ids=("borrower-alice", "borrower-bob", "borrower-frank"),
                tier_key="prime",
                min_credit_score=720,
                max_amount_cents=5_000_000,
            ),
            RiskTier(
                segment_id="tier-subprime",
                participant_ids=("borrower-carol", "borrower-dave", "borrower-grace"),
                tier_key="subprime",
                min_credit_score=580,
                max_amount_cents=1_000_000,
            ),
        )
        pending = (
            CreditAction(
                proposal_id="escalate-prior-001",
                actor_id="officer-prime",
                action_key=ACTION_ESCALATE,
                payload={"case_id": "case-prior-001", "reason": "carry_over_review"},
            ),
        )
        return SimulationState[RiskTier, Borrower, CreditAction](
            step_index=0,
            seed=self.seed,
            snapshot_ref=SnapshotRef(
                snapshot_id=SNAPSHOT_UUID,
                tier=SNAPSHOT_TIER,
                storage_key=SNAPSHOT_STORAGE_KEY,
            ),
            segments=tiers,
            participants=borrowers,
            pending_actions=pending,
        )
