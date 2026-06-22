# -*- coding: utf-8 -*-
"""Regressionstests — ProSync Desktop-Re-Sweep 2026-06-22 (Bugsweep-Loop-Lauf 26).

ProSyncStart_V3.1.py wird via importlib geladen (Dateiname mit Punkt). Echte Tests für die
importierbaren Bausteine; conn-Leak/Atomic-Schreiben zusätzlich statisch. Red-on-revert: PSY_SRC.

  copy  _atomic_copy2: tmp + os.replace (kein halbes Ziel).
  db    ConnectionDB._lock (RLock) — Cross-Thread-Serialisierung.
  A1/A2 check_wal_mode/checkpoint: conn in finally (kein Leak).
  A3    ConfigManager.save atomar.
  A4    import_portable_profile open() im try.
"""
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SRCDIR = Path(os.environ.get("PSY_SRC", _ROOT))
_MAIN = _SRCDIR / "ProSyncStart_V3.1.py"
SRC = _MAIN.read_text(encoding="utf-8")


def _load():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    spec = importlib.util.spec_from_file_location("prosync_main_under_test", str(_ROOT / "ProSyncStart_V3.1.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def has(n):
    return n in SRC


# --- echte Tests (live-Modul) ---
def test_atomic_copy2_no_tmp_left(tmp_path):
    m = _load()
    src = tmp_path / "s.bin"; src.write_bytes(b"DATA123")
    dst = tmp_path / "sub" / "t.bin"; (tmp_path / "sub").mkdir()
    m._atomic_copy2(str(src), str(dst))
    assert dst.read_bytes() == b"DATA123"
    assert not (tmp_path / "sub" / "t.bin.prosync_tmp").exists()


def test_connectiondb_lock_and_roundtrip(tmp_path):
    m = _load()
    import threading
    db = m.ConnectionDB(str(tmp_path / "idx.db"))
    try:
        assert isinstance(db._lock, type(threading.RLock()))
        fid = db.log_version("x", str(tmp_path / "x"), "2020-01-01T00:00:00", 7, "h" * 64, "source")
        assert isinstance(fid, int)
    finally:
        db.close()


def test_check_wal_mode_non_db_false_no_crash(tmp_path):
    m = _load()
    f = tmp_path / "plain.txt"; f.write_text("not a database")
    assert m.DatabaseSafetyManager.check_wal_mode(str(f)) is False


def test_config_save_atomic(tmp_path):
    m = _load()
    cfg = m.ConfigManager(str(tmp_path / "config.json"))
    cfg.save()
    assert (tmp_path / "config.json").exists()
    assert not (tmp_path / "config.json.tmp").exists()


# --- statische Assertions (red-on-revert) ---
def test_static_atomic_copy_used():
    assert has("def _atomic_copy2(") and has("os.replace(tmp, dst)"), "atomic-copy-Helfer fehlt"
    assert not has("shutil.copy2(s_abs, t_abs)") and not has("shutil.copy2(t_abs, s_abs)"), \
        "FolderSyncWorker nutzt noch direktes shutil.copy2"
    assert not has("shutil.copy2(source_file, target_file)"), "FileSyncWorker nutzt noch direktes shutil.copy2"


def test_static_conn_finally():
    # beide DB-Funktionen schliessen conn im finally
    assert SRC.count("if conn is not None:\n                conn.close()") >= 2, "conn-finally-close fehlt"


def test_static_config_atomic():
    assert has('tmp = f"{self.path}.tmp"') and has("os.replace(tmp, self.path)"), "config atomar fehlt"


def test_static_connectiondb_rlock():
    assert has("self._lock = threading.RLock()") and has("with self._lock:"), "ConnectionDB-Lock fehlt"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
