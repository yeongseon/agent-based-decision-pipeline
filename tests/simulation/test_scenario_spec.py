"""Conformance tests for the scenario spec protocol contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import assert_type
from uuid import UUID

from abdp.core.types import JsonValue, Seed
from abdp.simulation import scenario_spec
from abdp.simulation.scenario_spec import ScenarioSpec
from abdp.simulation.snapshot_ref import SnapshotRef
from abdp.simulation.state import SimulationState

_SNAPSHOT_ID = UUID("00000000-0000-0000-0000-000000000001")
_SEED = Seed(7)
_STORAGE_KEY = "snapshots/abc"


def _make_snapshot_ref() -> SnapshotRef:
    return SnapshotRef(snapshot_id=_SNAPSHOT_ID, tier="bronze", storage_key=_STORAGE_KEY)


@dataclass(frozen=True, slots=True, kw_only=True)
class _Participant:
    participant_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class _Segment:
    segment_id: str
    participant_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class _Action:
    proposal_id: str
    actor_id: str
    action_key: str
    payload: JsonValue


def _make_initial_state(
    *,
    seed: Seed = _SEED,
) -> SimulationState[_Segment, _Participant, _Action]:
    participant = _Participant(participant_id="p1")
    segment = _Segment(segment_id="s1", participant_ids=("p1",))
    action = _Action(proposal_id="prop-1", actor_id="p1", action_key="advance", payload=1)
    return SimulationState[_Segment, _Participant, _Action](
        step_index=0,
        seed=seed,
        snapshot_ref=_make_snapshot_ref(),
        segments=(segment,),
        participants=(participant,),
        pending_actions=(action,),
    )


class _ValidImpl:
    def __init__(self, scenario_key: str, seed: Seed) -> None:
        self.scenario_key = scenario_key
        self.seed = seed

    def build_initial_state(self) -> SimulationState[_Segment, _Participant, _Action]:
        return _make_initial_state(seed=self.seed)


class _MissingScenarioKey:
    def __init__(self) -> None:
        self.seed = _SEED

    def build_initial_state(self) -> SimulationState[_Segment, _Participant, _Action]:
        return _make_initial_state(seed=self.seed)


class _MissingSeed:
    def __init__(self) -> None:
        self.scenario_key = "baseline"

    def build_initial_state(self) -> SimulationState[_Segment, _Participant, _Action]:
        return _make_initial_state()


class _MissingBuildInitialState:
    def __init__(self) -> None:
        self.scenario_key = "baseline"
        self.seed = _SEED


def _public_protocol_members(proto: type) -> set[str]:
    return {
        name
        for name, value in proto.__dict__.items()
        if not name.startswith("_") and (callable(value) or isinstance(value, property))
    }


def test_scenario_spec_module_docstring_includes_contract_anchor() -> None:
    doc = scenario_spec.__doc__ or ""
    assert "Scenario spec protocol contract:" in doc
    assert "minimal seed-aware scenario contract" in doc
    assert "scenario_key: str" in doc
    assert "seed: Seed" in doc
    assert "build_initial_state()" in doc
    assert "neutral scenario discriminator" in doc
    assert "Runtime protocol checks are shallow" in doc
    assert "do not validate attribute types or method signatures" in doc
    assert "The protocol does not require a stored field, a property setter, or mutation semantics" in doc
    assert ("No guarantees about scenario-key uniqueness, determinism beyond seed carriage,") in doc
    assert "validation, persistence, serialization, or thread safety." in doc


def test_scenario_spec_module_exports_public_symbols_only() -> None:
    assert scenario_spec.__all__ == ["ScenarioSpec"]
    assert scenario_spec.ScenarioSpec is ScenarioSpec


def test_scenario_spec_is_protocol() -> None:
    assert getattr(ScenarioSpec, "_is_protocol", False) is True


def test_scenario_spec_class_docstring_is_omitted_for_pure_protocol_exemplar() -> None:
    assert ScenarioSpec.__doc__ is None


def test_scenario_spec_runtime_checkable_accepts_minimal_valid_impl() -> None:
    instance = _ValidImpl("baseline", _SEED)
    assert isinstance(instance, ScenarioSpec) is True
    spec: ScenarioSpec[_Segment, _Participant, _Action] = instance
    assert_type(spec.scenario_key, str)
    assert_type(spec.seed, Seed)
    state = spec.build_initial_state()
    assert_type(state, SimulationState[_Segment, _Participant, _Action])
    assert spec.scenario_key == "baseline"
    assert spec.seed == _SEED
    assert isinstance(state, SimulationState) is True
    assert state.step_index == 0
    assert state.seed == _SEED


def test_scenario_spec_runtime_checkable_rejects_missing_scenario_key() -> None:
    assert isinstance(_MissingScenarioKey(), ScenarioSpec) is False


def test_scenario_spec_runtime_checkable_rejects_missing_seed() -> None:
    assert isinstance(_MissingSeed(), ScenarioSpec) is False


def test_scenario_spec_runtime_checkable_rejects_missing_build_initial_state() -> None:
    assert isinstance(_MissingBuildInitialState(), ScenarioSpec) is False


def test_scenario_spec_contract_is_identity_seed_and_builder_only() -> None:
    assert _public_protocol_members(ScenarioSpec) == {
        "scenario_key",
        "seed",
        "build_initial_state",
    }
