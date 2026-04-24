"""Review-loop runner that keeps rejected attempts off the canonical plane."""

from dataclasses import dataclass, field
from uuid import UUID

from abdp.agents import Agent, AgentContext, AgentDecision
from abdp.inspector import TraceEvent, TraceRecorder
from abdp.review.attempt import ReviewAttempt
from abdp.review.critic import Critic
from abdp.review.policy import CorrectionMode, CorrectionPolicy
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
    _active_recorder: TraceRecorder | None = field(default=None, init=False, repr=False, compare=False)

    def run(self, spec: ScenarioSpec[S, P, A]) -> ScenarioRun[S, P, A]:
        """Execute the scenario and commit only accepted or policy-selected steps."""
        object.__setattr__(self, "_active_recorder", self._build_active_recorder(spec))
        state: SimulationState[S, P, A] = spec.build_initial_state()
        steps: list[ScenarioStep[S, P, A]] = []

        while state.step_index < self.max_steps:
            begin_event = self._emit(
                event_type="step.begin",
                step_index=state.step_index,
                attributes={"scenario_key": spec.scenario_key},
            )
            end_step, committed_step, next_state, stop = self._review_step(
                spec=spec,
                state=state,
                parent_event_id=None if begin_event is None else begin_event.event_id,
            )
            self._emit(
                event_type="step.end",
                step_index=end_step.state.step_index,
                attributes={"proposals": len(end_step.proposals), "decisions": len(end_step.decisions)},
            )
            if committed_step is not None:
                steps.append(committed_step)
            state = next_state
            if stop or state.step_index >= self.max_steps:
                break

        object.__setattr__(self, "_active_recorder", None)
        return ScenarioRun(scenario_key=spec.scenario_key, seed=spec.seed, steps=tuple(steps), final_state=state)

    def _build_active_recorder(self, spec: ScenarioSpec[S, P, A]) -> TraceRecorder | None:
        if self.recorder is None:
            return None
        return TraceRecorder(
            store=self.recorder.store,
            seed=spec.seed,
            run_id=self._stable_run_id(spec),
        )

    def _stable_run_id(self, spec: ScenarioSpec[S, P, A]) -> str:
        critic_name = f"{type(self.critic).__module__}.{type(self.critic).__qualname__}"
        reviser_name = f"{type(self.reviser).__module__}.{type(self.reviser).__qualname__}"
        return (
            f"review:{spec.scenario_key}:{int(spec.seed)}:"
            f"{self.policy.max_retries}:{self.policy.min_score:.17g}:{self.policy.on_fail}:"
            f"{critic_name}:{reviser_name}"
        )

    def _review_step(
        self,
        *,
        spec: ScenarioSpec[S, P, A],
        state: SimulationState[S, P, A],
        parent_event_id: UUID | None,
    ) -> tuple[ScenarioStep[S, P, A], ScenarioStep[S, P, A] | None, SimulationState[S, P, A], bool]:
        proposals_override: tuple[A, ...] | None = None
        attempt_no = 0

        while True:
            decisions = tuple(self._decide(agent, spec, state) for agent in self.agents)
            emissions = tuple(proposal for decision in decisions for proposal in decision.proposals)
            proposals = state.pending_actions + emissions if proposals_override is None else proposals_override
            step = ScenarioStep(state=state, decisions=decisions, proposals=proposals)

            if not proposals:
                return step, step, state, True

            review = self.critic.evaluate(step)
            accepted = review.score >= self.policy.min_score
            attempt: ReviewAttempt[A] = ReviewAttempt(
                step_index=state.step_index,
                attempt_no=attempt_no,
                step=step,
                decision=review,
                accepted=accepted,
            )
            self._emit_attempt(
                attempt=attempt,
                disposition=self._disposition(accepted=accepted, attempt_no=attempt_no),
                parent_event_id=parent_event_id,
            )

            if accepted:
                return step, step, self.resolver.resolve(state, proposals), False

            if attempt_no < self.policy.max_retries:
                proposals_override = self.reviser.revise(attempt)
                attempt_no += 1
                continue

            return self._resolve_terminal_failure(state=state, step=step, attempt=attempt)

    def _resolve_terminal_failure(
        self,
        *,
        state: SimulationState[S, P, A],
        step: ScenarioStep[S, P, A],
        attempt: ReviewAttempt[A],
    ) -> tuple[ScenarioStep[S, P, A], ScenarioStep[S, P, A] | None, SimulationState[S, P, A], bool]:
        mode: CorrectionMode = self.policy.on_fail
        if mode == "rollback":
            return step, None, state, True
        if mode == "stop":
            return step, None, state, True
        revised = self.reviser.revise(attempt)
        revised_step = ScenarioStep(state=state, decisions=step.decisions, proposals=revised)
        return revised_step, revised_step, self.resolver.resolve(state, revised), True

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

    def _disposition(self, *, accepted: bool, attempt_no: int) -> str:
        if accepted:
            return "accept"
        if attempt_no < self.policy.max_retries:
            return "retry"
        return self.policy.on_fail

    def _emit_attempt(
        self,
        *,
        attempt: ReviewAttempt[A],
        disposition: str,
        parent_event_id: UUID | None,
    ) -> None:
        self._emit(
            event_type="review.attempt",
            step_index=attempt.step_index,
            attributes={
                "attempt_no": attempt.attempt_no,
                "accepted": attempt.accepted,
                "score": attempt.decision.score,
                "critique": attempt.decision.critique,
                "disposition": disposition,
                "snapshot_id": str(attempt.step.state.snapshot_ref.snapshot_id),
                "storage_key": attempt.step.state.snapshot_ref.storage_key,
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
            if self._active_recorder is None
            else self._active_recorder.record(
                event_type=event_type,
                step_index=step_index,
                attributes=attributes,
                parent_event_id=parent_event_id,
            )
        )
