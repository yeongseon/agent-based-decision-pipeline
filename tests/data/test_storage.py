from __future__ import annotations

from typing import assert_type

from abdp.data import storage
from abdp.data.storage import StorageProtocol


class _ValidStorage:
    def __init__(self) -> None:
        self._items: dict[str, bytes] = {}

    def write_bytes(self, key: str, data: bytes) -> None:
        self._items[key] = data

    def read_bytes(self, key: str) -> bytes:
        return self._items[key]

    def exists(self, key: str) -> bool:
        return key in self._items


class _MissingWriteBytes:
    def read_bytes(self, key: str) -> bytes:
        return b""

    def exists(self, key: str) -> bool:
        return False


class _MissingReadBytes:
    def write_bytes(self, key: str, data: bytes) -> None:
        return None

    def exists(self, key: str) -> bool:
        return False


class _MissingExists:
    def write_bytes(self, key: str, data: bytes) -> None:
        return None

    def read_bytes(self, key: str) -> bytes:
        return b""


def test_storage_module_exports_storage_protocol() -> None:
    assert storage.__all__ == ["StorageProtocol"]
    assert storage.StorageProtocol is StorageProtocol


def test_storage_protocol_is_protocol() -> None:
    assert getattr(StorageProtocol, "_is_protocol", False) is True


def test_storage_protocol_is_runtime_checkable_and_accepts_minimal_structural_impl() -> None:
    dummy = _ValidStorage()
    assert isinstance(dummy, StorageProtocol) is True
    storage_impl: StorageProtocol = dummy
    storage_impl.write_bytes("manifest.json", b"{}")
    assert storage_impl.exists("manifest.json") is True
    data = storage_impl.read_bytes("manifest.json")
    assert_type(data, bytes)
    assert data == b"{}"


def test_storage_protocol_runtime_check_rejects_missing_write_bytes() -> None:
    assert isinstance(_MissingWriteBytes(), StorageProtocol) is False


def test_storage_protocol_runtime_check_rejects_missing_read_bytes() -> None:
    assert isinstance(_MissingReadBytes(), StorageProtocol) is False


def test_storage_protocol_runtime_check_rejects_missing_exists() -> None:
    assert isinstance(_MissingExists(), StorageProtocol) is False
