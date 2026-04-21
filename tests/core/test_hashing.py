from __future__ import annotations

import hashlib
import json
import re
from typing import cast

import pytest
from hypothesis import given, settings, strategies as st
from hypothesis.strategies import SearchStrategy

import abdp.core.hashing as hashing_module
from abdp.core.hashing import _canonical_json_bytes, stable_hash
from abdp.core.types import JsonValue

HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def _canonical(value: JsonValue) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def json_scalar_strategy() -> SearchStrategy[JsonValue]:
    return st.one_of(
        st.none(),
        st.booleans(),
        st.integers(min_value=-(2**32), max_value=2**32),
        st.floats(allow_nan=False, allow_infinity=False, allow_subnormal=False, width=64),
        st.text(alphabet=st.characters(exclude_categories=["Cs"]), max_size=32),
    )


def json_value_strategy() -> SearchStrategy[JsonValue]:
    return st.recursive(
        json_scalar_strategy(),
        lambda children: st.one_of(
            st.lists(children, max_size=4),
            st.dictionaries(
                st.text(alphabet=st.characters(exclude_categories=["Cs"]), min_size=1, max_size=8),
                children,
                max_size=4,
            ),
        ),
        max_leaves=8,
    )


def test_hashing_module_docstring_includes_stable_hashing_contract_anchor() -> None:
    assert hashing_module.__doc__ is not None
    assert "Stable hashing contract:" in hashing_module.__doc__
    assert "not for security signing" in hashing_module.__doc__


def test_hashing_module_exposes_only_stable_hash_publicly() -> None:
    assert hashing_module.__all__ == ["stable_hash"]


def test_canonical_json_bytes_sorts_object_keys_and_omits_whitespace() -> None:
    assert _canonical_json_bytes({"b": 2, "a": 1}) == b'{"a":1,"b":2}'


def test_canonical_json_bytes_preserves_array_order() -> None:
    assert _canonical_json_bytes([3, 1, 2]) == b"[3,1,2]"


def test_canonical_json_bytes_emits_unicode_without_ascii_escaping() -> None:
    assert _canonical_json_bytes("한") == '"한"'.encode()


def test_canonical_json_bytes_rejects_non_finite_floats_directly() -> None:
    for value in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError, match=r"Out of range float values are not JSON compliant"):
            _canonical_json_bytes(value)


def test_stable_hash_returns_expected_digest_for_none() -> None:
    assert stable_hash(None) == "74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b"


def test_stable_hash_returns_expected_digest_for_known_object() -> None:
    assert stable_hash({"a": 1, "b": 2}) == "43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777"


def test_stable_hash_returns_expected_digest_for_known_array() -> None:
    assert stable_hash([1, "two", None, True]) == "7b8032fffebbc32932bc49ec84cf4527e973466f623f05770de7f39d2b66af65"


def test_stable_hash_is_independent_of_dict_insertion_order() -> None:
    a = stable_hash({"a": 1, "b": 2, "c": 3})
    b = stable_hash({"c": 3, "a": 1, "b": 2})
    c = stable_hash({"b": 2, "c": 3, "a": 1})
    assert a == b == c


def test_stable_hash_preserves_list_order() -> None:
    assert stable_hash([1, 2, 3]) != stable_hash([3, 2, 1])


def test_stable_hash_accepts_nested_json_value() -> None:
    nested: JsonValue = {"outer": [{"inner": [1, 2, {"deep": None}]}, "tail"]}
    assert stable_hash(nested) == _canonical(nested)


def test_stable_hash_accepts_unicode_string() -> None:
    value: JsonValue = {"name": "한글-μ-🚀"}
    assert stable_hash(value) == _canonical(value)


def test_stable_hash_distinguishes_int_from_float() -> None:
    assert stable_hash(1) != stable_hash(1.0)


def test_stable_hash_distinguishes_false_from_zero() -> None:
    assert stable_hash(False) != stable_hash(0)
    assert stable_hash(True) != stable_hash(1)


@pytest.mark.parametrize(
    "value",
    [
        (1, 2, 3),
        {1, 2, 3},
        b"bytes",
        object(),
    ],
)
def test_stable_hash_rejects_non_json_top_level_inputs(value: object) -> None:
    with pytest.raises(
        TypeError,
        match=rf"^value must be JSON-compatible, got {type(value).__name__}$",
    ):
        stable_hash(cast(JsonValue, value))


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_stable_hash_rejects_top_level_non_finite_floats(value: float) -> None:
    with pytest.raises(TypeError, match=r"^value must be JSON-compatible, got float$"):
        stable_hash(value)


def test_stable_hash_rejects_nested_invalid_list_member() -> None:
    bad: object = [1, 2, (3, 4)]
    with pytest.raises(TypeError, match=r"^value must be JSON-compatible, got list$"):
        stable_hash(cast(JsonValue, bad))


def test_stable_hash_rejects_nested_invalid_dict_value() -> None:
    bad: object = {"k": float("nan")}
    with pytest.raises(TypeError, match=r"^value must be JSON-compatible, got dict$"):
        stable_hash(cast(JsonValue, bad))


def test_stable_hash_rejects_self_referential_list() -> None:
    cycle: list[object] = [1, 2]
    cycle.append(cycle)
    with pytest.raises(TypeError, match=r"^value must be JSON-compatible, got list$"):
        stable_hash(cast(JsonValue, cycle))


def test_stable_hash_rejects_self_referential_dict() -> None:
    cycle: dict[str, object] = {"k": 1}
    cycle["self"] = cycle
    with pytest.raises(TypeError, match=r"^value must be JSON-compatible, got dict$"):
        stable_hash(cast(JsonValue, cycle))


def test_stable_hash_rejects_indirect_cycle() -> None:
    a: list[object] = [1]
    b: list[object] = [2, a]
    a.append(b)
    with pytest.raises(TypeError, match=r"^value must be JSON-compatible, got list$"):
        stable_hash(cast(JsonValue, a))


@given(json_value_strategy())
@settings(max_examples=100)
def test_stable_hash_matches_canonical_sha256_for_generated_json_values(value: JsonValue) -> None:
    assert stable_hash(value) == _canonical(value)


@given(
    st.lists(
        st.text(alphabet=st.characters(exclude_categories=["Cs"]), min_size=1, max_size=8),
        min_size=0,
        max_size=6,
        unique=True,
    ),
    st.randoms(use_true_random=False),
)
@settings(max_examples=50)
def test_stable_hash_is_order_invariant_for_generated_dicts(keys: list[str], rng: object) -> None:
    import random

    assert isinstance(rng, random.Random)
    pairs = [(k, i) for i, k in enumerate(keys)]
    shuffled = list(pairs)
    rng.shuffle(shuffled)
    base: dict[str, JsonValue] = dict(pairs)
    other: dict[str, JsonValue] = dict(shuffled)
    assert stable_hash(base) == stable_hash(other)


@given(json_value_strategy())
@settings(max_examples=100)
def test_stable_hash_returns_64_char_lowercase_hex_for_generated_json_values(value: JsonValue) -> None:
    digest = stable_hash(value)
    assert HEX_RE.match(digest) is not None
