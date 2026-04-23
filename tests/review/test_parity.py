from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from uuid import UUID

from abdp.agents import AgentContext, AgentDecision
from abdp.core import JsonValue, Seed
from abdp.inspector import MemoryTraceStore, TraceRecorder
from abdp.review import CorrectionPolicy, ReviewDecision, ReviewLoopRunner
from abdp.scenario import ScenarioRunner
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
class _RecordingAgent:
    agent_id: str
    proposals_to_emit: tuple[_Action, ...]
    seen_contexts: list[AgentContext[SegmentState, ParticipantState, _Action]] = dataclasses.field(default_factory=list)

    def decide(
        self,
        context: AgentContext[SegmentState, ParticipantState, _Action],
    ) -> AgentDecision[_Action]:
        self.seen_contexts.append(context)
        return _Decision(agent_id=self.agent_id, proposals=self.proposals_to_emit)


@dataclass
class _RecordingResolver:
    received: list[tuple[int, tuple[_Action, ...]]] = dataclasses.field(default_factory=list)

    def resolve(
        self,
        state: _State,
        proposals: tuple[_Action, ...],
    ) -> _State:
        self.received.append((state.step_index, proposals))
        return _make_state(step_index=state.step_index + 1, pending=(), snapshot_suffix=state.step_index + 2)


@dataclass(frozen=True, slots=True)
class _AcceptingCritic:
    def evaluate(self, step: object) -> ReviewDecision:
        return ReviewDecision(score=1.0, critique="accept")


@dataclass(frozen=True, slots=True)
class _PassThroughReviser:
    def revise(self, attempt: object) -> tuple[_Action, ...]:
        return ()


def _make_state(
    *,
    step_index: int = 0,
    pending: tuple[_Action, ...] = (),
    snapshot_suffix: int = 1,
    seed: Seed = _SEED,
) -> _State:
    return SimulationState[SegmentState, ParticipantState, _Action](
        step_index=step_index,
        seed=seed,
        snapshot_ref=SnapshotRef(
            snapshot_id=UUID(int=snapshot_suffix), tier="bronze", storage_key=f"snapshots/{snapshot_suffix}"
        ),
        segments=(),
        participants=(),
        pending_actions=pending,
    )


def _make_action(suffix: str) -> _Action:
    return _Action(proposal_id=f"p-{suffix}", actor_id=f"a-{suffix}", action_key="noop", payload=None)


def test_review_loop_runner_with_zero_retries_matches_scenario_runner() -> None:
    initial = _make_state(step_index=0, pending=())
    spec = _Spec(scenario_key="parity", seed=_SEED, initial=initial)
    agent = _RecordingAgent(agent_id="agent-1", proposals_to_emit=(_make_action("x"),))
    resolver = _RecordingResolver()
    scenario_runner = ScenarioRunner(agents=(agent,), resolver=resolver, max_steps=3)
    review_runner = ReviewLoopRunner(
        agents=(agent,),
        resolver=resolver,
        max_steps=3,
        critic=_AcceptingCritic(),
        reviser=_PassThroughReviser(),
        policy=CorrectionPolicy(max_retries=0, min_score=0.0, on_fail="stop"),
    )

    assert review_runner.run(spec) == scenario_runner.run(spec)


def test_review_loop_runner_matches_scenario_runner_when_no_proposals_and_recorder_enabled() -> None:
    initial = _make_state(step_index=0, pending=())
    spec = _Spec(scenario_key="parity-empty", seed=_SEED, initial=initial)
    agent = _RecordingAgent(agent_id="agent-1", proposals_to_emit=())
    resolver = _RecordingResolver()
    recorder = TraceRecorder(store=MemoryTraceStore(), seed=_SEED, run_id="review-parity-empty")
    scenario_runner = ScenarioRunner(agents=(agent,), resolver=resolver, max_steps=3, recorder=recorder)
    review_runner = ReviewLoopRunner(
        agents=(agent,),
        resolver=resolver,
        max_steps=3,
        critic=_AcceptingCritic(),
        reviser=_PassThroughReviser(),
        policy=CorrectionPolicy(max_retries=0, min_score=0.0, on_fail="stop"),
        recorder=recorder,
    )

    assert review_runner.run(spec) == scenario_runner.run(spec)


def test_review_loop_runner_matches_scenario_runner_when_max_steps_is_zero() -> None:
    initial = _make_state(step_index=0, pending=())
    spec = _Spec(scenario_key="parity-zero", seed=_SEED, initial=initial)
    agent = _RecordingAgent(agent_id="agent-1", proposals_to_emit=(_make_action("x"),))
    resolver = _RecordingResolver()
    scenario_runner = ScenarioRunner(agents=(agent,), resolver=resolver, max_steps=0)
    review_runner = ReviewLoopRunner(
        agents=(agent,),
        resolver=resolver,
        max_steps=0,
        critic=_AcceptingCritic(),
        reviser=_PassThroughReviser(),
        policy=CorrectionPolicy(max_retries=0, min_score=0.0, on_fail="stop"),
    )

    assert review_runner.run(spec) == scenario_runner.run(spec)
