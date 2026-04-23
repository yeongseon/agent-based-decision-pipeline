from __future__ import annotations

import dataclasses
from typing import Protocol, cast

import pytest

from abdp.review.policy import CorrectionPolicy


class _DataclassParams(Protocol):
    frozen: bool


def test_correction_policy_is_frozen_slot_backed_dataclass() -> None:
    params = cast(_DataclassParams, object.__getattribute__(CorrectionPolicy, "__dataclass_params__"))

    assert dataclasses.is_dataclass(CorrectionPolicy)
    assert params.frozen is True
    assert "__slots__" in CorrectionPolicy.__dict__


def test_correction_policy_declares_expected_fields() -> None:
    fields = {field.name: field.type for field in dataclasses.fields(CorrectionPolicy)}

    assert fields == {
        "max_retries": int,
        "min_score": float,
        "on_fail": "Literal['rollback', 'revise', 'stop']",
    }


def test_correction_policy_accepts_valid_inputs() -> None:
    policy = CorrectionPolicy(max_retries=2, min_score=0.75, on_fail="revise")

    assert policy.max_retries == 2
    assert policy.min_score == 0.75
    assert policy.on_fail == "revise"


@pytest.mark.parametrize("value", [-1, True])
def test_correction_policy_rejects_invalid_max_retries(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        CorrectionPolicy(max_retries=value, min_score=0.5, on_fail="stop")


@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan"), float("inf")])
def test_correction_policy_rejects_invalid_min_score(value: float) -> None:
    with pytest.raises(ValueError):
        CorrectionPolicy(max_retries=1, min_score=value, on_fail="rollback")


def test_correction_policy_rejects_unknown_on_fail_mode() -> None:
    with pytest.raises(ValueError):
        CorrectionPolicy(max_retries=1, min_score=0.5, on_fail="unknown")
