from __future__ import annotations

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

import pytest

from abdp.agents import AgentContext, AgentDecision
from abdp.core import JsonValue, Seed
from abdp.simulation import (
    ParticipantState,
    SegmentState,
    SimulationState,
)
from abdp.simulation.snapshot_ref import SnapshotRef


@dataclass(frozen=True, slots=True)
class _Action:
    proposal_id: str
    actor_id: str
    action_key: str
    payload: JsonValue


_State = SimulationState[SegmentState, ParticipantState, _Action]


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
        return _make_state(
            step_index=state.step_index + 1,
            pending=(),
            snapshot_suffix=state.step_index + 2,
        )


_DEFAULT_SEED: Seed = Seed(7)


def _make_snapshot_ref(suffix: int = 1) -> SnapshotRef:
    return SnapshotRef(
        snapshot_id=UUID(int=suffix),
        tier="bronze",
        storage_key=f"snapshots/{suffix}",
    )


def _make_state(
    *,
    step_index: int = 0,
    pending: tuple[_Action, ...] = (),
    snapshot_suffix: int = 1,
    seed: Seed = _DEFAULT_SEED,
) -> _State:
    return SimulationState[SegmentState, ParticipantState, _Action](
        step_index=step_index,
        seed=seed,
        snapshot_ref=_make_snapshot_ref(snapshot_suffix),
        segments=(),
        participants=(),
        pending_actions=pending,
    )


def _make_action(suffix: str) -> _Action:
    return _Action(
        proposal_id=f"p-{suffix}",
        actor_id=f"a-{suffix}",
        action_key="noop",
        payload=None,
    )


@pytest.fixture
def make_action() -> Callable[[str], _Action]:
    return _make_action


@pytest.fixture
def make_state() -> Callable[..., _State]:
    return _make_state


@pytest.fixture
def make_spec() -> type[_Spec]:
    return _Spec


@pytest.fixture
def make_recording_agent() -> type[_RecordingAgent]:
    return _RecordingAgent


@pytest.fixture
def make_recording_resolver() -> type[_RecordingResolver]:
    return _RecordingResolver


@pytest.fixture
def decision_cls() -> type[_Decision]:
    return _Decision
