"""Regressionstests — Bugsweep ProSync 2026-11-14."""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

try:
    from PySide6.QtCore import QCoreApplication
except ImportError:  # pragma: no cover
    QCoreApplication = None


def _load():
    spec = importlib.util.spec_from_file_location("prosync_bs1114", ROOT / "ProSyncStart_V3.1.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def prosync():
    if QCoreApplication is None:
        pytest.skip("PySide6 nicht verfügbar")
    if QCoreApplication.instance() is None:
        QCoreApplication(sys.argv)
    return _load()


def _file(path: Path, text: str, mtime: float) -> None:
    path.write_text(text, encoding="utf-8")
    os.utime(path, (mtime, mtime))


def test_update_mode_never_overwrites_a_newer_target(prosync, tmp_path):
    """Doku: „update – nur neuere Dateien übertragen“. Der Code kopierte bei jedem Unterschied
    und überschrieb eine im Ziel neuer bearbeitete Datei mit der älteren Quellfassung."""
    src, tgt = tmp_path / "src", tmp_path / "tgt"
    src.mkdir()
    tgt.mkdir()
    base = 1_700_000_000
    _file(src / "bericht.txt", "alte Fassung", base)
    _file(tgt / "bericht.txt", "im Ziel neu bearbeitet", base + 3600)
    _file(src / "neu.txt", "neuere Quelle", base + 7200)
    _file(tgt / "neu.txt", "alt im Ziel", base)

    worker = prosync.FolderSyncWorker({"id": "u", "name": "update", "source": str(src),
                                       "target": str(tgt), "mode": "update"})
    errors, reports = [], []
    worker.error.connect(errors.append)
    worker.sync_report.connect(reports.append)
    worker.run()

    assert errors == []
    assert (tgt / "bericht.txt").read_text(encoding="utf-8") == "im Ziel neu bearbeitet"
    assert (tgt / "neu.txt").read_text(encoding="utf-8") == "neuere Quelle"
    assert reports[0]["files_copied"] == 1 and reports[0]["files_skipped"] == 1


def test_one_way_still_copies_every_difference(prosync, tmp_path):
    src, tgt = tmp_path / "src", tmp_path / "tgt"
    src.mkdir()
    tgt.mkdir()
    _file(src / "a.txt", "quelle", 1_700_000_000)
    _file(tgt / "a.txt", "ziel neuer", 1_700_003_600)
    worker = prosync.FolderSyncWorker({"id": "o", "name": "one_way", "source": str(src),
                                       "target": str(tgt), "mode": "one_way"})
    worker.run()
    assert (tgt / "a.txt").read_text(encoding="utf-8") == "quelle"


def test_sftp_update_skips_newer_remote_files(prosync):
    src = {"a.txt": {"size": 5, "mtime": 100.0}, "b.txt": {"size": 5, "mtime": 9000.0}}
    remote = {"a.txt": {"size": 9, "mtime": 5000.0}, "b.txt": {"size": 9, "mtime": 100.0}}
    actions = prosync.SftpTargetSyncWorker._build_actions(None, src, remote, "update")
    assert actions == [("UPLOAD", "b.txt")]
    actions = prosync.SftpTargetSyncWorker._build_actions(None, src, remote, "one_way")
    assert actions == [("UPLOAD", "a.txt"), ("UPLOAD", "b.txt")]
