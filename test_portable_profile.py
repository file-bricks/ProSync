"""Regression tests for the redacted portable exchange format."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path


def load_prosync_module():
    """Load the ProSync main module via importlib."""
    module_path = Path(__file__).with_name("ProSyncStart_V3.1.py")
    spec = importlib.util.spec_from_file_location("prosync", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_portable_profile_export_import():
    """Portable export should redact local paths and import as remapping drafts."""
    prosync = load_prosync_module()

    with tempfile.TemporaryDirectory() as temp_dir:
        old_appdata = os.environ.get("APPDATA")
        os.environ["APPDATA"] = temp_dir
        try:
            config_path = Path(temp_dir) / "ProSync_config.json"
            export_path = Path(temp_dir) / "prosync-profile-v1.json"

            cfg = prosync.ConfigManager(str(config_path))
            cfg.data = {
                "app": {
                    "notifications_enabled": False,
                    "profiler_path": r"C:\Private\Tools\ProFiler.exe",
                },
                "connections": [
                    {
                        "id": "folder-1",
                        "name": "Projekt Backup",
                        "type": prosync.ConnectionType.FOLDER,
                        "source": r"C:\Users\User\Projects\Alpha",
                        "target": r"D:\Backups\Alpha",
                        "mode": "mirror",
                        "conflict_policy": "source",
                        "indexing": True,
                        "db_path": r"C:\Users\User\Projects\Alpha\index.db",
                        "exclude_patterns": ["*.tmp", "__pycache__"],
                        "autosync": {"enabled": True, "interval_minutes": 60},
                        "_safety_analysis": {
                            "databases_found": 2,
                            "critical_databases": 1,
                            "excluded_databases": 1,
                            "total_db_size_mb": 12.5,
                        },
                    },
                    {
                        "id": "file-1",
                        "name": "SQLite Backup",
                        "type": prosync.ConnectionType.FILE,
                        "source_file": r"C:\Users\User\App\data.db",
                        "target_file": r"E:\Backup\data.db",
                        "mode": "one_way",
                        "checkpoint_before_sync": True,
                        "autosync": {"enabled": False, "interval_minutes": 240},
                        "_file_analysis": {
                            "type": "sqlite",
                            "wal_mode": True,
                            "is_critical": True,
                            "size_mb": 8.2,
                        },
                    },
                ],
            }
            cfg.save()

            report_log = Path(temp_dir) / "ProSync" / "reports" / "sync_log.json"
            report_log.parent.mkdir(parents=True, exist_ok=True)
            report_log.write_text(
                json.dumps(
                    [
                        {
                            "connection": "Projekt Backup",
                            "connection_id": "folder-1",
                            "mode": "mirror",
                            "started_at": "2026-05-26T10:00:00+00:00",
                            "duration_seconds": 4.5,
                            "files_copied": 12,
                            "files_deleted": 1,
                            "files_skipped": 3,
                            "bytes_copied": 2048,
                            "total_actions": 16,
                        }
                    ],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            payload = cfg.export_portable_profile(str(export_path))
            exported_text = export_path.read_text(encoding="utf-8")

            assert payload["schema"] == prosync.PORTABLE_PROFILE_SCHEMA
            assert payload["app"] == {"notifications_enabled": False}
            assert payload["reports"]["count"] == 1
            assert payload["reports"]["latest"]["connection"] == "Projekt Backup"
            assert r"C:\Users\User\Projects\Alpha" not in exported_text
            assert r"C:\Private\Tools\ProFiler.exe" not in exported_text

            folder_payload = next(conn for conn in payload["connections"] if conn["id"] == "folder-1")
            file_payload = next(conn for conn in payload["connections"] if conn["id"] == "file-1")
            assert folder_payload["path_hints"]["source_label"] == "Alpha"
            assert folder_payload["path_hints"]["target_label"] == "Alpha"
            assert folder_payload["path_hints"]["db_label"] == "index.db"
            assert "source" not in folder_payload
            assert "target" not in folder_payload
            assert file_payload["path_hints"]["source_label"] == "data.db"
            assert file_payload["path_hints"]["target_label"] == "data.db"
            assert "source_file" not in file_payload
            assert "target_file" not in file_payload

            imported_cfg = prosync.ConfigManager(str(Path(temp_dir) / "Imported.json"))
            result = imported_cfg.import_portable_profile(str(export_path))

            assert result == {"imported": 2, "renamed": 0}
            imported_connections = imported_cfg.list_connections()
            assert len(imported_connections) == 2
            assert imported_cfg.data["app"]["notifications_enabled"] is False

            imported_folder = next(conn for conn in imported_connections if conn["name"] == "Projekt Backup")
            assert imported_folder["source"] == ""
            assert imported_folder["target"] == ""
            assert imported_folder["autosync"]["enabled"] is False
            assert imported_folder["_portable_import"]["requires_mapping"] is True
            assert imported_folder["_portable_import"]["path_hints"]["source_label"] == "Alpha"
        finally:
            if old_appdata is None:
                os.environ.pop("APPDATA", None)
            else:
                os.environ["APPDATA"] = old_appdata


def test_portable_profile_import_renames_colliding_ids():
    """Import should not overwrite existing local connections on ID collision."""
    prosync = load_prosync_module()

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "ProSync_config.json"
        exchange_path = Path(temp_dir) / "portable.json"

        cfg = prosync.ConfigManager(str(config_path))
        cfg.data = {
            "app": {"notifications_enabled": True},
            "connections": [
                {
                    "id": "shared-id",
                    "name": "Lokale Aufgabe",
                    "type": prosync.ConnectionType.FOLDER,
                    "source": r"C:\Local\Source",
                    "target": r"D:\Local\Target",
                    "mode": "mirror",
                }
            ],
        }
        cfg.save()

        exchange_path.write_text(
            json.dumps(
                {
                    "schema": prosync.PORTABLE_PROFILE_SCHEMA,
                    "exported_at": "2026-05-26T12:00:00+00:00",
                    "exported_from": {"app": "ProSync", "version": "3.2"},
                    "app": {"notifications_enabled": True},
                    "connections": [
                        {
                            "id": "shared-id",
                            "name": "Importierte Aufgabe",
                            "type": prosync.ConnectionType.FILE,
                            "mode": "one_way",
                            "checkpoint_before_sync": True,
                            "exclude_patterns": [],
                            "autosync": {"enabled": False, "interval_minutes": 30},
                            "path_hints": {
                                "source_label": "data.db",
                                "target_label": "data.db",
                            },
                        }
                    ],
                    "reports": {"count": 0, "latest": None},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        result = cfg.import_portable_profile(str(exchange_path))
        ids = [conn["id"] for conn in cfg.list_connections()]

        assert result == {"imported": 1, "renamed": 1}
        assert "shared-id" in ids
        assert len(ids) == 2
        assert len(set(ids)) == 2


def test_portable_profile_import_accepts_single_string_exclude_pattern():
    """Import should treat a single exclude pattern string as one pattern."""
    prosync = load_prosync_module()

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "ProSync_config.json"
        exchange_path = Path(temp_dir) / "portable.json"

        cfg = prosync.ConfigManager(str(config_path))
        exchange_path.write_text(
            json.dumps(
                {
                    "schema": prosync.PORTABLE_PROFILE_SCHEMA,
                    "exported_at": "2026-05-28T06:00:00+00:00",
                    "exported_from": {"app": "ProSync", "version": "3.2"},
                    "app": {"notifications_enabled": True},
                    "connections": [
                        {
                            "id": "folder-1",
                            "name": "Importierte Aufgabe",
                            "type": prosync.ConnectionType.FOLDER,
                            "mode": "mirror",
                            "exclude_patterns": "*.tmp",
                            "autosync": {"enabled": False, "interval_minutes": 15},
                            "path_hints": {
                                "source_label": "Quelle",
                                "target_label": "Ziel",
                            },
                        }
                    ],
                    "reports": {"count": 0, "latest": None},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        cfg.import_portable_profile(str(exchange_path))

        imported = cfg.list_connections()[0]
        assert imported["exclude_patterns"] == ["*.tmp"]


def test_portable_profile_export_accepts_single_string_exclude_pattern():
    """Export should treat a single exclude pattern string as one pattern."""
    prosync = load_prosync_module()

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "ProSync_config.json"
        export_path = Path(temp_dir) / "portable.json"

        cfg = prosync.ConfigManager(str(config_path))
        cfg.data = {
            "app": {"notifications_enabled": True},
            "connections": [
                {
                    "id": "folder-1",
                    "name": "Export-Aufgabe",
                    "type": prosync.ConnectionType.FOLDER,
                    "source": r"C:\Quelle",
                    "target": r"D:\Ziel",
                    "mode": "mirror",
                    "exclude_patterns": "*.tmp",
                    "autosync": {"enabled": False, "interval_minutes": 15},
                }
            ],
        }

        payload = cfg.export_portable_profile(str(export_path))

        assert payload["connections"][0]["exclude_patterns"] == ["*.tmp"]


if __name__ == "__main__":
    try:
        test_portable_profile_export_import()
        test_portable_profile_import_renames_colliding_ids()
        test_portable_profile_import_accepts_single_string_exclude_pattern()
        test_portable_profile_export_accepts_single_string_exclude_pattern()
        print("portable profile tests passed")
        sys.exit(0)
    except Exception as exc:
        print(f"portable profile tests failed: {exc}")
        raise
