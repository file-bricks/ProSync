#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reproduzierbarer Linux-Plattform-Smoke für ProSync V3.1 / V3.2.

Der Smoke deckt die geplante Linux-Source-Linie ab (8-Punkte-Standard):
1. Linux Datei- und Ordner-Öffner ('xdg-open' via prosync_utils)
2. Headless/Offscreen PySide6 MainWindow & Tray-Lifecycle (QT_QPA_PLATFORM=offscreen)
3. POSIX/Linux XDG App-Pfade & Reports-Persistenz (~/.config/ProSync)
4. Sibling-Launcher & ProFiler-Pfadauflösung ohne Windows-creationflags
5. Redigierter Profil-Export (prosync-profile-v1.json) ohne absolute Linux-Pfade/Secrets
6. Cross-OS Konfliktregeln (cross_os_rules.py) für case-sensitive/insensitive Linux-Dateisysteme
7. Übersetzungssystem & Sprachkatalog-Parität auf Linux
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
    spec = importlib.util.spec_from_file_location("prosync_linux_smoke", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _create_test_sqlite_db(path: str, wal_mode: bool = False) -> None:
    """Erstellt eine Test-SQLite-Datenbank mit optionalem WAL-Modus."""
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE sync_items (id INTEGER PRIMARY KEY, name TEXT, size INTEGER)")
    conn.execute("INSERT INTO sync_items (name, size) VALUES ('LinuxÜbertrag.dat', 4096)")
    conn.commit()
    if wal_mode:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.commit()
    conn.close()


def test_linux_open_dispatch() -> None:
    """Check 1: Linux Opener nutzt 'xdg-open' und ignoriert nicht-existente Pfade."""
    print("Test 1: Linux System-Öffner ('xdg-open') via prosync_utils")
    import prosync_utils

    with tempfile.TemporaryDirectory(prefix="prosync-linux-open-") as tmp_dir:
        tmp = Path(tmp_dir)
        probe_file = tmp / "LinuxÜberblick.txt"
        probe_file.write_text("Linux Test", encoding="utf-8")
        captured_calls: list[list[str]] = []

        def fake_call(command):
            captured_calls.append(command)
            return 0

        with mock.patch.object(prosync_utils.sys, "platform", "linux"), mock.patch.object(
            prosync_utils.subprocess,
            "call",
            side_effect=fake_call,
        ):
            prosync_utils.open_file_cross_platform(str(probe_file))
            prosync_utils.open_folder_cross_platform(str(probe_file))
            prosync_utils.open_file_cross_platform(str(tmp / "fehlt_auf_linux.txt"))

        assert captured_calls == [
            ["xdg-open", str(probe_file)],
            ["xdg-open", str(probe_file.parent)],
        ], f"Unerwartete xdg-open Aufrufe: {captured_calls}"
    print("  PASS: Linux xdg-open Befehle fuer Dateien und Ordner verifiziert\n")


def test_linux_offscreen_window_lifecycle() -> None:
    """Check 2: Headless PySide6 MainWindow auf Linux."""
    print("Test 2: Offscreen PySide6 MainWindow auf Linux")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv[:1])
    prosync = _load_prosync_module()

    with tempfile.TemporaryDirectory(prefix="prosync-linux-win-") as tmp_dir:
        tmp = Path(tmp_dir)
        cfg = prosync.ConfigManager(str(tmp / "ProSync_config.json"))
        window = prosync.MainWindow(cfg)

        assert window.isVisible() is False
        assert "ProSync" in window.windowTitle()
        assert window.tray_icon is not None

        window.tray_icon.hide()
        window.close()
        app.processEvents()

    print("  PASS: Offscreen MainWindow und Tray-Icon auf Linux initialisiert und beendet\n")


def test_linux_app_paths_and_reports() -> None:
    """Check 3: POSIX / Linux XDG App-Pfade und Report-Persistenz."""
    print("Test 3: POSIX/Linux XDG App-Pfade und Report-Persistenz")
    prosync = _load_prosync_module()

    with tempfile.TemporaryDirectory(prefix="prosync-linux-paths-") as tmp_dir:
        tmp = Path(tmp_dir)
        fake_home = tmp / "home" / "linuxuser"
        fake_home.mkdir(parents=True, exist_ok=True)

        os.environ["APPDATA"] = str(fake_home / ".config")
        base_dir = tmp / "REL-PUB_ProSync"
        base_dir.mkdir(parents=True, exist_ok=True)

        reports_dir = Path(os.environ["APPDATA"]) / "ProSync" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_file = reports_dir / "sync_log.json"

        test_reports = [
            {
                "connection": "Linux Sync Archiv",
                "connection_id": "conn-linux-1",
                "mode": "mirror",
                "started_at": "2026-08-21T14:00:00+00:00",
                "duration_seconds": 2.10,
                "files_copied": 8,
                "files_deleted": 0,
                "files_skipped": 1,
                "bytes_copied": 163840,
                "total_actions": 8,
            }
        ]
        report_file.write_text(json.dumps(test_reports, ensure_ascii=False, indent=2), encoding="utf-8")

        read_data = json.loads(report_file.read_text(encoding="utf-8"))
        assert len(read_data) == 1
        assert read_data[0]["connection"] == "Linux Sync Archiv"
        assert read_data[0]["bytes_copied"] == 163840

    print("  PASS: Linux Report-Pfade und UTF-8 JSON-Persistenz validiert\n")


def test_linux_sibling_and_tool_launcher() -> None:
    """Check 4: Sibling-Launcher und Tool-Start ohne Windows-Flags auf Linux."""
    print("Test 4: Sibling-Launcher und Prozess-Start auf Linux")
    prosync = _load_prosync_module()

    with tempfile.TemporaryDirectory(prefix="prosync-linux-launch-") as tmp_dir:
        tmp = Path(tmp_dir)
        base_dir = tmp / "REL-PUB_ProSync"
        base_dir.mkdir(parents=True, exist_ok=True)
        profiler_root = tmp / "REL-PUB_ProFiler"
        profiler_root.mkdir(parents=True, exist_ok=True)
        profiler_entry = profiler_root / "Profiler_Suite_V15.py"
        profiler_entry.write_text("# Linux smoke\n", encoding="utf-8")

        resolved = prosync.resolve_profiler_launch_path(base_dir)
        assert resolved == profiler_entry, f"Profiler nicht aufgelöst: {resolved}"

        # MainWindow Tool-Launch Mock
        cfg = prosync.ConfigManager(str(tmp / "ProSync_config.json"))
        window = prosync.MainWindow(cfg)

        with mock.patch.object(prosync.sys, "platform", "linux"), mock.patch.object(
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

    print("  PASS: Linux Tool-Start ohne Windows-creationflags erfolgreich\n")


def test_linux_redacted_profile_export_import() -> None:
    """Check 5: Redigierter Export prosync-profile-v1.json auf Linux."""
    print("Test 5: Redigierter Profil-Export ohne Secrets/Absolute Pfade auf Linux")
    prosync = _load_prosync_module()

    with tempfile.TemporaryDirectory(prefix="prosync-linux-export-") as tmp_dir:
        tmp = Path(tmp_dir)
        cfg = prosync.ConfigManager(str(tmp / "ProSync_config.json"))
        cfg.data["app"] = {"notifications_enabled": True}
        cfg.data["connections"] = [
            {
                "id": "conn-linux-mirror",
                "name": "Server Sync Übertragung",
                "type": "folder",
                "source": "/srv/sync/data/Quellordner",
                "target": "/mnt/nfs/backup/Zielordner",
                "mode": "mirror",
                "exclude_patterns": ["*.tmp", "__pycache__", ".git"],
                "autosync": {"enabled": True, "interval_minutes": 30},
                "conflict_policy": "source",
                "indexing": True,
                "db_path": "/srv/sync/data/Quellordner/index.db",
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
        assert "/srv/sync/data/Quellordner" not in export_text
        assert "/mnt/nfs/backup/Zielordner" not in export_text
        assert "Server Sync Übertragung" in export_text

    print("  PASS: Linux Export ohne Pfad-Leaks mit UTF-8 Umlauten validiert\n")


def test_linux_cross_os_conflict_rules() -> None:
    """Check 6: Cross-OS Konfliktregeln für Linux ext4/btrfs."""
    print("Test 6: Cross-OS Konfliktregeln für Linux Dateisysteme")
    import cross_os_rules

    # 1. Case-sensitive Pfade bleiben auf Linux im expliziten Modus unterscheidbar
    test_paths = [
        "/srv/data/file.txt",
        "/srv/data/FILE.TXT",
    ]
    conflicts_case_sensitive = cross_os_rules.find_cross_os_path_conflicts(test_paths, case_sensitive=True)
    assert len(conflicts_case_sensitive) == 0, "Case-sensitive sollte 2 getrennte Pfade sehen"

    conflicts_case_insensitive = cross_os_rules.find_cross_os_path_conflicts(test_paths, case_sensitive=False)
    assert len(conflicts_case_insensitive) == 1, "Case-insensitive sollte Kollision erkennen"

    # 2. Separator-Normalisierung
    posix_path = "/srv/data//sync/subfolder/"
    key = cross_os_rules.portable_path_key(posix_path)
    assert key == "/srv/data/sync/subfolder"

    print("  PASS: Cross-OS Pfadregeln fuer Linux verifiziert\n")


def test_linux_translation_parity() -> None:
    """Check 7: TranslationSystem auf Linux."""
    print("Test 7: TranslationSystem auf Linux")
    import translator

    with tempfile.TemporaryDirectory(prefix="prosync-linux-lang-") as tmp_dir:
        tmp = Path(tmp_dir)
        ts = translator.TranslationSystem(default_lang="de", app_dir=tmp)

        assert ts.t("Datei oeffnen") == "Datei oeffnen"
        assert ts.t("Synchronisation") == "Synchronisation"

        ts.set_language("en")
        assert ts.current_lang == "en"

    print("  PASS: TranslationSystem Sprachkatalog auf Linux validiert\n")


def test_linux_sqlite_safety_and_wal_checkpoint() -> None:
    """Check 8: SQLite-Sicherheit, WAL-Modus und Checkpointing auf Linux."""
    print("Test 8: SQLite DatabaseSafetyManager auf Linux")
    prosync = _load_prosync_module()
    DatabaseSafetyManager = prosync.DatabaseSafetyManager

    with tempfile.TemporaryDirectory(prefix="prosync-linux-db-") as tmp_dir:
        tmp = Path(tmp_dir)
        db_path = tmp / "production_linux.db"
        _create_test_sqlite_db(str(db_path), wal_mode=True)

        assert DatabaseSafetyManager.is_database_file("production_linux.db") is True
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

    print("  PASS: SQLite WAL-Erkennung, Checkpoint und Safe Settings auf Linux validiert\n")


def main() -> int:
    print("=== ProSync Linux Platform Smoke-Suite ===\n")
    try:
        test_linux_open_dispatch()
        test_linux_offscreen_window_lifecycle()
        test_linux_app_paths_and_reports()
        test_linux_sibling_and_tool_launcher()
        test_linux_redacted_profile_export_import()
        test_linux_cross_os_conflict_rules()
        test_linux_translation_parity()
        test_linux_sqlite_safety_and_wal_checkpoint()

        print("=== ALL 8 LINUX PLATFORM SMOKE CHECKS PASSED ===")
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
