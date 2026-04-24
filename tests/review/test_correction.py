from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from uuid import UUID

from abdp.agents import AgentContext, AgentDecision
from abdp.core import JsonValue, Seed
from abdp.review import CorrectionPolicy, ReviewAttempt, ReviewDecision, ReviewLoopRunner
from abdp.scenario import ScenarioStep
from abdp.simulation import ParticipantState, SegmentState, SimulationState
from abdp.simulation.snapshot_ref import SnapshotRef


@dataclass(frozen=True, slots=True)
class _Action:
    proposal_id: str
    actor_id: str
    action_key: str
    payload: JsonValue


_State = SimulationState[SegmentState, ParticipantState, _Action]
_SEED = Seed(7)


@dataclass(frozen=True, slots=True)
class _Spec:
    scenario_key: str
    seed: Seed
    initial: _State

    def build_initial_state(self) -> _State:
        return self.initial


@dataclass
class _Decision:
    agent_id: str
    proposals: tuple[_Action, ...]


@dataclass
class _Agent:
    agent_id: str
    proposals_to_emit: tuple[_Action, ...]
    seen_states: list[_State] = dataclasses.field(default_factory=list)

    def decide(self, context: AgentContext[SegmentState, ParticipantState, _Action]) -> AgentDecision[_Action]:
        self.seen_states.append(context.state)
        return _Decision(agent_id=self.agent_id, proposals=self.proposals_to_emit)


@dataclass
class _Resolver:
    received: list[tuple[_State, tuple[_Action, ...]]] = dataclasses.field(default_factory=list)

    def resolve(self, state: _State, proposals: tuple[_Action, ...]) -> _State:
        self.received.append((state, proposals))
        return _make_state(step_index=state.step_index + 1, snapshot_suffix=state.step_index + 2)


@dataclass
class _ScoreCritic:
    scores: dict[str, float]
    seen_steps: list[ScenarioStep[SegmentState, ParticipantState, _Action]] = dataclasses.field(default_factory=list)

    def evaluate(self, step: ScenarioStep[SegmentState, ParticipantState, _Action]) -> ReviewDecision:
        self.seen_steps.append(step)
        proposal_id = step.proposals[0].proposal_id
        return ReviewDecision(score=self.scores[proposal_id], critique=proposal_id)


@dataclass
class _Reviser:
    revised: tuple[_Action, ...]
    seen_attempts: list[ReviewAttempt[_Action]] = dataclasses.field(default_factory=list)

    def revise(self, attempt: ReviewAttempt[_Action]) -> tuple[_Action, ...]:
        self.seen_attempts.append(attempt)
        return self.revised


def _make_state(*, step_index: int = 0, snapshot_suffix: int = 1) -> _State:
    return SimulationState[SegmentState, ParticipantState, _Action](
        step_index=step_index,
        seed=_SEED,
        snapshot_ref=SnapshotRef(
            snapshot_id=UUID(int=snapshot_suffix), tier="bronze", storage_key=f"snapshots/{snapshot_suffix}"
        ),
        segments=(),
        participants=(),
        pending_actions=(),
    )


def _action(name: str) -> _Action:
    return _Action(proposal_id=name, actor_id="agent-1", action_key="noop", payload=None)


def test_review_loop_runner_retries_until_a_revised_attempt_is_accepted() -> None:
    initial = _make_state(step_index=0)
    spec = _Spec(scenario_key="retry", seed=_SEED, initial=initial)
    agent = _Agent(agent_id="agent-1", proposals_to_emit=(_action("initial"),))
    resolver = _Resolver()
    critic = _ScoreCritic(scores={"initial": 0.2, "revised": 0.9})
    reviser = _Reviser(revised=(_action("revised"),))
    runner = ReviewLoopRunner(
        agents=(agent,),
        resolver=resolver,
        max_steps=1,
        critic=critic,
        reviser=reviser,
        policy=CorrectionPolicy(max_retries=1, min_score=0.5, on_fail="stop"),
    )

    run = runner.run(spec)

    assert [proposal.proposal_id for proposal in run.steps[0].proposals] == ["revised"]
    assert [proposal.proposal_id for _, proposals in resolver.received for proposal in proposals] == ["revised"]
    assert [step.proposals[0].proposal_id for step in critic.seen_steps] == ["initial", "revised"]


def test_review_loop_runner_retries_from_the_same_committed_state() -> None:
    initial = _make_state(step_index=0, snapshot_suffix=99)
    spec = _Spec(scenario_key="rollback", seed=_SEED, initial=initial)
    agent = _Agent(agent_id="agent-1", proposals_to_emit=(_action("initial"),))
    resolver = _Resolver()
    critic = _ScoreCritic(scores={"initial": 0.2, "revised": 0.2})
    reviser = _Reviser(revised=(_action("revised"),))
    runner = ReviewLoopRunner(
        agents=(agent,),
        resolver=resolver,
        max_steps=1,
        critic=critic,
        reviser=reviser,
        policy=CorrectionPolicy(max_retries=1, min_score=0.5, on_fail="rollback"),
    )

    runner.run(spec)

    snapshots = [step.state.snapshot_ref.snapshot_id for step in critic.seen_steps]
    assert snapshots == [UUID(int=99), UUID(int=99)]


def test_review_loop_runner_rolls_back_after_terminal_failure() -> None:
    initial = _make_state(step_index=0)
    spec = _Spec(scenario_key="rollback-fail", seed=_SEED, initial=initial)
    runner = ReviewLoopRunner(
        agents=(_Agent(agent_id="agent-1", proposals_to_emit=(_action("initial"),)),),
        resolver=_Resolver(),
        max_steps=1,
        critic=_ScoreCritic(scores={"initial": 0.1, "revised": 0.1}),
        reviser=_Reviser(revised=(_action("revised"),)),
        policy=CorrectionPolicy(max_retries=1, min_score=0.5, on_fail="rollback"),
    )

    run = runner.run(spec)

    assert run.steps == ()
    assert run.final_state == initial


def test_review_loop_runner_stop_policy_stops_without_committing_rejected_attempt() -> None:
    initial = _make_state(step_index=0)
    spec = _Spec(scenario_key="stop", seed=_SEED, initial=initial)
    resolver = _Resolver()
    runner = ReviewLoopRunner(
        agents=(_Agent(agent_id="agent-1", proposals_to_emit=(_action("initial"),)),),
        resolver=resolver,
        max_steps=3,
        critic=_ScoreCritic(scores={"initial": 0.1}),
        reviser=_Reviser(revised=(_action("revised"),)),
        policy=CorrectionPolicy(max_retries=0, min_score=0.5, on_fail="stop"),
    )

    run = runner.run(spec)

    assert run.steps == ()
    assert resolver.received == []
    assert run.final_state == initial


def test_review_loop_runner_revise_policy_commits_revised_attempt_after_terminal_failure() -> None:
    initial = _make_state(step_index=0)
    spec = _Spec(scenario_key="revise", seed=_SEED, initial=initial)
    resolver = _Resolver()
    reviser = _Reviser(revised=(_action("revised"),))
    runner = ReviewLoopRunner(
        agents=(_Agent(agent_id="agent-1", proposals_to_emit=(_action("initial"),)),),
        resolver=resolver,
        max_steps=3,
        critic=_ScoreCritic(scores={"initial": 0.1}),
        reviser=reviser,
        policy=CorrectionPolicy(max_retries=0, min_score=0.5, on_fail="revise"),
    )

    run = runner.run(spec)

    assert [proposal.proposal_id for proposal in run.steps[0].proposals] == ["revised"]
    assert [proposal.proposal_id for _, proposals in resolver.received for proposal in proposals] == ["revised"]
    assert len(reviser.seen_attempts) == 1
