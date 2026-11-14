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


def test_file_connection_two_way_brings_back_a_newer_target(prosync, tmp_path):
    """Der Dateidialog bietet „two_way“ an, der FileSyncWorker kopierte aber immer Quelle → Ziel:
    eine am Ziel bearbeitete Datei wurde beim nächsten Sync überschrieben."""
    source, target = tmp_path / "a" / "notizen.txt", tmp_path / "b" / "notizen.txt"
    source.parent.mkdir()
    target.parent.mkdir()
    _file(source, "Stand Laptop", 1_700_000_000)
    _file(target, "am Zielrechner ergänzt", 1_700_003_600)
    cfg = {"id": "f", "name": "Datei", "type": "file", "source_file": str(source),
           "target_file": str(target), "mode": "two_way"}
    errors = []
    worker = prosync.FileSyncWorker(cfg)
    worker.error.connect(errors.append)
    worker.run()
    assert errors == []
    assert source.read_text(encoding="utf-8") == "am Zielrechner ergänzt"
    assert target.read_text(encoding="utf-8") == "am Zielrechner ergänzt"

    # one_way bleibt eine Sicherung: Quelle gewinnt immer.
    _file(target, "am Ziel geändert", 1_700_009_000)
    prosync.FileSyncWorker({**cfg, "mode": "one_way"}).run()
    assert target.read_text(encoding="utf-8") == "am Zielrechner ergänzt"


def test_reader_search_finds_names_with_capital_umlauts(prosync, tmp_path):
    """SQLite-lower()/LIKE kennen nur ASCII: „Übersicht“ oder „übersicht“ fanden
    „Übersicht_2026.pdf“ nicht (Ä/Ö/Ü am Wortanfang sind im Deutschen häufig)."""
    sys.path.insert(0, str(ROOT))
    import ProSyncReader

    db = prosync.ConnectionDB(str(tmp_path / "profiler_index.db"))
    try:
        db.log_version("Übersicht_2026.pdf", str(tmp_path / "Übersicht_2026.pdf"), 1.0, 10, "h1", "source")
        db.log_version("Ölrechnung.pdf", str(tmp_path / "Ölrechnung.pdf"), 1.0, 10, "h2", "source")
    finally:
        db.close()

    class _Manager:
        dbs = [str(tmp_path / "profiler_index.db")]

    for term, expected in (("Übersicht", "Übersicht_2026.pdf"), ("übersicht", "Übersicht_2026.pdf"),
                           ("öl", "Ölrechnung.pdf")):
        found = []
        worker = ProSyncReader.SearchWorker(_Manager(), term)
        worker.results_found.connect(found.extend)
        worker.run()
        assert [r["name"] for r in found] == [expected], term
