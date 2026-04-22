"""Frozen public surface of the ``abdp.evidence`` package."""

from __future__ import annotations

import abdp.evidence
import pytest
from abdp.evidence.audit_log import AuditLog
from abdp.evidence.claim import ClaimRecord, make_claim_record
from abdp.evidence.record import EvidenceRecord, make_evidence_record
from abdp.evidence.store import EvidenceStore

EXPECTED_PUBLIC_NAMES: tuple[str, ...] = (
    "AuditLog",
    "ClaimRecord",
    "EvidenceRecord",
    "EvidenceStore",
    "make_claim_record",
    "make_evidence_record",
)

EXPECTED_SOURCE_IDENTITY: dict[str, object] = {
    "AuditLog": AuditLog,
    "ClaimRecord": ClaimRecord,
    "EvidenceRecord": EvidenceRecord,
    "EvidenceStore": EvidenceStore,
    "make_claim_record": make_claim_record,
    "make_evidence_record": make_evidence_record,
}


def test_evidence_package_all_lists_exact_expected_symbols() -> None:
    assert isinstance(abdp.evidence.__all__, tuple)
    assert all(isinstance(name, str) for name in abdp.evidence.__all__)
    assert abdp.evidence.__all__ == EXPECTED_PUBLIC_NAMES


@pytest.mark.parametrize("name", EXPECTED_PUBLIC_NAMES)
def test_evidence_package_exposes_symbol_with_source_identity(name: str) -> None:
    assert getattr(abdp.evidence, name) is EXPECTED_SOURCE_IDENTITY[name]


def test_evidence_package_star_import_yields_exactly_the_public_surface() -> None:
    namespace: dict[str, object] = {}
    exec("from abdp.evidence import *", namespace)
    namespace.pop("__builtins__", None)
    assert sorted(namespace.keys()) == sorted(EXPECTED_PUBLIC_NAMES)


def test_evidence_package_namespace_exposes_only_approved_public_names() -> None:
    public_attrs = sorted(name for name in vars(abdp.evidence) if not name.startswith("_"))
    assert public_attrs == sorted(EXPECTED_PUBLIC_NAMES)


def test_evidence_package_has_module_docstring() -> None:
    doc = abdp.evidence.__doc__
    assert isinstance(doc, str)
    assert doc.strip()
