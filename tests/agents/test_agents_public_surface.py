from __future__ import annotations

import abdp.agents
from abdp.agents.decision import AgentDecision as SourceAgentDecision

EXPECTED_PUBLIC_NAMES: tuple[str, ...] = ("AgentDecision",)

EXPECTED_SOURCE_IDENTITY: dict[str, object] = {
    "AgentDecision": SourceAgentDecision,
}

REPRESENTATIVE_INTERNAL_NAMES: list[str] = ["decision"]


def test_agents_package_all_lists_exact_expected_symbols() -> None:
    assert abdp.agents.__all__ == EXPECTED_PUBLIC_NAMES


def test_agents_package_exposes_each_listed_symbol_with_source_identity() -> None:
    assert abdp.agents.AgentDecision is EXPECTED_SOURCE_IDENTITY["AgentDecision"]


def test_agents_package_does_not_leak_representative_internal_helpers() -> None:
    for name in REPRESENTATIVE_INTERNAL_NAMES:
        assert not hasattr(abdp.agents, name)


def test_agents_package_star_import_yields_exactly_the_public_surface() -> None:
    namespace: dict[str, object] = {}
    exec("from abdp.agents import *", namespace)
    _ = namespace.pop("__builtins__", None)
    assert sorted(namespace.keys()) == sorted(EXPECTED_PUBLIC_NAMES)


def test_agents_package_namespace_exposes_only_approved_public_names() -> None:
    public_attrs = sorted(name for name in vars(abdp.agents) if not name.startswith("_"))
    assert public_attrs == sorted(EXPECTED_PUBLIC_NAMES)
