"""Runnable entrypoint for the queue scheduling example."""

from __future__ import annotations

from abdp.core.types import Seed
from abdp.scenario import ScenarioRunner

from examples.queue_scheduling.agents import QueueWorkerAgent
from examples.queue_scheduling.domain import QueueProposal, QueueScenario, Slot, Worker
from examples.queue_scheduling.resolver import QueueResolver


def main() -> None:
    scenario = QueueScenario(scenario_key="latency-baseline", seed=Seed(11))
    runner = ScenarioRunner[Slot, Worker, QueueProposal](
        agents=(
            QueueWorkerAgent(agent_id="worker-fast", queue_id="expedite"),
            QueueWorkerAgent(agent_id="worker-flex", queue_id="standard"),
        ),
        resolver=QueueResolver(),
        max_steps=3,
    )
    run = runner.run(scenario)
    print(f"scenario_key={run.scenario_key}")
    print(f"seed={int(run.seed)}")
    print(f"step_count={run.step_count}")
    print(f"final_step_index={run.final_state.step_index}")
    print(f"max_steps_reached={run.final_state.step_index == runner.max_steps}")


if __name__ == "__main__":
    main()
