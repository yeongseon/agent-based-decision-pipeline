from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from abdp.agents import AgentContext, AgentDecision
from abdp.core import JsonValue, Seed
from abdp.evidence import InMemoryEvidenceStore, make_evidence_record
from abdp.inspector import MemoryTraceStore, TraceRecorder
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

    def decide(self, context: AgentContext[SegmentState, ParticipantState, _Action]) -> AgentDecision[_Action]:
        return _Decision(agent_id=self.agent_id, proposals=self.proposals_to_emit)


@dataclass
class _EvidenceResolver:
    evidence_store: InMemoryEvidenceStore[SegmentState, ParticipantState, _Action]

    def resolve(self, state: _State, proposals: tuple[_Action, ...]) -> _State:
        for proposal in proposals:
            self.evidence_store.record(
                make_evidence_record(
                    seed=state.seed,
                    evidence_key=proposal.proposal_id,
                    step_index=state.step_index,
                    agent_id=proposal.actor_id,
                    payload={"proposal_id": proposal.proposal_id},
                    created_at=datetime(2026, 1, 1, tzinfo=UTC),
                )
            )
        return _make_state(step_index=state.step_index + 1, snapshot_suffix=state.step_index + 2)


@dataclass
class _Critic:
    scores: dict[str, float]

    def evaluate(self, step: ScenarioStep[SegmentState, ParticipantState, _Action]) -> ReviewDecision:
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


def test_rejected_stop_attempts_stay_out_of_the_canonical_evidence_store() -> None:
    trace_store = MemoryTraceStore()
    evidence_store = InMemoryEvidenceStore[SegmentState, ParticipantState, _Action]()
    runner = ReviewLoopRunner(
        agents=(_Agent(agent_id="agent-1", proposals_to_emit=(_action("initial"),)),),
        resolver=_EvidenceResolver(evidence_store=evidence_store),
        max_steps=1,
        critic=_Critic(scores={"initial": 0.1}),
        reviser=_Reviser(revised=(_action("revised"),)),
        policy=CorrectionPolicy(max_retries=0, min_score=0.5, on_fail="stop"),
        recorder=TraceRecorder(store=trace_store, seed=_SEED, run_id="ignored"),
    )

    run = runner.run(_Spec(scenario_key="isolation-stop", seed=_SEED, initial=_make_state()))

    run_id = tuple(trace_store.runs())[0]
    attempts = tuple(trace_store.query(run_id=run_id, event_type="review.attempt"))
    assert [attempt.attributes["accepted"] for attempt in attempts] == [False]
    assert run.steps == ()
    assert evidence_store.evidence() == ()


def test_rejected_attempts_live_in_inspector_plane_but_accepted_retry_is_canonical() -> None:
    trace_store = MemoryTraceStore()
    evidence_store = InMemoryEvidenceStore[SegmentState, ParticipantState, _Action]()
    runner = ReviewLoopRunner(
        agents=(_Agent(agent_id="agent-1", proposals_to_emit=(_action("initial"),)),),
        resolver=_EvidenceResolver(evidence_store=evidence_store),
        max_steps=1,
        critic=_Critic(scores={"initial": 0.2, "revised": 0.9}),
        reviser=_Reviser(revised=(_action("revised"),)),
        policy=CorrectionPolicy(max_retries=1, min_score=0.5, on_fail="rollback"),
        recorder=TraceRecorder(store=trace_store, seed=_SEED, run_id="ignored"),
    )

    run = runner.run(_Spec(scenario_key="isolation-retry", seed=_SEED, initial=_make_state()))

    run_id = tuple(trace_store.runs())[0]
    begin_event = tuple(trace_store.query(run_id=run_id, event_type="step.begin"))[0]
    attempts = tuple(trace_store.query(run_id=run_id, event_type="review.attempt"))
    assert [attempt.attributes["accepted"] for attempt in attempts] == [False, True]
    assert all(attempt.parent_event_id == begin_event.event_id for attempt in attempts)
    assert [proposal.proposal_id for proposal in run.steps[0].proposals] == ["revised"]
    assert [record.evidence_key for record in evidence_store.evidence()] == ["revised"]
