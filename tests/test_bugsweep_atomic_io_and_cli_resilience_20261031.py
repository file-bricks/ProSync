"""Hermetic regression tests for bugsweep 2026-10-31:
Atomic I/O resilience (readonly overwrite, WinError 5/32 retry), translation CLI CWD-independence,
and SQLite connection cleanup in ProSyncReader.
"""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

import prosync_utils
from prosync_utils import atomic_write_json, atomic_write_text


def test_atomic_write_text_overwrites_readonly_destination(tmp_path: Path) -> None:
    target = tmp_path / "readonly_doc.txt"
    target.write_text("Alter Inhalt", encoding="utf-8")
    os.chmod(target, stat.S_IREAD)

    # Must succeed and overwrite without PermissionError [WinError 5]
    atomic_write_text(str(target), "Neuer atomarer Inhalt", encoding="utf-8")

    assert target.is_file()
    assert target.read_text(encoding="utf-8") == "Neuer atomarer Inhalt"
    # Ensure no leftover temp files exist
    assert list(tmp_path.iterdir()) == [target]


def test_atomic_write_json_overwrites_readonly_destination(tmp_path: Path) -> None:
    target = tmp_path / "readonly_config.json"
    target.write_text('{"version": 1}', encoding="utf-8")
    os.chmod(target, stat.S_IREAD)

    # Must succeed and overwrite without PermissionError [WinError 5]
    new_data = {"version": 2, "active": True, "title": "Aktualisiert"}
    atomic_write_json(str(target), new_data, indent=2, ensure_ascii=False)

    assert target.is_file()
    assert json.loads(target.read_text(encoding="utf-8")) == new_data
    assert list(tmp_path.iterdir()) == [target]


def test_atomic_write_rejects_directory(tmp_path: Path) -> None:
    target_dir = tmp_path / "subfolder"
    target_dir.mkdir()

    with pytest.raises(IsADirectoryError):
        atomic_write_text(str(target_dir), "text")

    with pytest.raises(IsADirectoryError):
        atomic_write_json(str(target_dir), {"key": "val"})

    # Ensure no temp files were created inside or beside target_dir
    assert list(target_dir.iterdir()) == []


def test_atomic_write_restores_original_mode_on_failure(tmp_path: Path) -> None:
    target = tmp_path / "readonly_preserve.txt"
    target.write_text("Soll erhalten bleiben", encoding="utf-8")
    os.chmod(target, stat.S_IREAD)

    # Simulate failure during replace
    with mock.patch("prosync_utils.os.replace", side_effect=OSError("Transiente Sperre")):
        with pytest.raises(OSError, match="Transiente Sperre"):
            atomic_write_text(str(target), "Fehlgeschlagener Schreibversuch")

    assert target.read_text(encoding="utf-8") == "Soll erhalten bleiben"
    assert list(tmp_path.iterdir()) == [target], "Temporary files must be cleaned up on failure"
    if os.name == "nt":
        current_stat = os.stat(target)
        assert not (current_stat.st_mode & stat.S_IWRITE), "Readonly attribute must be preserved on failure"


def test_manage_translations_cwd_independence(tmp_path: Path, monkeypatch) -> None:
    import manage_translations

    # Change current working directory to an isolated temp directory
    monkeypatch.chdir(tmp_path)

    # Invoking check_translations() without arguments must resolve to the real project directory
    # and return 0 (100% parity across all 6 languages) instead of looking in tmp_path
    exit_code = manage_translations.check_translations()
    assert exit_code == 0


def test_manage_translations_excludes_tooling_scripts() -> None:
    import manage_translations

    app_dir = Path(manage_translations.__file__).resolve().parent
    german_strings = manage_translations.find_german_strings(str(app_dir))

    # Should not pick up internal docstring / constant words from translator.py or manage_translations.py
    assert "locales/translations.json" not in german_strings


def test_prosync_reader_search_worker_closes_connection_on_error(tmp_path: Path) -> None:
    import ProSyncReader

    # Create dummy database
    db_file = tmp_path / "test_corrupt.db"
    db_file.write_text("Keine SQLite Datenbank")

    class DummyManager:
        dbs = [str(db_file)]

    worker = ProSyncReader.SearchWorker(DummyManager(), "test")

    closed = False
    original_connect = ProSyncReader.sqlite3.connect

    class TrackedConn:
        def __init__(self, *args, **kwargs):
            self.real_conn = original_connect(*args, **kwargs)
        def cursor(self):
            raise ProSyncReader.sqlite3.DatabaseError("Simulierter korrupter Header")
        def close(self):
            nonlocal closed
            closed = True
            self.real_conn.close()

    with mock.patch.object(ProSyncReader.sqlite3, "connect", side_effect=TrackedConn):
        worker.run()

    assert closed, "SearchWorker must close SQLite connection in finally block even on error"
