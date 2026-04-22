"""Frozen public surface of the ``abdp.scenario`` package."""

from __future__ import annotations

import sys

import abdp.scenario
import abdp.scenario.resolver  # noqa: F401
import abdp.scenario.run  # noqa: F401
import abdp.scenario.runner  # noqa: F401
import abdp.scenario.step  # noqa: F401

resolver_module = sys.modules["abdp.scenario.resolver"]
run_module = sys.modules["abdp.scenario.run"]
runner_module = sys.modules["abdp.scenario.runner"]
step_module = sys.modules["abdp.scenario.step"]

EXPECTED_PUBLIC_NAMES: tuple[str, ...] = (
    "ActionResolver",
    "ScenarioRun",
    "ScenarioRunner",
    "ScenarioStep",
)

EXPECTED_SOURCE_IDENTITY: dict[str, object] = {
    "ActionResolver": resolver_module.ActionResolver,
    "ScenarioRun": run_module.ScenarioRun,
    "ScenarioRunner": runner_module.ScenarioRunner,
    "ScenarioStep": step_module.ScenarioStep,
}

REPRESENTATIVE_INTERNAL_NAMES: list[str] = ["resolver", "run", "runner", "step"]


def test_scenario_package_all_lists_exact_expected_symbols() -> None:
    assert abdp.scenario.__all__ == EXPECTED_PUBLIC_NAMES


def test_scenario_package_exposes_each_listed_symbol_with_source_identity() -> None:
    for name in EXPECTED_PUBLIC_NAMES:
        attr = getattr(abdp.scenario, name)
        assert attr is EXPECTED_SOURCE_IDENTITY[name]


def test_scenario_package_does_not_leak_representative_internal_helpers() -> None:
    for name in REPRESENTATIVE_INTERNAL_NAMES:
        assert not hasattr(abdp.scenario, name)


def test_scenario_package_star_import_yields_exactly_the_public_surface() -> None:
    namespace: dict[str, object] = {}
    exec("from abdp.scenario import *", namespace)
    namespace.pop("__builtins__", None)
    assert sorted(namespace.keys()) == sorted(EXPECTED_PUBLIC_NAMES)


def test_scenario_package_namespace_exposes_only_approved_public_names() -> None:
    public_attrs = sorted(name for name in vars(abdp.scenario) if not name.startswith("_"))
    assert public_attrs == sorted(EXPECTED_PUBLIC_NAMES)


def test_scenario_package_has_module_docstring() -> None:
    doc = abdp.scenario.__doc__
    assert isinstance(doc, str)
    assert doc.strip()
