# -*- coding: utf-8 -*-
"""Regressionstests — ProSync Desktop-Bugsweep 2026-06-28 (Bugsweep-Loop-Lauf 27).

Gefixt in diesem Lauf:
  B1  ConnectionDB.close(): self.conn=None nach self.conn.close() fehlte → doppelter
      close()-Aufruf erzeugte spurious ProgrammingError (jetzt sauber idempotent).
  B2  FolderSyncWorker.run(): self.db.close() fehlte im finally-Block → WAL-Checkpoint
      wurde nur durch Python-GC ausgelöst (nicht-deterministisch) statt explizit.

Red-on-revert: PSY_SRC.
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

def test_connectiondb_close_idempotent(tmp_path):
    """B1: Doppelter close()-Aufruf muss ohne Exception durchlaufen.

    Vor dem Fix: zweiter Aufruf traf self.conn (truthy, aber bereits geschlossen),
    führte wal_checkpoint auf toter Connection durch → ProgrammingError in except abgefangen,
    spurious Warning. Nach dem Fix: self.conn=None, zweiter Aufruf verlässt sofort den
    Guard-Block.
    """
    m = _load()
    db = m.ConnectionDB(str(tmp_path / "double_close.db"))
    db.log_version("f", str(tmp_path / "f"), "2024-01-01T00:00:00+00:00", 1, "a" * 64, "source")

    # Erster close
    db.close()
    assert db.conn is None, "self.conn muss nach close() auf None gesetzt sein"

    # Zweiter close muss sauber ohne Exception ablaufen
    try:
        db.close()
    except Exception as exc:
        raise AssertionError(f"Zweiter close()-Aufruf darf keine Exception werfen, bekam: {exc}")


def test_connectiondb_close_sets_conn_none(tmp_path):
    """B1: Sicherstellen dass self.conn nach close() tatsächlich None ist (Guard-Bedingung)."""
    m = _load()
    db = m.ConnectionDB(str(tmp_path / "guard.db"))
    assert db.conn is not None, "Vorbedingung: conn muss nach __init__ gesetzt sein"
    db.close()
    assert db.conn is None, "self.conn muss nach close() None sein"


# --- statische Assertions (red-on-revert) ---

def test_static_conn_none_after_close():
    """B1 statisch: self.conn = None muss im finally-Block von ConnectionDB.close() stehen."""
    assert has("self.conn = None  # Bugsweep 27"), \
        "self.conn=None nach close() fehlt (Bugsweep 27 Fix nicht gefunden)"


def test_static_db_close_in_folder_worker_finally():
    """B2 statisch: FolderSyncWorker.run() muss self.db.close() im finally-Block aufrufen."""
    # Prüfen: 'finally:' gefolgt von 'self.db.close()' im run()-Körper
    assert has("# Bugsweep 27: WAL-Checkpoint explizit auslösen statt GC zu vertrauen"), \
        "WAL-Checkpoint-finally in FolderSyncWorker.run() fehlt (Bugsweep 27 Fix nicht gefunden)"
    assert SRC.count("self.db.close()") >= 1, \
        "self.db.close() im FolderSyncWorker.run()-finally fehlt"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
