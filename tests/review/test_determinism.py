from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from abdp.agents import AgentContext, AgentDecision
from abdp.core import JsonValue, Seed
from abdp.inspector import MemoryTraceStore, TraceEvent, TraceRecorder
from abdp.review import CorrectionPolicy, ReviewAttempt, ReviewDecision, ReviewLoopRunner
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

    def decide(self, context: AgentContext[SegmentState, ParticipantState, _Action]) -> AgentDecision[_Action]:
        return _Decision(agent_id=self.agent_id, proposals=self.proposals_to_emit)


@dataclass
class _Resolver:
    def resolve(self, state: _State, proposals: tuple[_Action, ...]) -> _State:
        return _make_state(step_index=state.step_index + 1, snapshot_suffix=state.step_index + 2)


@dataclass
class _Critic:
    scores: dict[str, float]

    def evaluate(self, step: object) -> ReviewDecision:
        proposal_id = step.proposals[0].proposal_id
        return ReviewDecision(score=self.scores[proposal_id], critique=proposal_id)


@dataclass
class _Reviser:
    revised: tuple[_Action, ...]

    def revise(self, attempt: ReviewAttempt[_Action]) -> tuple[_Action, ...]:
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


def _event_tuple(event: TraceEvent) -> tuple[object, ...]:
    return (
        event.event_id,
        event.run_id,
        event.seq,
        event.step_index,
        event.event_type,
        tuple(sorted(event.attributes.items())),
        event.timestamp_ns,
        event.parent_event_id,
    )


def _execute(run_id: str) -> tuple[object, tuple[tuple[object, ...], ...]]:
    store = MemoryTraceStore()
    recorder = TraceRecorder(store=store, seed=_SEED, run_id=run_id)
    runner = ReviewLoopRunner(
        agents=(_Agent(agent_id="agent-1", proposals_to_emit=(_action("initial"),)),),
        resolver=_Resolver(),
        max_steps=1,
        critic=_Critic(scores={"initial": 0.2, "revised": 0.9}),
        reviser=_Reviser(revised=(_action("revised"),)),
        policy=CorrectionPolicy(max_retries=1, min_score=0.5, on_fail="stop"),
        recorder=recorder,
    )
    run = runner.run(_Spec(scenario_key="determinism", seed=_SEED, initial=_make_state()))
    actual_run_id = tuple(store.runs())[0]
    return run, tuple(_event_tuple(event) for event in store.query(run_id=actual_run_id))


def test_review_loop_runner_produces_byte_identical_run_and_trace_sequences() -> None:
    run_a, events_a = _execute("run-a")
    run_b, events_b = _execute("run-b")

    assert run_a == run_b
    assert events_a == events_b
