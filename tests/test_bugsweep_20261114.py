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


def test_reader_preview_reads_windows_ansi_text(prosync, tmp_path):
    """Die Vorschau las nur UTF-8 (errors=replace): ANSI-Umlaute/€ erschienen als „�“."""
    sys.path.insert(0, str(ROOT))
    import ProSyncReader

    text = "Prüfbericht „Müller“ – 5 €"
    for name, data in (("ansi.txt", text.encode("cp1252")), ("utf8.txt", text.encode("utf-8-sig"))):
        (tmp_path / name).write_bytes(data)
        shown = []
        worker = ProSyncReader.PreviewWorker(str(tmp_path / name))
        worker.preview_ready.connect(shown.append)
        worker.run()
        assert shown == [text], name


def test_reader_preview_keeps_long_utf8_text_utf8(prosync, tmp_path):
    """Ein am 12-kB-Leseende abgeschnittenes UTF-8-Zeichen darf nicht zur cp1252-Dekodierung führen."""
    sys.path.insert(0, str(ROOT))
    import ProSyncReader

    text = "ä" * 9000  # 18 kB UTF-8 aus Zwei-Byte-Zeichen
    # Das führende „x“ versetzt die Zeichen um ein Byte: Byte 12000 liegt mitten in einem „ä“.
    (tmp_path / "lang.txt").write_bytes(("x" + text).encode("utf-8"))
    shown = []
    worker = ProSyncReader.PreviewWorker(str(tmp_path / "lang.txt"))
    worker.preview_ready.connect(shown.append)
    worker.run()
    assert shown[0] == ("x" + text)[:3000]


def test_case_only_rename_is_one_file_on_windows(prosync):
    """„bericht.pdf“ (Ziel) vs. „Bericht.pdf“ (Quelle) galten als zwei Dateien: Mirror plante
    Kopieren UND Löschen derselben physischen Datei (gemessen: Ziel in 3 von 6 Läufen leer)."""
    src = {"Bericht.pdf": {"size": 3, "mtime": 200.0}}
    tgt = {"bericht.pdf": {"size": 3, "mtime": 100.0}}
    casefold = lambda rel: rel.lower()  # noqa: E731 - Windows-Verhalten auch auf Linux-CI prüfen
    for mode in ("mirror", "two_way", "update", "one_way"):
        actions = prosync.plan_folder_actions(src, tgt, mode, "newest", path_key=casefold)
        assert actions == [("COPY_L2R", "Bericht.pdf")], (mode, actions)


@pytest.mark.skipif(os.name != "nt", reason="case-insensitives Dateisystem (Windows) nötig")
def test_mirror_keeps_case_renamed_file_for_every_hash_order(tmp_path):
    import subprocess

    script = (
        "import importlib.util, os, sys\n"
        "from PySide6.QtCore import QCoreApplication\n"
        "app = QCoreApplication(sys.argv)\n"
        f"spec = importlib.util.spec_from_file_location('p', {str(ROOT / 'ProSyncStart_V3.1.py')!r})\n"
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        "root = sys.argv[1]\n"
        "w = m.FolderSyncWorker({'id': 'c', 'name': 'case', 'source': root + '/src', 'target': root + '/tgt', 'mode': 'mirror'})\n"
        "w.run()\n"
        "print(sorted(os.listdir(root + '/tgt')))\n"
    )
    for seed in range(1, 7):
        run_root = tmp_path / f"run{seed}"
        (run_root / "src").mkdir(parents=True)
        (run_root / "tgt").mkdir()
        (run_root / "src" / "Bericht.pdf").write_text("neu", encoding="utf-8")
        (run_root / "tgt" / "bericht.pdf").write_text("alt", encoding="utf-8")
        _file(run_root / "tgt" / "bericht.pdf", "alt", 1_700_000_000)
        _file(run_root / "src" / "Bericht.pdf", "neu", 1_700_003_600)  # Quelle später bearbeitet
        env = {**os.environ, "PYTHONHASHSEED": str(seed), "QT_QPA_PLATFORM": "offscreen"}
        out = subprocess.run([sys.executable, "-c", script, str(run_root)], env=env,
                             capture_output=True, text=True, timeout=60).stdout.strip()
        # Datei bleibt erhalten (Windows behält beim Ersetzen die alte Schreibweise) und ist aktuell.
        assert out.lower() == "['bericht.pdf']", (seed, out)
        assert (run_root / "tgt" / "Bericht.pdf").read_text(encoding="utf-8") == "neu"
