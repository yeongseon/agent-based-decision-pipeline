from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Protocol, cast, get_args, get_origin, get_type_hints
from uuid import UUID

from abdp.agents import Agent, AgentContext, AgentDecision
from abdp.core import JsonValue, Seed
from abdp.scenario import ActionResolver, ScenarioRun, ScenarioRunner
from abdp.simulation import (
    ParticipantState,
    SegmentState,
    SimulationState,
)
from abdp.simulation.snapshot_ref import SnapshotRef


class _DataclassParams(Protocol):
    frozen: bool


@dataclass(frozen=True, slots=True)
class _Action:
    proposal_id: str
    actor_id: str
    action_key: str
    payload: JsonValue


def _snapshot_ref(suffix: int = 1) -> SnapshotRef:
    return SnapshotRef(
        snapshot_id=UUID(int=suffix),
        tier="bronze",
        storage_key=f"snapshots/{suffix}",
    )


def _state(
    step_index: int = 0,
    pending: tuple[_Action, ...] = (),
    snapshot_suffix: int = 1,
) -> SimulationState[SegmentState, ParticipantState, _Action]:
    return SimulationState[SegmentState, ParticipantState, _Action](
        step_index=step_index,
        seed=Seed(7),
        snapshot_ref=_snapshot_ref(snapshot_suffix),
        segments=(),
        participants=(),
        pending_actions=pending,
    )


@dataclass(frozen=True, slots=True)
class _Spec:
    scenario_key: str
    seed: Seed
    initial: SimulationState[SegmentState, ParticipantState, _Action]

    def build_initial_state(
        self,
    ) -> SimulationState[SegmentState, ParticipantState, _Action]:
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
        state: SimulationState[SegmentState, ParticipantState, _Action],
        proposals: tuple[_Action, ...],
    ) -> SimulationState[SegmentState, ParticipantState, _Action]:
        self.received.append((state.step_index, proposals))
        return _state(
            step_index=state.step_index + 1,
            pending=(),
            snapshot_suffix=state.step_index + 2,
        )


def _action(suffix: str) -> _Action:
    return _Action(
        proposal_id=f"p-{suffix}",
        actor_id=f"a-{suffix}",
        action_key="noop",
        payload=None,
    )


def test_scenario_runner_is_a_frozen_slot_backed_dataclass_with_expected_fields() -> None:
    params = cast(_DataclassParams, object.__getattribute__(ScenarioRunner, "__dataclass_params__"))

    assert dataclasses.is_dataclass(ScenarioRunner)
    assert params.frozen is True
    assert "__slots__" in ScenarioRunner.__dict__

    fields = {f.name: f.type for f in dataclasses.fields(ScenarioRunner)}
    assert set(fields) == {"agents", "resolver", "max_steps"}
    assert fields["max_steps"] is int

    hints = get_type_hints(ScenarioRunner)
    agents_args = get_args(hints["agents"])
    assert get_origin(hints["agents"]) is tuple
    assert get_origin(agents_args[0]) is Agent
    assert agents_args[1] is Ellipsis
    assert get_origin(hints["resolver"]) is ActionResolver
    assert len(ScenarioRunner.__type_params__) == 3


def test_run_invokes_agents_in_order_and_merges_pending_before_emissions() -> None:
    pending = (_action("pending"),)
    initial = _state(step_index=0, pending=pending)
    spec = _Spec(scenario_key="merge-key", seed=Seed(7), initial=initial)

    a1_emit = (_action("a1"),)
    a2_emit = (_action("a2-x"), _action("a2-y"))
    agent1 = _RecordingAgent(agent_id="agent-1", proposals_to_emit=a1_emit)
    agent2 = _RecordingAgent(agent_id="agent-2", proposals_to_emit=a2_emit)
    resolver = _RecordingResolver()

    runner = ScenarioRunner[SegmentState, ParticipantState, _Action](
        agents=(agent1, agent2),
        resolver=resolver,
        max_steps=1,
    )

    run = runner.run(spec)

    assert run.scenario_key == "merge-key"
    assert run.seed == Seed(7)
    assert run.step_count == 1

    step = run.steps[0]
    assert tuple(d.agent_id for d in step.decisions) == ("agent-1", "agent-2")
    assert step.proposals == pending + a1_emit + a2_emit

    assert agent1.seen_contexts[0].agent_id == "agent-1"
    assert agent1.seen_contexts[0].scenario_key == "merge-key"
    assert agent1.seen_contexts[0].step_index == 0
    assert agent1.seen_contexts[0].seed == Seed(7)
    assert agent1.seen_contexts[0].state is initial

    assert resolver.received == [(0, pending + a1_emit + a2_emit)]
    assert run.final_state.step_index == 1


def test_run_records_empty_terminal_step_and_skips_resolver_when_no_proposals() -> None:
    initial = _state(step_index=0, pending=())
    spec = _Spec(scenario_key="quiet", seed=Seed(0), initial=initial)
    silent = _RecordingAgent(agent_id="silent", proposals_to_emit=())
    resolver = _RecordingResolver()

    runner = ScenarioRunner[SegmentState, ParticipantState, _Action](
        agents=(silent,),
        resolver=resolver,
        max_steps=5,
    )
    run = runner.run(spec)

    assert run.step_count == 1
    assert run.steps[0].proposals == ()
    assert run.steps[0].state is initial
    assert run.steps[0].decisions == (_Decision(agent_id="silent", proposals=()),)
    assert silent.seen_contexts != []
    assert silent.seen_contexts[0].agent_id == "silent"
    assert silent.seen_contexts[0].step_index == 0
    assert resolver.received == []
    assert run.final_state is initial


def test_run_stops_after_max_steps_resolutions() -> None:
    initial = _state(step_index=0, pending=())
    spec = _Spec(scenario_key="bounded", seed=Seed(0), initial=initial)
    emitter = _RecordingAgent(agent_id="emit", proposals_to_emit=(_action("e"),))
    resolver = _RecordingResolver()

    runner = ScenarioRunner[SegmentState, ParticipantState, _Action](
        agents=(emitter,),
        resolver=resolver,
        max_steps=2,
    )
    run = runner.run(spec)

    assert run.step_count == 2
    assert len(resolver.received) == 2
    assert run.final_state.step_index == 2
    assert run.steps[0].state.step_index == 0
    assert run.steps[1].state.step_index == 1


def test_run_is_deterministic_for_same_spec_agents_and_resolver() -> None:
    initial = _state(step_index=0, pending=(_action("p"),))
    spec = _Spec(scenario_key="det", seed=Seed(42), initial=initial)

    def _build_run() -> ScenarioRun[SegmentState, ParticipantState, _Action]:
        agent = _RecordingAgent(agent_id="a", proposals_to_emit=(_action("x"), _action("y")))
        resolver = _RecordingResolver()
        runner = ScenarioRunner[SegmentState, ParticipantState, _Action](
            agents=(agent,), resolver=resolver, max_steps=3
        )
        return runner.run(spec)

    assert _build_run() == _build_run()


def test_run_with_zero_max_steps_records_no_steps_and_returns_initial_state() -> None:
    initial = _state(step_index=0, pending=(_action("ignored"),))
    spec = _Spec(scenario_key="zero", seed=Seed(0), initial=initial)
    agent = _RecordingAgent(agent_id="a", proposals_to_emit=(_action("x"),))
    resolver = _RecordingResolver()

    runner = ScenarioRunner[SegmentState, ParticipantState, _Action](agents=(agent,), resolver=resolver, max_steps=0)
    run = runner.run(spec)

    assert run.step_count == 0
    assert run.final_state is initial
    assert agent.seen_contexts == []
    assert resolver.received == []
