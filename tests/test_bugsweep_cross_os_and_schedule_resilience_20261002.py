"""Hermetic regression tests for Cross-OS path rules and calendar schedule resilience.

Tests cover:
1. describe_path_normalization: clean paths must not be flagged with 'redundant-segments'.
2. describe_path_normalization: repeated slashes, trailing slashes, whitespace and dot-segments
   are accurately recognized as 'redundant-segments'.
3. find_cross_os_path_conflicts: case-only path differences do not produce spurious 'redundant-segments'.
4. portable_path_key: empty/None path yields empty string and does not falsely collide with '.'.
5. parse_weekdays: English 2-letter codes (tu, we, th, su).
6. parse_weekdays: Spanish names (lunes, martes, etc.) and group aliases (laborables, fin de semana).
7. parse_weekdays: range syntax support (mon-wed, 1-4, fri-mon wrap-around).
8. parse_weekdays: compound group aliases in comma-separated strings and iterables (workdays,sat).
9. parse_weekdays: boolean rejection guard (booleans are not treated as weekday ints 0/1).
10. ConfigManager._portable_autosync: mixed types in weekdays list do not crash sorting.
11. AutosyncController._start_daily_timer: catches RuntimeError safely and logs warning.
"""

from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo
import importlib.util
import pytest
from PySide6.QtCore import QCoreApplication

from cross_os_rules import (
    describe_path_normalization,
    find_cross_os_path_conflicts,
    portable_path_key,
)
from schedule_time import (
    WEEKDAY_ALIASES,
    WEEKDAY_GROUPS,
    next_daily_run,
    parse_weekdays,
)

root_dir = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "prosync_v31",
    str(root_dir / "ProSyncStart_V3.1.py"),
)
prosync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prosync)
ConnectionScheduler = prosync.ConnectionScheduler
ConfigManager = prosync.ConfigManager


@pytest.fixture(autouse=True)
def ensure_qapp():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


BERLIN = ZoneInfo("Europe/Berlin")


# --- 1. Clean paths do not produce 'redundant-segments' ---
def test_describe_path_normalization_clean_path_no_redundant_segments() -> None:
    for path in ("docs/readme.txt", "src/core/main.py", "invoices/2026/01.pdf", "file.txt", "a/b/c"):
        reasons = describe_path_normalization(path)
        assert "redundant-segments" not in reasons, f"spurious redundant-segments for {path}: {reasons}"


# --- 2. Genuine redundant segments are correctly identified ---
def test_describe_path_normalization_redundant_segments_detected() -> None:
    test_cases = [
        ("docs//readme.txt", "repeated slashes"),
        ("docs/readme.txt/", "trailing slash on file"),
        ("folder/subfolder/", "trailing slash on directory"),
        ("  docs/readme.txt", "leading whitespace"),
        ("docs/readme.txt  ", "trailing whitespace"),
        ("docs/./readme.txt", "embedded dot segment"),
        ("./docs/readme.txt", "leading dot segment"),
        ("docs/readme.txt/.", "trailing dot segment"),
    ]
    for path, desc in test_cases:
        reasons = describe_path_normalization(path)
        assert "redundant-segments" in reasons, f"expected redundant-segments for {desc} ({path}): {reasons}"


# --- 3. Case-only conflict does not have 'redundant-segments' ---
def test_find_cross_os_path_conflicts_case_only_has_no_redundant_segments() -> None:
    conflicts = find_cross_os_path_conflicts(["folder/A", "folder/a"])
    assert len(conflicts) == 1
    assert conflicts[0].key == "folder/a"
    assert "case" in conflicts[0].reasons
    assert "case-insensitive-key" in conflicts[0].reasons
    assert "redundant-segments" not in conflicts[0].reasons


# --- 4. Empty/None path does not collide with '.' ---
def test_portable_path_key_empty_and_none() -> None:
    assert portable_path_key("") == ""
    assert portable_path_key(None) == ""
    assert portable_path_key("   ") == ""
    assert portable_path_key(".") == "."
    conflicts = find_cross_os_path_conflicts(["", "."])
    assert len(conflicts) == 0


# --- 5. English 2-letter codes ---
def test_parse_weekdays_english_2letter_codes() -> None:
    assert parse_weekdays("mo,tu,we,th,fr,sa,su") == {0, 1, 2, 3, 4, 5, 6}
    assert parse_weekdays(["tu", "th"]) == {1, 3}
    assert parse_weekdays("we,su") == {2, 6}


# --- 6. Spanish names and groups ---
def test_parse_weekdays_spanish_names_and_groups() -> None:
    assert parse_weekdays("lunes,martes,miercoles,jueves,viernes") == {0, 1, 2, 3, 4}
    assert parse_weekdays("lunes,martes,miércoles,jueves,viernes") == {0, 1, 2, 3, 4}
    assert parse_weekdays("sabado,domingo") == {5, 6}
    assert parse_weekdays("sábado,domingo") == {5, 6}
    assert parse_weekdays("laborables") == {0, 1, 2, 3, 4}
    assert parse_weekdays("dias laborables") == {0, 1, 2, 3, 4}
    assert parse_weekdays("fin de semana") == {5, 6}
    assert parse_weekdays("diario") == {0, 1, 2, 3, 4, 5, 6}
    assert parse_weekdays("todos") == {0, 1, 2, 3, 4, 5, 6}


# --- 7. Range syntax support ---
def test_parse_weekdays_range_syntax() -> None:
    assert parse_weekdays("mon-wed") == {0, 1, 2}
    assert parse_weekdays("mo-mi") == {0, 1, 2}
    assert parse_weekdays("1-4") == {1, 2, 3, 4}
    assert parse_weekdays("0..2") == {0, 1, 2}
    # Wrap-around range: Friday to Monday
    assert parse_weekdays("fri-mon") == {4, 5, 6, 0}
    assert parse_weekdays("fr-mo") == {4, 5, 6, 0}


# --- 8. Compound groups in comma-separated strings and iterables ---
def test_parse_weekdays_compound_groups() -> None:
    assert parse_weekdays("workdays,sat") == {0, 1, 2, 3, 4, 5}
    assert parse_weekdays("mon-fri,sun") == {0, 1, 2, 3, 4, 6}
    assert parse_weekdays("mo-fr,so") == {0, 1, 2, 3, 4, 6}
    assert parse_weekdays(["workdays", "sun"]) == {0, 1, 2, 3, 4, 6}
    assert parse_weekdays(["mon-wed", "fri"]) == {0, 1, 2, 4}


# --- 9. Boolean rejection guard ---
def test_parse_weekdays_rejects_booleans() -> None:
    with pytest.raises(TypeError, match="boolean"):
        parse_weekdays(True)
    with pytest.raises(TypeError, match="boolean"):
        parse_weekdays(False)
    with pytest.raises(TypeError, match="boolean"):
        parse_weekdays([True, False])
    with pytest.raises(TypeError, match="boolean"):
        parse_weekdays([0, 1, True])


# --- 10. ConfigManager portable weekdays export with mixed types ---
def test_autosync_portable_weekdays_export_mixed_types() -> None:
    conn = {
        "id": "c1",
        "name": "Test",
        "autosync": {
            "mode": "daily",
            "daily_time": "12:00",
            "timezone": "Europe/Berlin",
            "weekdays": ["mon", 2, "fri"],
        },
    }
    exported = ConfigManager._portable_autosync(conn)
    assert exported["weekdays"] == [2, "fri", "mon"]


# --- 11. ConnectionScheduler catches RuntimeError safely ---
def test_start_daily_timer_catches_runtime_error(monkeypatch) -> None:
    class DummyConfig:
        def list_connections(self):
            return []

    scheduler = ConnectionScheduler(DummyConfig())
    conn = {"id": "c_err", "name": "BrokenConn"}
    autosync = {
        "mode": "daily",
        "daily_time": "12:00",
        "timezone": "Europe/Berlin",
    }

    def failing_next_run(*args, **kwargs):
        raise RuntimeError("could not determine the next scheduled run")

    monkeypatch.setattr(prosync, "next_daily_run", failing_next_run)

    warnings = []
    monkeypatch.setattr(prosync, "log_warning", lambda msg: warnings.append(msg))

    # Must not raise RuntimeError
    scheduler._start_daily_timer(conn, autosync)
    assert len(warnings) == 1
    assert "ist ungültig" in warnings[0]
    assert "c_err" not in scheduler.timers
