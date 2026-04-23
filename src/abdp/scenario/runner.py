"""Public ``ScenarioRunner`` model exposed by ``abdp.scenario``."""

from dataclasses import dataclass

from abdp.agents import Agent, AgentContext, AgentDecision
from abdp.inspector.recorder import TraceRecorder
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

    When ``recorder`` is provided, ``run`` emits ``step.begin``,
    ``decision.evaluate``, and ``step.end`` :class:`abdp.inspector.TraceEvent`
    records into the inspector plane. Recording is metadata only and does
    not influence canonical scenario output.
    """

    agents: tuple[Agent[S, P, A], ...]
    resolver: ActionResolver[S, P, A]
    max_steps: int
    recorder: TraceRecorder | None = None

    def run(self, spec: ScenarioSpec[S, P, A]) -> ScenarioRun[S, P, A]:
        """Execute the scenario and return its full ``ScenarioRun`` trace."""
        state: SimulationState[S, P, A] = spec.build_initial_state()
        steps: list[ScenarioStep[S, P, A]] = []

        while state.step_index < self.max_steps:
            self._emit(
                event_type="step.begin",
                step_index=state.step_index,
                attributes={"scenario_key": spec.scenario_key},
            )
            decisions: tuple[AgentDecision[A], ...] = tuple(self._decide(agent, spec, state) for agent in self.agents)
            emissions: tuple[A, ...] = tuple(proposal for decision in decisions for proposal in decision.proposals)
            merged: tuple[A, ...] = state.pending_actions + emissions

            steps.append(ScenarioStep(state=state, decisions=decisions, proposals=merged))

            self._emit(
                event_type="step.end",
                step_index=state.step_index,
                attributes={
                    "proposals": len(merged),
                    "decisions": len(decisions),
                },
            )

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

    def _decide(
        self,
        agent: Agent[S, P, A],
        spec: ScenarioSpec[S, P, A],
        state: SimulationState[S, P, A],
    ) -> AgentDecision[A]:
        decision = agent.decide(
            AgentContext(
                scenario_key=spec.scenario_key,
                agent_id=agent.agent_id,
                step_index=state.step_index,
                seed=state.seed,
                state=state,
            )
        )
        self._emit(
            event_type="decision.evaluate",
            step_index=state.step_index,
            attributes={
                "agent_id": agent.agent_id,
                "proposals": len(decision.proposals),
            },
        )
        return decision

    def _emit(
        self,
        *,
        event_type: str,
        step_index: int,
        attributes: dict[str, str | int | float | bool],
    ) -> None:
        if self.recorder is None:
            return
        self.recorder.record(
            event_type=event_type,
            step_index=step_index,
            attributes=attributes,
        )
