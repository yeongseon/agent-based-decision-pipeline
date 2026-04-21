from __future__ import annotations

from typing import cast
from uuid import NAMESPACE_DNS, NAMESPACE_OID, NAMESPACE_URL, UUID, uuid5

import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import SearchStrategy

from abdp.core.ids import deterministic_uuid, parse_uuid
from abdp.core.types import Seed, validate_seed

UINT32_MAX = 2**32 - 1


def seed_strategy() -> SearchStrategy[Seed]:
    return st.integers(min_value=0, max_value=UINT32_MAX).map(validate_seed)


def name_strategy() -> SearchStrategy[str]:
    return st.text(
        alphabet=st.characters(exclude_categories=["Cs"]),
        max_size=256,
    )


def test_deterministic_uuid_returns_expected_uuid_for_known_inputs() -> None:
    result = deterministic_uuid(Seed(42), NAMESPACE_URL, "agent-1")
    assert result == UUID("7039efdf-fc9c-5fb8-b29f-b650f56485ff")
    assert result.version == 5


def test_deterministic_uuid_is_repeatable_for_same_inputs() -> None:
    first = deterministic_uuid(Seed(123), NAMESPACE_DNS, "node")
    second = deterministic_uuid(Seed(123), NAMESPACE_DNS, "node")
    assert first == second


def test_deterministic_uuid_changes_when_seed_changes() -> None:
    a = deterministic_uuid(Seed(1), NAMESPACE_DNS, "node")
    b = deterministic_uuid(Seed(2), NAMESPACE_DNS, "node")
    assert a != b


def test_deterministic_uuid_changes_when_namespace_changes() -> None:
    a = deterministic_uuid(Seed(1), NAMESPACE_DNS, "node")
    b = deterministic_uuid(Seed(1), NAMESPACE_URL, "node")
    assert a != b


def test_deterministic_uuid_changes_when_name_changes() -> None:
    a = deterministic_uuid(Seed(1), NAMESPACE_DNS, "node-a")
    b = deterministic_uuid(Seed(1), NAMESPACE_DNS, "node-b")
    assert a != b


def test_deterministic_uuid_accepts_empty_name() -> None:
    result = deterministic_uuid(Seed(0), NAMESPACE_URL, "")
    assert result == UUID("3dd002d5-9f12-5f2c-94c9-2b52bd5a8669")


def test_deterministic_uuid_accepts_unicode_name() -> None:
    result = deterministic_uuid(Seed(7), NAMESPACE_DNS, "한글-μ-🚀")
    assert result == UUID("6cdcf97e-ab53-5897-8b41-3e6c7d03705b")


def test_deterministic_uuid_accepts_long_name() -> None:
    long_name = "x" * 4096
    a = deterministic_uuid(Seed(1), NAMESPACE_DNS, long_name)
    b = deterministic_uuid(Seed(1), NAMESPACE_DNS, long_name)
    assert a == b
    assert a == uuid5(NAMESPACE_DNS, f"1\0{long_name}")


@pytest.mark.parametrize(
    ("seed_value", "exc", "match"),
    [
        (True, TypeError, r"^Seed must be a non-bool int, got bool$"),
        (-1, ValueError, r"^Seed must be >= 0, got -1$"),
        (UINT32_MAX + 1, ValueError, rf"^Seed must be <= {UINT32_MAX}, got {UINT32_MAX + 1}$"),
    ],
)
def test_deterministic_uuid_rejects_invalid_seed(seed_value: object, exc: type[Exception], match: str) -> None:
    with pytest.raises(exc, match=match):
        deterministic_uuid(cast(Seed, seed_value), NAMESPACE_DNS, "node")


def test_deterministic_uuid_rejects_non_uuid_namespace() -> None:
    with pytest.raises(TypeError, match=r"^namespace must be UUID, got str$"):
        deterministic_uuid(Seed(1), cast(UUID, "not-a-uuid"), "node")


def test_deterministic_uuid_rejects_non_string_name() -> None:
    with pytest.raises(TypeError, match=r"^name must be str, got int$"):
        deterministic_uuid(Seed(1), NAMESPACE_DNS, cast(str, 7))


@given(seed_strategy(), st.uuids(), name_strategy())
def test_deterministic_uuid_matches_contract_for_valid_inputs(seed: Seed, namespace: UUID, name: str) -> None:
    expected = uuid5(namespace, f"{int(seed)}\0{name}")
    result = deterministic_uuid(seed, namespace, name)
    assert result == expected
    assert deterministic_uuid(seed, namespace, name) == result
    assert result.version == 5


def test_parse_uuid_round_trips_canonical_text() -> None:
    text = "12345678-1234-5678-1234-567812345678"
    result = parse_uuid(text)
    assert result == UUID(text)
    assert str(result) == text


@pytest.mark.parametrize(
    "text",
    [
        "12345678123456781234567812345678",
        "{12345678-1234-5678-1234-567812345678}",
        "urn:uuid:12345678-1234-5678-1234-567812345678",
        "12345678-1234-5678-1234-567812345678".upper(),
    ],
)
def test_parse_uuid_accepts_non_canonical_valid_forms(text: str) -> None:
    expected = UUID("12345678-1234-5678-1234-567812345678")
    assert parse_uuid(text) == expected


def test_parse_uuid_accepts_valid_non_v5_uuid() -> None:
    text = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    assert parse_uuid(text) == UUID(text)


@pytest.mark.parametrize(
    "text",
    [
        "",
        "not-a-uuid",
        " 12345678-1234-5678-1234-567812345678",
        "12345678-1234-5678-1234-567812345678 ",
    ],
)
def test_parse_uuid_rejects_invalid_uuid_text(text: str) -> None:
    with pytest.raises(ValueError, match=rf"^Invalid UUID string: {text!r}$"):
        parse_uuid(text)


def test_parse_uuid_rejects_non_string_input() -> None:
    with pytest.raises(TypeError, match=r"^UUID value must be str, got int$"):
        parse_uuid(cast(str, 7))


def test_parse_uuid_works_for_namespace_constants() -> None:
    for ns in (NAMESPACE_DNS, NAMESPACE_URL, NAMESPACE_OID):
        assert parse_uuid(str(ns)) == ns
