"""Integration test for the credit underwriting example (#101).

Verifies that the example wires together domain types, agents, resolver, and
scenario builder against the public ``abdp`` v0.2 surface, runs deterministically
under ``ScenarioRunner`` for a fixed seed, and exposes a ``main()`` entrypoint.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import assert_type

import pytest

import abdp
from abdp.agents import Agent
from abdp.core.types import Seed, is_json_value
from abdp.scenario import ActionResolver, ScenarioRun, ScenarioRunner
from abdp.simulation import (
    ActionProposal,
    ParticipantState,
    ScenarioSpec,
    SegmentState,
    SimulationState,
)
from examples.credit_underwriting import (
    Borrower,
    CreditAction,
    CreditResolver,
    CreditScenario,
    RiskTier,
    TierOfficer,
)
from examples.credit_underwriting.__main__ import main as credit_main

REPO_ROOT = Path(__file__).resolve().parents[2]
SEED = Seed(7)
SCENARIO_KEY = "credit-underwriting-baseline"


def _build_runner() -> ScenarioRunner[RiskTier, Borrower, CreditAction]:
    return ScenarioRunner[RiskTier, Borrower, CreditAction](
        agents=(
            TierOfficer(agent_id="officer-prime", tier_key="prime"),
            TierOfficer(agent_id="officer-subprime", tier_key="subprime"),
        ),
        resolver=CreditResolver(),
        max_steps=8,
    )


def test_borrower_satisfies_participant_state_protocol() -> None:
    borrower = Borrower(
        participant_id="borrower-alice",
        credit_score=780,
        requested_amount_cents=3_000_000,
        debt_to_income_bps=2500,
    )
    assert isinstance(borrower, ParticipantState)
    assert borrower.participant_id == "borrower-alice"


def test_risk_tier_satisfies_segment_state_protocol() -> None:
    tier = RiskTier(
        segment_id="tier-prime",
        participant_ids=("borrower-alice",),
        tier_key="prime",
        min_credit_score=720,
        max_amount_cents=5_000_000,
    )
    assert isinstance(tier, SegmentState)
    assert tier.segment_id == "tier-prime"
    assert tier.participant_ids == ("borrower-alice",)


def test_credit_action_satisfies_action_proposal_protocol() -> None:
    action = CreditAction(
        proposal_id="p-001",
        actor_id="officer-prime",
        action_key="approve",
        payload={"borrower_id": "borrower-alice"},
    )
    assert isinstance(action, ActionProposal)
    assert is_json_value(action.payload)


def test_credit_scenario_satisfies_scenario_spec_protocol() -> None:
    scenario = CreditScenario(seed=SEED)
    assert isinstance(scenario, ScenarioSpec)
    assert scenario.scenario_key == SCENARIO_KEY
    assert scenario.seed == SEED
    state = scenario.build_initial_state()
    _ = assert_type(state, SimulationState[RiskTier, Borrower, CreditAction])
    assert isinstance(state, SimulationState)


def test_tier_officer_satisfies_agent_protocol() -> None:
    officer = TierOfficer(agent_id="officer-prime", tier_key="prime")
    assert isinstance(officer, Agent)
    assert officer.agent_id == "officer-prime"


def test_credit_resolver_satisfies_action_resolver_protocol() -> None:
    resolver = CreditResolver()
    assert isinstance(resolver, ActionResolver)


def test_run_is_deterministic_for_fixed_seed() -> None:
    runner = _build_runner()
    run_a = runner.run(CreditScenario(seed=SEED))
    run_b = runner.run(CreditScenario(seed=SEED))
    assert run_a == run_b


def test_run_produces_expected_terminal_shape() -> None:
    run = _build_runner().run(CreditScenario(seed=SEED))
    _ = assert_type(run, ScenarioRun[RiskTier, Borrower, CreditAction])
    assert run.scenario_key == SCENARIO_KEY
    assert run.seed == SEED
    assert run.step_count == 3
    assert run.final_state.step_index == 2
    assert run.final_state.pending_actions == ()
    for tier in run.final_state.segments:
        assert tier.participant_ids == ()


def test_run_exercises_all_credit_action_keys_across_steps() -> None:
    run = _build_runner().run(CreditScenario(seed=SEED))
    step0_keys = sorted(p.action_key for p in run.steps[0].proposals)
    assert step0_keys == [
        "approve",
        "approve",
        "decline",
        "decline",
        "escalate",
        "request_info",
        "request_info",
    ]
    step1_keys = sorted(p.action_key for p in run.steps[1].proposals)
    assert step1_keys == ["escalate", "escalate"]
    assert run.steps[2].proposals == ()


def test_resolver_rejects_unknown_action_key() -> None:
    resolver = CreditResolver()
    state = CreditScenario(seed=SEED).build_initial_state()
    bad = CreditAction(
        proposal_id="bad-001",
        actor_id="officer-prime",
        action_key="mystery",
        payload={"borrower_id": "borrower-alice"},
    )
    with pytest.raises(ValueError, match="Unknown action_key"):
        resolver.resolve(state, (bad,))


def test_main_entrypoint_prints_deterministic_summary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    credit_main()
    captured = capsys.readouterr()
    assert "scenario_key=credit-underwriting-baseline" in captured.out
    assert "seed=7" in captured.out
    assert "step_count=3" in captured.out
    assert "final_step_index=2" in captured.out


def test_no_abdp_source_files_modified_by_example() -> None:
    fixture_path = Path(inspect.getfile(CreditScenario)).resolve()
    abdp_pkg_path = Path(inspect.getfile(abdp)).resolve().parent
    assert fixture_path.is_relative_to(REPO_ROOT / "examples")
    assert not fixture_path.is_relative_to(REPO_ROOT / "src")
    assert abdp_pkg_path == REPO_ROOT / "src" / "abdp"
