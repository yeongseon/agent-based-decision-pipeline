"""Credit underwriting resolver that progresses tier membership and pending escalations."""

from __future__ import annotations

from typing import cast, override

from abdp.core.types import JsonValue
from abdp.scenario import ActionResolver
from abdp.simulation import SimulationState

from examples.credit_underwriting.domain import (
    ACTION_APPROVE,
    ACTION_DECLINE,
    ACTION_ESCALATE,
    ACTION_REQUEST_INFO,
    Borrower,
    CreditAction,
    RiskTier,
)


class CreditResolver(ActionResolver[RiskTier, Borrower, CreditAction]):
    @override
    def resolve(
        self,
        state: SimulationState[RiskTier, Borrower, CreditAction],
        proposals: tuple[CreditAction, ...],
    ) -> SimulationState[RiskTier, Borrower, CreditAction]:
        removed_ids: set[str] = set()
        next_pending: list[CreditAction] = []
        for proposal in proposals:
            match proposal.action_key:
                case k if k == ACTION_APPROVE or k == ACTION_DECLINE:
                    removed_ids.add(_borrower_id(proposal))
                case k if k == ACTION_REQUEST_INFO:
                    borrower_id = _borrower_id(proposal)
                    removed_ids.add(borrower_id)
                    next_pending.append(_escalation_for(borrower_id, proposal, state.step_index + 1))
                case k if k == ACTION_ESCALATE:
                    continue
                case unknown:
                    raise ValueError(f"Unknown action_key: {unknown}")
        return SimulationState[RiskTier, Borrower, CreditAction](
            step_index=state.step_index + 1,
            seed=state.seed,
            snapshot_ref=state.snapshot_ref,
            segments=tuple(_drop_members(tier, removed_ids) for tier in state.segments),
            participants=state.participants,
            pending_actions=tuple(next_pending),
        )


def _drop_members(tier: RiskTier, removed_ids: set[str]) -> RiskTier:
    return RiskTier(
        segment_id=tier.segment_id,
        participant_ids=tuple(pid for pid in tier.participant_ids if pid not in removed_ids),
        tier_key=tier.tier_key,
        min_credit_score=tier.min_credit_score,
        max_amount_cents=tier.max_amount_cents,
    )


def _escalation_for(borrower_id: str, source: CreditAction, next_step_index: int) -> CreditAction:
    return CreditAction(
        proposal_id=f"escalate-{borrower_id}-step{next_step_index}",
        actor_id=source.actor_id,
        action_key=ACTION_ESCALATE,
        payload={
            "case_id": f"case-{borrower_id}",
            "reason": "borderline_request_info",
        },
    )


def _borrower_id(proposal: CreditAction) -> str:
    payload = cast(dict[str, JsonValue], proposal.payload)
    return cast(str, payload["borrower_id"])
