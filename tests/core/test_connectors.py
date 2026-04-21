"""Conformance tests for the core connector protocol contract."""

from __future__ import annotations

from typing import assert_type

from abdp.core import connectors
from abdp.core.connectors import Connector


class _ValidConnector:
    @property
    def name(self) -> str:
        return "dummy"

    def send(self, request: int) -> str:
        return str(request)


class _MissingSend:
    @property
    def name(self) -> str:
        return "no-send"


class _MissingName:
    def send(self, request: int) -> str:
        return str(request)


def test_connectors_module_exports_connector() -> None:
    assert connectors.__all__ == ["Connector"]
    assert connectors.Connector is Connector


def test_connector_is_protocol() -> None:
    assert getattr(Connector, "_is_protocol", False) is True


def test_connector_is_runtime_checkable_and_accepts_minimal_structural_impl() -> None:
    dummy = _ValidConnector()
    assert isinstance(dummy, Connector) is True
    connector: Connector[int, str] = dummy
    response = connector.send(1)
    assert_type(response, str)
    assert response == "1"
    assert connector.name == "dummy"


def test_connector_runtime_check_rejects_missing_send() -> None:
    assert isinstance(_MissingSend(), Connector) is False


def test_connector_runtime_check_rejects_missing_name() -> None:
    assert isinstance(_MissingName(), Connector) is False
