"""Credit underwriting agents that emit per-borrower disposition proposals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import override

from abdp.agents import Agent, AgentContext, AgentDecision

from examples.credit_underwriting.domain import (
    ACTION_APPROVE,
    ACTION_DECLINE,
    ACTION_REQUEST_INFO,
    Borrower,
    CreditAction,
    RiskTier,
)


@dataclass(slots=True, kw_only=True)
class CreditDecision:
    agent_id: str
    proposals: tuple[CreditAction, ...]


@dataclass(slots=True, kw_only=True)
class TierOfficer(Agent[RiskTier, Borrower, CreditAction]):
    agent_id: str
    tier_key: str

    @override
    def decide(
        self,
        context: AgentContext[RiskTier, Borrower, CreditAction],
    ) -> AgentDecision[CreditAction]:
        state = context.state
        tier = next((t for t in state.segments if t.tier_key == self.tier_key), None)
        if tier is None or not tier.participant_ids:
            return CreditDecision(agent_id=self.agent_id, proposals=())
        borrowers_by_id = {b.participant_id: b for b in state.participants}
        proposals = tuple(
            self._propose(borrowers_by_id[borrower_id], tier, context.step_index)
            for borrower_id in tier.participant_ids
        )
        return CreditDecision(agent_id=self.agent_id, proposals=proposals)

    def _propose(self, borrower: Borrower, tier: RiskTier, step_index: int) -> CreditAction:
        return CreditAction(
            proposal_id=f"decision-{self.tier_key}-{borrower.participant_id}-step{step_index}",
            actor_id=self.agent_id,
            action_key=_classify(borrower, tier),
            payload={
                "borrower_id": borrower.participant_id,
                "credit_score": borrower.credit_score,
                "requested_amount_cents": borrower.requested_amount_cents,
            },
        )


def _classify(borrower: Borrower, tier: RiskTier) -> str:
    if borrower.credit_score < tier.min_credit_score:
        return ACTION_DECLINE
    if borrower.requested_amount_cents > tier.max_amount_cents:
        return ACTION_REQUEST_INFO
    return ACTION_APPROVE
