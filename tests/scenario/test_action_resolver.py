from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import get_args, get_origin, get_type_hints
from uuid import uuid4

from abdp.scenario import ActionResolver
from abdp.core.types import Seed
from abdp.simulation import SimulationState
from abdp.simulation.action_proposal import ActionProposal
from abdp.simulation.participant_state import ParticipantState
from abdp.simulation.segment_state import SegmentState
from abdp.simulation.snapshot_ref import SnapshotRef


def test_action_resolver_is_runtime_checkable_protocol() -> None:
    assert getattr(ActionResolver, "_is_protocol", False) is True
    assert getattr(ActionResolver, "_is_runtime_protocol", False) is True


def test_action_resolver_declares_expected_type_parameters() -> None:
    assert tuple(param.__name__ for param in ActionResolver.__type_params__) == ("S", "P", "A")


def test_action_resolver_declares_expected_resolve_signature() -> None:
    signature = inspect.signature(ActionResolver.resolve)
    hints = get_type_hints(ActionResolver.resolve)
    type_params = ActionResolver.__type_params__
    expected_simulation_state_args = tuple(type_params[: len(SimulationState.__type_params__)])

    assert tuple(signature.parameters) == ("self", "state", "proposals")

    state_annotation = hints["state"]
    proposals_annotation = hints["proposals"]
    return_annotation = hints["return"]

    assert get_origin(state_annotation) is SimulationState
    assert get_args(state_annotation) == expected_simulation_state_args
    assert get_origin(proposals_annotation) is tuple
    assert get_args(proposals_annotation) == (type_params[2], Ellipsis)
    assert get_origin(return_annotation) is SimulationState
    assert get_args(return_annotation) == expected_simulation_state_args


@dataclass(frozen=True, slots=True)
class ExampleSegment:
    segment_id: str
    participant_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ExampleParticipant:
    participant_id: str


@dataclass(frozen=True, slots=True)
class ExampleAction:
    proposal_id: str
    actor_id: str
    action_key: str
    payload: str


class ExampleResolver:
    def resolve(
        self,
        state: SimulationState[ExampleSegment, ExampleParticipant, ExampleAction],
        proposals: tuple[ExampleAction, ...],
    ) -> SimulationState[ExampleSegment, ExampleParticipant, ExampleAction]:
        return state


def test_concrete_resolver_satisfies_action_resolver_protocol() -> None:
    segment = ExampleSegment(segment_id="segment-1", participant_ids=("participant-1",))
    participant = ExampleParticipant(participant_id="participant-1")
    action = ExampleAction(
        proposal_id="proposal-1",
        actor_id="participant-1",
        action_key="hold",
        payload="{}",
    )
    state = SimulationState[ExampleSegment, ExampleParticipant, ExampleAction](
        step_index=0,
        seed=Seed(1),
        snapshot_ref=SnapshotRef(
            snapshot_id=uuid4(),
            tier="bronze",
            storage_key="snapshots/1.json",
        ),
        segments=(segment,),
        participants=(participant,),
        pending_actions=(action,),
    )
    resolver = ExampleResolver()

    assert isinstance(segment, SegmentState)
    assert isinstance(participant, ParticipantState)
    assert isinstance(action, ActionProposal)
    assert resolver.resolve(state, (action,)) is state
    assert isinstance(resolver, ActionResolver)
