"""Runnable entrypoint for the credit underwriting example."""

from __future__ import annotations

from abdp.core.types import Seed
from abdp.scenario import ScenarioRunner

from examples.credit_underwriting.agents import TierOfficer
from examples.credit_underwriting.domain import Borrower, CreditAction, RiskTier
from examples.credit_underwriting.resolver import CreditResolver
from examples.credit_underwriting.scenario import CreditScenario


def main() -> None:
    scenario = CreditScenario(seed=Seed(7))
    runner = ScenarioRunner[RiskTier, Borrower, CreditAction](
        agents=(
            TierOfficer(agent_id="officer-prime", tier_key="prime"),
            TierOfficer(agent_id="officer-subprime", tier_key="subprime"),
        ),
        resolver=CreditResolver(),
        max_steps=8,
    )
    run = runner.run(scenario)
    print(f"scenario_key={run.scenario_key}")
    print(f"seed={int(run.seed)}")
    print(f"step_count={run.step_count}")
    print(f"final_step_index={run.final_state.step_index}")


if __name__ == "__main__":
    main()
