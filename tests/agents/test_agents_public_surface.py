"""Frozen public surface of the ``abdp.agents`` package."""

from __future__ import annotations

import sys

import abdp.agents
import abdp.agents.agent  # noqa: F401
import abdp.agents.context  # noqa: F401
import abdp.agents.decision  # noqa: F401

agent_module = sys.modules["abdp.agents.agent"]
context_module = sys.modules["abdp.agents.context"]
decision_module = sys.modules["abdp.agents.decision"]

EXPECTED_PUBLIC_NAMES: tuple[str, ...] = ("Agent", "AgentContext", "AgentDecision")

EXPECTED_SOURCE_IDENTITY: dict[str, object] = {
    "Agent": agent_module.Agent,
    "AgentContext": context_module.AgentContext,
    "AgentDecision": decision_module.AgentDecision,
}

REPRESENTATIVE_INTERNAL_NAMES: list[str] = ["agent", "context", "decision"]


def test_agents_package_all_lists_exact_expected_symbols() -> None:
    assert abdp.agents.__all__ == EXPECTED_PUBLIC_NAMES


def test_agents_package_exposes_each_listed_symbol_with_source_identity() -> None:
    for name in EXPECTED_PUBLIC_NAMES:
        attr = getattr(abdp.agents, name)
        assert attr is EXPECTED_SOURCE_IDENTITY[name]


def test_agents_package_does_not_leak_representative_internal_helpers() -> None:
    for name in REPRESENTATIVE_INTERNAL_NAMES:
        assert not hasattr(abdp.agents, name)


def test_agents_package_star_import_yields_exactly_the_public_surface() -> None:
    namespace: dict[str, object] = {}
    exec("from abdp.agents import *", namespace)
    namespace.pop("__builtins__", None)
    assert sorted(namespace.keys()) == sorted(EXPECTED_PUBLIC_NAMES)


def test_agents_package_namespace_exposes_only_approved_public_names() -> None:
    public_attrs = sorted(name for name in vars(abdp.agents) if not name.startswith("_"))
    assert public_attrs == sorted(EXPECTED_PUBLIC_NAMES)


def test_agents_package_has_module_docstring() -> None:
    doc = abdp.agents.__doc__
    assert isinstance(doc, str)
    assert doc.strip()
