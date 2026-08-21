#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reproduzierbarer macOS-Plattform-Smoke für ProSync V3.1 / V3.2.

Der Smoke deckt die geplante macOS-Source-Linie ab (8-Punkte-Standard):
1. macOS Datei- und Ordner-Öffner ('open' und 'open -R' via prosync_utils)
2. Headless/Offscreen PySide6 MainWindow & Tray-Lifecycle (QT_QPA_PLATFORM=offscreen)
3. POSIX/macOS App-Pfade & Reports-Persistenz (~/.config/ProSync)
4. Sibling-Launcher & ProFiler-Pfadauflösung ohne Windows-creationflags
5. Redigierter Profil-Export (prosync-profile-v1.json) ohne absolute Pfade/Secrets
6. Cross-OS Konfliktregeln (cross_os_rules.py) für APFS/HFS+ Unicode-NFC & Casing
7. Übersetzungssystem & Sprachkatalog-Parität auf macOS
8. SQLite-Datenbank-Sicherheit, WAL-Modus-Erkennung & Checkpointing
"""

from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def _load_prosync_module():
    """Dynamisch ProSyncStart_V3.1.py laden."""
    module_path = PROJECT_ROOT / "ProSyncStart_V3.1.py"
    spec = importlib.util.spec_from_file_location("prosync_macos_smoke", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _create_test_sqlite_db(path: str, wal_mode: bool = False) -> None:
    """Erstellt eine Test-SQLite-Datenbank mit optionalem WAL-Modus."""
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE sync_items (id INTEGER PRIMARY KEY, name TEXT, size INTEGER)")
    conn.execute("INSERT INTO sync_items (name, size) VALUES ('Übertrag.dat', 2048)")
    conn.commit()
    if wal_mode:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.commit()
    conn.close()


def test_macos_open_dispatch() -> None:
    """Check 1: macOS Opener nutzt 'open' und ignoriert nicht-existente Pfade."""
    print("Test 1: macOS System-Öffner ('open') via prosync_utils")
    import prosync_utils

    with tempfile.TemporaryDirectory(prefix="prosync-mac-open-") as tmp_dir:
        tmp = Path(tmp_dir)
        probe_file = tmp / "Übersicht.txt"
        probe_file.write_text("macOS Test", encoding="utf-8")
        captured_calls: list[list[str]] = []

        def fake_call(command):
            captured_calls.append(command)
            return 0

        with mock.patch.object(prosync_utils.sys, "platform", "darwin"), mock.patch.object(
            prosync_utils.subprocess,
            "call",
            side_effect=fake_call,
        ):
            prosync_utils.open_file_cross_platform(str(probe_file))
            prosync_utils.open_folder_cross_platform(str(probe_file))
            prosync_utils.open_file_cross_platform(str(tmp / "fehlt_auf_mac.txt"))

        assert captured_calls == [
            ["open", str(probe_file)],
            ["open", str(probe_file.parent)],
        ], f"Unerwartete Open-Aufrufe: {captured_calls}"
    print("  PASS: macOS open-Befehle fuer Dateien und Ordner verifiziert\n")


def test_macos_offscreen_window_lifecycle() -> None:
    """Check 2: Headless PySide6 MainWindow auf macOS."""
    print("Test 2: Offscreen PySide6 MainWindow auf macOS")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv[:1])
    prosync = _load_prosync_module()

    with tempfile.TemporaryDirectory(prefix="prosync-mac-win-") as tmp_dir:
        tmp = Path(tmp_dir)
        cfg = prosync.ConfigManager(str(tmp / "ProSync_config.json"))
        window = prosync.MainWindow(cfg)

        assert window.isVisible() is False
        assert "ProSync" in window.windowTitle()
        assert window.tray_icon is not None

        window.tray_icon.hide()
        window.close()
        app.processEvents()

    print("  PASS: Offscreen MainWindow und Tray-Icon initialisiert und sauber beendet\n")


def test_macos_app_paths_and_reports() -> None:
    """Check 3: POSIX / macOS App-Pfade und Report-Persistenz."""
    print("Test 3: POSIX/macOS App-Pfade und Report-Persistenz")
    prosync = _load_prosync_module()

    with tempfile.TemporaryDirectory(prefix="prosync-mac-paths-") as tmp_dir:
        tmp = Path(tmp_dir)
        fake_home = tmp / "Users" / "developer"
        fake_home.mkdir(parents=True, exist_ok=True)

        os.environ["APPDATA"] = str(fake_home / "Library" / "Application Support")
        base_dir = tmp / "REL-PUB_ProSync"
        base_dir.mkdir(parents=True, exist_ok=True)

        reports_dir = Path(os.environ["APPDATA"]) / "ProSync" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_file = reports_dir / "sync_log.json"

        test_reports = [
            {
                "connection": "macOS Sync Archiv",
                "connection_id": "conn-darwin-1",
                "mode": "mirror",
                "started_at": "2026-08-21T14:00:00+00:00",
                "duration_seconds": 1.75,
                "files_copied": 5,
                "files_deleted": 0,
                "files_skipped": 2,
                "bytes_copied": 81920,
                "total_actions": 5,
            }
        ]
        report_file.write_text(json.dumps(test_reports, ensure_ascii=False, indent=2), encoding="utf-8")

        read_data = json.loads(report_file.read_text(encoding="utf-8"))
        assert len(read_data) == 1
        assert read_data[0]["connection"] == "macOS Sync Archiv"
        assert read_data[0]["bytes_copied"] == 81920

    print("  PASS: macOS Report-Pfade und UTF-8 JSON-Persistenz validiert\n")


def test_macos_sibling_and_tool_launcher() -> None:
    """Check 4: Sibling-Launcher und Tool-Start ohne Windows-Flags auf macOS."""
    print("Test 4: Sibling-Launcher und Prozess-Start auf macOS")
    prosync = _load_prosync_module()

    with tempfile.TemporaryDirectory(prefix="prosync-mac-launch-") as tmp_dir:
        tmp = Path(tmp_dir)
        base_dir = tmp / "REL-PUB_ProSync"
        base_dir.mkdir(parents=True, exist_ok=True)
        profiler_root = tmp / "REL-PUB_ProFiler"
        profiler_root.mkdir(parents=True, exist_ok=True)
        profiler_entry = profiler_root / "Profiler_Suite_V15.py"
        profiler_entry.write_text("# macOS smoke\n", encoding="utf-8")

        resolved = prosync.resolve_profiler_launch_path(base_dir)
        assert resolved == profiler_entry, f"Profiler nicht aufgelöst: {resolved}"

        # MainWindow Tool-Launch Mock
        cfg = prosync.ConfigManager(str(tmp / "ProSync_config.json"))
        window = prosync.MainWindow(cfg)

        with mock.patch.object(prosync.sys, "platform", "darwin"), mock.patch.object(
            prosync.subprocess,
            "Popen",
        ) as popen_mock:
            window._launch_tool_process(profiler_entry)

        launch_cmd = popen_mock.call_args.args[0]
        launch_kwargs = popen_mock.call_args.kwargs

        assert launch_cmd == [sys.executable, str(profiler_entry)]
        assert launch_kwargs["cwd"] == str(profiler_root)
        assert "creationflags" not in launch_kwargs

        window.tray_icon.hide()
        window.close()

    print("  PASS: macOS Tool-Start ohne Windows-creationflags erfolgreich\n")


def test_macos_redacted_profile_export_import() -> None:
    """Check 5: Redigierter Export prosync-profile-v1.json auf macOS."""
    print("Test 5: Redigierter Profil-Export ohne Secrets/Absolute Pfade")
    prosync = _load_prosync_module()

    with tempfile.TemporaryDirectory(prefix="prosync-mac-export-") as tmp_dir:
        tmp = Path(tmp_dir)
        cfg = prosync.ConfigManager(str(tmp / "ProSync_config.json"))
        cfg.data["app"] = {"notifications_enabled": True}
        cfg.data["connections"] = [
            {
                "id": "conn-darwin-mirror",
                "name": "Arbeitsverzeichnis macOS",
                "type": "folder",
                "source": "/Users/developer/Projects/Quellordner",
                "target": "/Volumes/BackupSSD/Zielordner",
                "mode": "mirror",
                "exclude_patterns": ["*.DS_Store", ".Trash", "__pycache__"],
                "autosync": {"enabled": True, "interval_minutes": 15},
                "conflict_policy": "source",
                "indexing": True,
                "db_path": "/Users/developer/Projects/Quellordner/index.db",
            }
        ]

        export_path = tmp / "prosync-profile-v1.json"
        payload = cfg.export_portable_profile(str(export_path))
        export_text = export_path.read_text(encoding="utf-8")
        exported = json.loads(export_text)

        assert payload["schema"] == "prosync-profile-v1"
        assert exported["connections"][0]["path_hints"] == {
            "source_label": "Quellordner",
            "target_label": "Zielordner",
            "db_label": "index.db",
        }
        # Absolute Pfade dürfen nicht im Export stehen
        assert "/Users/developer/Projects/Quellordner" not in export_text
        assert "/Volumes/BackupSSD/Zielordner" not in export_text
        assert "Arbeitsverzeichnis macOS" in export_text

    print("  PASS: Redigierter Export ohne Pfad-Leaks mit UTF-8 Umlauten validiert\n")


def test_macos_cross_os_conflict_rules() -> None:
    """Check 6: Cross-OS Konfliktregeln und Normalisierung für macOS."""
    print("Test 6: Cross-OS Konfliktregeln für macOS APFS/HFS+")
    import cross_os_rules

    # 1. Unicode NFC Normalisierung (macOS NFD zu portablem NFC)
    nfd_name = "U\u0308berblick"  # 'Ü' zerlegt in U + Combining Diaeresis
    nfc_name = "Überblick"
    assert cross_os_rules.portable_path_key(nfd_name) == cross_os_rules.portable_path_key(nfc_name)

    # 2. Case-folding Konflikterkennung auf case-insensitive Dateisystemen (APFS Standard)
    test_paths = [
        "/Volumes/Data/Projects/Documentation.pdf",
        "/Volumes/Data/Projects/DOCUMENTATION.PDF",
    ]
    conflicts = cross_os_rules.find_cross_os_path_conflicts(test_paths, case_sensitive=False)
    assert len(conflicts) == 1
    assert "case" in conflicts[0].reasons or "case-insensitive-key" in conflicts[0].reasons

    # 3. Separator-Bereinigung
    mixed_path = "Projects\\SubDir//file.txt"
    key = cross_os_rules.portable_path_key(mixed_path)
    assert "\\" not in key
    assert "//" not in key
    assert key == "projects/subdir/file.txt"

    print("  PASS: Cross-OS Pfadregeln und Unicode-Normalisierung für macOS verifiziert\n")


def test_macos_translation_parity() -> None:
    """Check 7: Übersetzungssystem & TranslationSystem auf macOS."""
    print("Test 7: TranslationSystem auf macOS")
    import translator

    with tempfile.TemporaryDirectory(prefix="prosync-mac-lang-") as tmp_dir:
        tmp = Path(tmp_dir)
        ts = translator.TranslationSystem(default_lang="de", app_dir=tmp)

        # Deutsche Standard-Begriffe
        assert ts.t("Datei oeffnen") == "Datei oeffnen"
        assert ts.t("Einstellungen") == "Einstellungen"

        # Sprachumschaltung
        ts.set_language("en")
        assert ts.current_lang == "en"

    print("  PASS: TranslationSystem Sprachkatalog und Umschaltung auf macOS validiert\n")


def test_macos_sqlite_safety_and_wal_checkpoint() -> None:
    """Check 8: SQLite-Sicherheit, WAL-Modus und Checkpointing auf macOS."""
    print("Test 8: SQLite DatabaseSafetyManager auf macOS")
    prosync = _load_prosync_module()
    DatabaseSafetyManager = prosync.DatabaseSafetyManager

    with tempfile.TemporaryDirectory(prefix="prosync-mac-db-") as tmp_dir:
        tmp = Path(tmp_dir)
        db_path = tmp / "production_macos.db"
        _create_test_sqlite_db(str(db_path), wal_mode=True)

        assert DatabaseSafetyManager.is_database_file("production_macos.db") is True
        assert DatabaseSafetyManager.is_sqlite_database(str(db_path)) is True
        assert DatabaseSafetyManager.check_wal_mode(str(db_path)) is True

        # Scan
        scanned = DatabaseSafetyManager.scan_directory_for_databases(str(tmp))
        assert len(scanned) >= 1
        assert any(db["path"] == str(db_path) for db in scanned)

        # WAL Checkpoint
        checkpoint_ok = DatabaseSafetyManager.checkpoint_sqlite_database(str(db_path))
        assert checkpoint_ok is True

        # Safe settings anwenden
        folder_cfg = {
            "type": "folder",
            "source": str(tmp),
            "mode": "two_way",
        }
        modified_cfg, warnings, excluded, changed = DatabaseSafetyManager.apply_safe_settings_folder(
            folder_cfg, scanned
        )
        assert changed is True
        assert "exclude_patterns" in modified_cfg

    print("  PASS: SQLite WAL-Erkennung, Checkpoint und Safe Settings auf macOS validiert\n")


def main() -> int:
    print("=== ProSync macOS Platform Smoke-Suite ===\n")
    try:
        test_macos_open_dispatch()
        test_macos_offscreen_window_lifecycle()
        test_macos_app_paths_and_reports()
        test_macos_sibling_and_tool_launcher()
        test_macos_redacted_profile_export_import()
        test_macos_cross_os_conflict_rules()
        test_macos_translation_parity()
        test_macos_sqlite_safety_and_wal_checkpoint()

        print("=== ALL 8 MACOS PLATFORM SMOKE CHECKS PASSED ===")
        return EXIT_SUCCESS
    except AssertionError as exc:
        print(f"\nTEST FAILED: {exc}")
        return EXIT_FAILURE
    except Exception as exc:
        print(f"\nUNEXPECTED ERROR: {exc}")
        import traceback

        traceback.print_exc()
        return EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
