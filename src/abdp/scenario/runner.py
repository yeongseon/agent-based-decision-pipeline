"""Public ``ScenarioRunner`` model exposed by ``abdp.scenario``."""

from dataclasses import dataclass

from abdp.agents import Agent, AgentContext, AgentDecision
from abdp.scenario.resolver import ActionResolver
from abdp.scenario.run import ScenarioRun
from abdp.scenario.step import ScenarioStep
from abdp.simulation import (
    ActionProposal,
    ParticipantState,
    ScenarioSpec,
    SegmentState,
    SimulationState,
)

__all__ = ["ScenarioRunner"]


@dataclass(frozen=True, slots=True)
class ScenarioRunner[S: SegmentState, P: ParticipantState, A: ActionProposal]:
    """Deterministic execution loop for an agent-based scenario.

    Drives a ``ScenarioSpec`` forward by polling each ``Agent`` in declared
    tuple order, merging the resulting proposals with any ``pending_actions``
    carried by the current state, and delegating progression to an
    ``ActionResolver``. Iteration is bounded by ``max_steps`` and terminates
    early when no proposals remain to resolve.
    """

    agents: tuple[Agent[S, P, A], ...]
    resolver: ActionResolver[S, P, A]
    max_steps: int

    def run(self, spec: ScenarioSpec[S, P, A]) -> ScenarioRun[S, P, A]:
        """Execute the scenario and return its full ``ScenarioRun`` trace."""
        state: SimulationState[S, P, A] = spec.build_initial_state()
        steps: list[ScenarioStep[S, P, A]] = []

        while state.step_index < self.max_steps:
            decisions: tuple[AgentDecision[A], ...] = tuple(
                agent.decide(
                    AgentContext(
                        scenario_key=spec.scenario_key,
                        agent_id=agent.agent_id,
                        step_index=state.step_index,
                        seed=state.seed,
                        state=state,
                    )
                )
                for agent in self.agents
            )
            emissions: tuple[A, ...] = tuple(proposal for decision in decisions for proposal in decision.proposals)
            merged: tuple[A, ...] = state.pending_actions + emissions

            steps.append(ScenarioStep(state=state, decisions=decisions, proposals=merged))

            if not merged:
                break

            state = self.resolver.resolve(state, merged)
            if state.step_index >= self.max_steps:
                break

        return ScenarioRun(
            scenario_key=spec.scenario_key,
            seed=spec.seed,
            steps=tuple(steps),
            final_state=state,
        )
