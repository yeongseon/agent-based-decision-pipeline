from __future__ import annotations

from datetime import datetime

import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import SearchStrategy

from abdp.core.types import (
    JsonPrimitive,
    JsonValue,
    Seed,
    is_json_value,
    validate_seed,
)

UINT32_MAX = 2**32 - 1


def json_primitive_strategy() -> SearchStrategy[JsonPrimitive]:
    return st.one_of(
        st.none(),
        st.booleans(),
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(),
    )


def json_value_strategy() -> SearchStrategy[JsonValue]:
    return st.recursive(
        json_primitive_strategy(),
        lambda children: st.one_of(
            st.lists(children),
            st.dictionaries(st.text(), children),
        ),
        max_leaves=20,
    )


def test_validate_seed_accepts_uint32_bounds() -> None:
    assert validate_seed(0) == 0
    assert validate_seed(1) == 1
    assert validate_seed(UINT32_MAX) == UINT32_MAX


def test_validate_seed_rejects_negative_integers() -> None:
    with pytest.raises(ValueError, match=r"Seed must be >= 0, got -1"):
        validate_seed(-1)


def test_validate_seed_rejects_values_above_uint32_max() -> None:
    with pytest.raises(ValueError, match=rf"Seed must be <= {UINT32_MAX}, got {UINT32_MAX + 1}"):
        validate_seed(UINT32_MAX + 1)


@pytest.mark.parametrize(
    ("value", "type_name"),
    [("1", "str"), (1.0, "float"), (None, "NoneType"), (object(), "object"), ([0], "list")],
)
def test_validate_seed_rejects_non_integer_inputs(value: object, type_name: str) -> None:
    with pytest.raises(TypeError, match=rf"Seed must be a non-bool int, got {type_name}"):
        validate_seed(value)


@pytest.mark.parametrize("value", [True, False])
def test_validate_seed_rejects_bool_values(value: bool) -> None:
    with pytest.raises(TypeError, match=r"Seed must be a non-bool int, got bool"):
        validate_seed(value)


def test_seed_newtype_is_runtime_identity_without_validation() -> None:
    assert Seed(0) == 0
    assert Seed(-1) == -1


@pytest.mark.parametrize(
    "value",
    [None, False, True, "", "text", 0, 1, -1, 0.0, -1.25],
)
def test_is_json_value_accepts_json_primitives(value: object) -> None:
    assert is_json_value(value) is True


def test_is_json_value_accepts_empty_containers() -> None:
    assert is_json_value([]) is True
    assert is_json_value({}) is True


@given(json_value_strategy())
def test_is_json_value_accepts_generated_nested_json_values(value: JsonValue) -> None:
    assert is_json_value(value) is True


@pytest.mark.parametrize(
    "value",
    [
        object(),
        datetime(2024, 1, 1),
        {1, 2},
        b"bytes",
        (1, 2),
        {1: "x"},
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_is_json_value_rejects_non_json_runtime_objects(value: object) -> None:
    assert is_json_value(value) is False


def test_is_json_value_rejects_list_with_invalid_member() -> None:
    assert is_json_value(["ok", object()]) is False
    assert is_json_value([1, (2, 3)]) is False


def test_is_json_value_rejects_dict_with_non_string_key() -> None:
    assert is_json_value({1: "ok"}) is False
    assert is_json_value({None: "ok"}) is False


def test_is_json_value_rejects_dict_with_invalid_value() -> None:
    assert is_json_value({"ok": object()}) is False
    assert is_json_value({"ok": float("nan")}) is False


def test_is_json_value_accepts_nested_valid_structure() -> None:
    nested: object = {"a": [1, 2, {"b": None, "c": [True, "x", 1.5]}], "d": {}}
    assert is_json_value(nested) is True


def test_is_json_value_rejects_nested_invalid_structure() -> None:
    nested: object = {"a": [1, 2, {"b": None, "c": [True, "x", float("inf")]}]}
    assert is_json_value(nested) is False
