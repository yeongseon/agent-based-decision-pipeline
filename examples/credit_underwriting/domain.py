"""Credit underwriting domain types for the abdp v0.2 example."""

from __future__ import annotations

from dataclasses import dataclass

from abdp.core.types import JsonValue

ACTION_APPROVE = "approve"
ACTION_DECLINE = "decline"
ACTION_REQUEST_INFO = "request_info"
ACTION_ESCALATE = "escalate"


@dataclass(frozen=True, slots=True, kw_only=True)
class Borrower:
    participant_id: str
    credit_score: int
    requested_amount_cents: int
    debt_to_income_bps: int


@dataclass(frozen=True, slots=True, kw_only=True)
class RiskTier:
    segment_id: str
    participant_ids: tuple[str, ...]
    tier_key: str
    min_credit_score: int
    max_amount_cents: int


@dataclass(slots=True, kw_only=True)
class CreditAction:
    proposal_id: str
    actor_id: str
    action_key: str
    payload: JsonValue
