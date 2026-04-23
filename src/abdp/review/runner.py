"""Review-loop runner that keeps rejected attempts off the canonical plane."""

from dataclasses import dataclass
from uuid import UUID

from abdp.agents import Agent, AgentContext, AgentDecision
from abdp.inspector import TraceEvent, TraceRecorder
from abdp.review.attempt import ReviewAttempt
from abdp.review.critic import Critic
from abdp.review.policy import CorrectionPolicy
from abdp.review.reviser import Reviser
from abdp.scenario import ActionResolver, ScenarioRun, ScenarioStep
from abdp.simulation import ActionProposal, ParticipantState, ScenarioSpec, SegmentState, SimulationState

__all__ = ["ReviewLoopRunner"]


@dataclass(frozen=True, slots=True)
class ReviewLoopRunner[S: SegmentState, P: ParticipantState, A: ActionProposal]:
    """Scenario runner with a deterministic critic and reviser hook."""

    agents: tuple[Agent[S, P, A], ...]
    resolver: ActionResolver[S, P, A]
    max_steps: int
    critic: Critic[S, P, A]
    reviser: Reviser[A]
    policy: CorrectionPolicy
    recorder: TraceRecorder | None = None

    def run(self, spec: ScenarioSpec[S, P, A]) -> ScenarioRun[S, P, A]:
        """Execute the scenario and commit only accepted steps."""
        state: SimulationState[S, P, A] = spec.build_initial_state()
        steps: list[ScenarioStep[S, P, A]] = []

        while state.step_index < self.max_steps:
            begin_event = self._emit(
                event_type="step.begin",
                step_index=state.step_index,
                attributes={"scenario_key": spec.scenario_key},
            )
            decisions: tuple[AgentDecision[A], ...] = tuple(self._decide(agent, spec, state) for agent in self.agents)
            emissions: tuple[A, ...] = tuple(proposal for decision in decisions for proposal in decision.proposals)
            merged: tuple[A, ...] = state.pending_actions + emissions
            step = ScenarioStep(state=state, decisions=decisions, proposals=merged)

            if merged:
                review = self.critic.evaluate(step)
                attempt = ReviewAttempt(
                    step_index=state.step_index,
                    attempt_no=0,
                    step=step,
                    decision=review,
                    accepted=review.score >= self.policy.min_score,
                )
                self._emit_attempt(
                    attempt=attempt, parent_event_id=None if begin_event is None else begin_event.event_id
                )

            steps.append(step)
            self._emit(
                event_type="step.end",
                step_index=state.step_index,
                attributes={"proposals": len(merged), "decisions": len(decisions)},
            )
            if not merged:
                break
            state = self.resolver.resolve(state, merged)
            if state.step_index >= self.max_steps:
                break

        return ScenarioRun(scenario_key=spec.scenario_key, seed=spec.seed, steps=tuple(steps), final_state=state)

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
            attributes={"agent_id": agent.agent_id, "proposals": len(decision.proposals)},
        )
        return decision

    def _emit_attempt(self, *, attempt: ReviewAttempt[A], parent_event_id: UUID | None) -> None:
        self._emit(
            event_type="review.attempt",
            step_index=attempt.step_index,
            attributes={
                "attempt_no": attempt.attempt_no,
                "accepted": attempt.accepted,
                "score": attempt.decision.score,
                "critique": attempt.decision.critique,
            },
            parent_event_id=parent_event_id,
        )

    def _emit(
        self,
        *,
        event_type: str,
        step_index: int,
        attributes: dict[str, str | int | float | bool],
        parent_event_id: UUID | None = None,
    ) -> TraceEvent | None:
        return (
            None
            if self.recorder is None
            else self.recorder.record(
                event_type=event_type,
                step_index=step_index,
                attributes=attributes,
                parent_event_id=parent_event_id,
            )
        )
