from __future__ import annotations

import dataclasses
from typing import Protocol, cast, get_args, get_origin, get_type_hints

from abdp.agents import Agent
from abdp.scenario import ActionResolver, ScenarioRunner


class _DataclassParams(Protocol):
    frozen: bool


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
