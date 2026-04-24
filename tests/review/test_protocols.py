from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar, get_args, get_origin, get_type_hints

from abdp.review.attempt import ReviewAttempt, ReviewDecision
from abdp.review.critic import Critic
from abdp.review.reviser import Reviser
from abdp.scenario import ScenarioStep
from abdp.simulation import ActionProposal, ParticipantState, SegmentState


class _ValidCritic:
    def evaluate(self, step: ScenarioStep[SegmentState, ParticipantState, ActionProposal]) -> ReviewDecision:
        raise NotImplementedError


class _MissingCriticMethod:
    pass


class _IdentityOnlyCritic:
    def evaluate(self, step: object) -> object:
        return object()


@dataclass(frozen=True, slots=True)
class _Action:
    proposal_id: str
    actor_id: str
    action_key: str
    payload: None


class _ValidReviser:
    def revise(self, attempt: ReviewAttempt[_Action]) -> tuple[_Action, ...]:
        raise NotImplementedError


class _MissingReviserMethod:
    pass


class _IdentityOnlyReviser:
    def revise(self, attempt: object) -> object:
        return ()


def test_critic_is_generic_runtime_checkable_protocol() -> None:
    assert getattr(Critic, "_is_protocol", False) is True
    assert getattr(Critic, "_is_runtime_protocol", False) is True
    assert tuple(param.__name__ for param in Critic.__type_params__) == ("S", "P", "A")


def test_critic_declares_expected_signature() -> None:
    hints = get_type_hints(Critic.evaluate)

    assert get_origin(hints["step"]) is ScenarioStep
    assert get_args(hints["return"]) == ()
    assert hints["return"] is ReviewDecision


def test_critic_runtime_checkable_accepts_structural_impl() -> None:
    assert isinstance(_ValidCritic(), Critic) is True


def test_critic_runtime_checkable_rejects_missing_method() -> None:
    assert isinstance(_MissingCriticMethod(), Critic) is False


def test_critic_runtime_check_only_guards_method_identity() -> None:
    assert isinstance(_IdentityOnlyCritic(), Critic) is True


def test_reviser_is_generic_runtime_checkable_protocol() -> None:
    assert getattr(Reviser, "_is_protocol", False) is True
    assert getattr(Reviser, "_is_runtime_protocol", False) is True
    assert len(Reviser.__type_params__) == 1
    assert isinstance(Reviser.__type_params__[0], TypeVar)
    assert Reviser.__type_params__[0].__name__ == "A"


def test_reviser_declares_expected_signature() -> None:
    hints = get_type_hints(Reviser.revise)

    assert get_origin(hints["attempt"]) is ReviewAttempt
    assert get_origin(hints["return"]) is tuple
    assert get_args(hints["return"]) == (Reviser.__type_params__[0], Ellipsis)


def test_reviser_runtime_checkable_accepts_structural_impl() -> None:
    assert isinstance(_ValidReviser(), Reviser) is True


def test_reviser_runtime_checkable_rejects_missing_method() -> None:
    assert isinstance(_MissingReviserMethod(), Reviser) is False


def test_reviser_runtime_check_only_guards_method_identity() -> None:
    assert isinstance(_IdentityOnlyReviser(), Reviser) is True
