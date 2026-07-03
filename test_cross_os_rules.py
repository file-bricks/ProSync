"""Regression tests for ProSync cross-OS handoff rules."""

from __future__ import annotations

from cross_os_rules import find_cross_os_path_conflicts, portable_path_key


def test_portable_path_key_normalizes_separators_case_and_unicode() -> None:
    composed = "C:\\Sync\\Caf\u00e9\\Reports"
    decomposed = "c:/sync/cafe\u0301/reports/"

    assert portable_path_key(composed) == portable_path_key(decomposed)
    assert portable_path_key(composed) == "c:/sync/caf\u00e9/reports"


def test_find_cross_os_path_conflicts_groups_portable_collisions() -> None:
    conflicts = find_cross_os_path_conflicts(
        [
            "C:\\Sync\\Invoices",
            "c:/sync/invoices/",
            "/srv/prosync/Archive",
            "/srv/prosync/Archive 2026",
        ]
    )

    assert len(conflicts) == 1
    assert conflicts[0].key == "c:/sync/invoices"
    assert conflicts[0].paths == ("C:\\Sync\\Invoices", "c:/sync/invoices/")
    assert "separator" in conflicts[0].reasons
    assert "case-insensitive-key" in conflicts[0].reasons


def test_case_sensitive_mode_allows_linux_distinct_names() -> None:
    conflicts = find_cross_os_path_conflicts(
        ["Reports/Q1", "reports/q1"],
        case_sensitive=True,
    )

    assert conflicts == []


def test_case_insensitive_mode_blocks_cross_os_ambiguous_names() -> None:
    conflicts = find_cross_os_path_conflicts(["Reports/Q1", "reports/q1"])

    assert len(conflicts) == 1
    assert conflicts[0].key == "reports/q1"
