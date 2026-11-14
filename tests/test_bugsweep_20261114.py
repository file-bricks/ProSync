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


def test_stopping_a_batch_releases_ui_and_auto_sync(tmp_path):
    """Wächter (kein Fehlerfund, geprüft 2026-11-14): Nach dem Abbrechen eines Batches müssen
    Queue, Start-Button und Worker freigegeben sein — sonst würde jeder Auto-Sync bis zum Neustart
    übersprungen. Der Worker kehrt beim Abbruch ohne eigenes emit zurück; das Thread-Ende löst
    worker_finished trotzdem aus (gleichnamiges Signal)."""
    import json
    import subprocess

    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("_batch_stop_scenario.py")),
         str(ROOT / "ProSyncStart_V3.1.py"), str(tmp_path)],
        env=env, capture_output=True, text=True, timeout=90,
    )
    assert result.stdout.strip(), result.stderr[-800:]
    state = json.loads(result.stdout.strip().splitlines()[-1])
    assert state == {"batch_active": False, "run_enabled": True, "worker_none": True}, state


# --- Store/MSIX: Programmordner ist schreibgeschützt -----------------------------------------
# Logger (beim Import), ProSync_config.json und search_config.json lagen im Programmordner bzw.
# im Arbeitsverzeichnis. Im MSIX-Paket (C:/Program Files/WindowsApps/...) ist der schreibgeschützt:
# die Store-Version wäre schon beim Import des Loggers mit PermissionError abgebrochen.


@pytest.fixture
def packaged(monkeypatch, tmp_path):
    sys.path.insert(0, str(ROOT))
    import prosync_utils

    monkeypatch.setattr(prosync_utils, "is_msix_packaged", lambda: True)
    monkeypatch.setenv("APPDATA", str(tmp_path / "Roaming"))
    return tmp_path / "Roaming" / "ProSync"


def test_user_data_dir_stays_beside_the_program_when_not_packaged(tmp_path):
    sys.path.insert(0, str(ROOT))
    import prosync_utils

    assert prosync_utils.is_msix_packaged() is False  # Testlauf ist kein Paket
    assert prosync_utils.user_data_dir(tmp_path) == tmp_path


def test_packaged_config_goes_to_appdata(prosync, packaged):
    path = Path(prosync.default_config_path())
    assert path == packaged / "ProSync_config.json"
    prosync.ConfigManager(str(path))  # legt die Datei an, statt im Programmordner zu scheitern
    assert path.is_file()


def test_packaged_logger_writes_to_appdata(packaged):
    import logging

    import logger as logger_module

    log = logging.getLogger("ProSync")
    saved = log.handlers[:]
    log.handlers.clear()
    try:
        instance = object.__new__(logger_module.ProSyncLogger)
        instance._logger = None
        instance._initialize_logger()
        files = [Path(h.baseFilename) for h in log.handlers if hasattr(h, "baseFilename")]
        assert files == [packaged / "prosync.log"]
    finally:
        for handler in log.handlers:
            handler.close()
        log.handlers[:] = saved


def test_packaged_reader_keeps_its_db_list_in_appdata(packaged, monkeypatch, tmp_path):
    import ProSyncReader

    monkeypatch.chdir(tmp_path)  # Hauptprogramm startet den Reader mit cwd = Programmordner
    assert Path(ProSyncReader.config_path()) == packaged / "search_config.json"


@pytest.mark.parametrize("content", ['<<<<<<< HEAD\n{"Hallo": {"de": "Hallo"}}\n', "[]\n"])
def test_translation_scan_never_empties_an_unreadable_file(tmp_path, content):
    """manage_translations.py (Scan) ersetzte eine kaputte translations.json (z. B. Merge-Konfliktmarker)
    durch nur die neu gefundenen Schlüssel und meldete Erfolg — alle Übersetzungen weg. Gleiches Muster
    wie promptboard#4."""
    sys.path.insert(0, str(ROOT))
    import manage_translations as mt

    (tmp_path / "sample.py").write_text('button.setText("Datei öffnen")\n', encoding="utf-8")
    trans_file = tmp_path / "locales" / "translations.json"
    trans_file.parent.mkdir()
    trans_file.write_text(content, encoding="utf-8")
    assert mt.manage_translations(str(tmp_path)) == 1
    assert trans_file.read_text(encoding="utf-8") == content


def test_daily_timer_that_wakes_early_neither_syncs_early_nor_twice(prosync):
    """Qt-CoarseTimer (Standard) darf bis 5 % des Intervalls zu früh aufwachen — bei 20 h bis 1 h.
    Dann lief der Sync vor der eingestellten Zeit und der Timer wurde erneut auf denselben, noch
    kommenden Termin gestellt: zweiter Lauf kurz darauf."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from PySide6.QtCore import Qt

    berlin = ZoneInfo("Europe/Berlin")

    class _Cfg:
        def __init__(self, conns):
            self.conns = conns

        def list_connections(self):
            return self.conns

    conn = {"id": "d1", "name": "Täglich", "autosync": {
        "enabled": True, "mode": "daily", "daily_time": "13:00", "timezone": "Europe/Berlin"}}
    moments = iter([
        datetime(2026, 1, 15, 17, 0, tzinfo=berlin),       # Einplanen: 20 h bis morgen 13:00
        datetime(2026, 1, 16, 12, 10, tzinfo=berlin),      # Timer wacht 50 min zu früh auf
        datetime(2026, 1, 16, 13, 0, 1, tzinfo=berlin),    # pünktlich
    ])
    scheduler = prosync.ConnectionScheduler(_Cfg([conn]), now_provider=lambda _tz: next(moments))
    triggered = []
    scheduler.trigger_sync.connect(lambda c: triggered.append(c["id"]))
    try:
        scheduler.update_all()
        assert scheduler.timers["d1"].timerType() == Qt.TimerType.PreciseTimer

        scheduler._on_daily_timer("d1")
        assert triggered == [], "zu früh aufgewacht: darf noch nicht synchronisieren"
        assert scheduler.timers["d1"].interval() == 50 * 60 * 1000

        scheduler._on_daily_timer("d1")
        assert triggered == ["d1"]
        assert scheduler.timers["d1"].interval() == (24 * 60 * 60 - 1) * 1000
    finally:
        scheduler.stop_all()


@pytest.mark.parametrize("target", ["/", ".", "./", "//", "~", "~/"])
def test_sftp_mirror_refuses_server_root_and_login_home(prosync, tmp_path, target):
    """Spiegel löscht am Ziel alles, was in der Quelle fehlt. Ziel "/" (Server-Wurzel) oder "."/"~"
    (Login-Verzeichnis) hätte dort z. B. .ssh/authorized_keys gelöscht — danach kommt ProSync selbst
    nicht mehr auf den Server. „update“ löscht nichts und bleibt erlaubt."""
    src = tmp_path / "src"
    src.mkdir()
    cfg = {"id": "s", "name": "S", "type": "sftp", "source": str(src), "target": target,
           "remote_host": "host", "mode": "mirror"}
    with pytest.raises(ValueError, match="Spiegel"):
        prosync.validate_sftp_connection(cfg)
    assert prosync.validate_sftp_connection({**cfg, "mode": "update"}) is True


def test_sftp_mirror_to_root_deletes_nothing_on_the_server(prosync, tmp_path):
    sys.path.insert(0, str(ROOT))
    from test_sftp_target import FakeSftp, FakeSsh

    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("a", encoding="utf-8")
    sftp = FakeSftp()
    for d in ("/home", "/home/u", "/home/u/.ssh"):
        sftp.mkdir(d)
    sftp.files["/home/u/.ssh/authorized_keys"] = {"content": b"ssh-ed25519 AAAA", "mtime": 1}
    cfg = {"id": "s", "name": "S", "type": "sftp", "source": str(src), "target": "/",
           "remote_host": "host", "mode": "mirror"}
    errors = []
    worker = prosync.SftpTargetSyncWorker(cfg, transport_factory=lambda _c: (FakeSsh(), sftp))
    worker.error.connect(errors.append)
    worker.run()
    assert "/home/u/.ssh/authorized_keys" in sftp.files
    assert errors and "Spiegel" in errors[0]


def test_reader_ignores_stale_results_and_never_terminates_threads(tmp_path):
    """Neue Suche/Vorschau beendete den laufenden Worker per QThread.terminate() (laut Qt gefährlich:
    unter Windows TerminateThread, kann mitten in SQLite/pypdf mit gehaltenem GIL sterben) und ließ ihn
    mit der Ergebnisliste verbunden — spät eintreffende alte Treffer/Vorschauen überschrieben die neuen."""
    import json
    import subprocess

    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("_reader_stale_scenario.py")),
         str(ROOT / "ProSyncReader.py"), str(tmp_path)],
        env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90,
    )
    assert result.stdout.strip(), result.stderr[-800:]
    state = json.loads(result.stdout.strip().splitlines()[-1])
    assert state["terminated"] is False
    assert all("VERALTET" not in text for text in state["shown"]), state["shown"]
    assert any("aktuell" in text for text in state["shown"]), state["shown"]
    assert state["preview"] == "NEUE VORSCHAU"


def test_quit_from_tray_waits_for_a_running_sync(tmp_path):
    """„Beenden“ (force_quit) während eines Syncs: QApplication.quit() sofort, der Worker lief weiter und
    Qt zerstörte den laufenden Thread beim Aufräumen — Prozess brach ab (Exitcode ≠ 0), der Sync wurde
    mitten im Lauf abgeschnitten."""
    import json
    import subprocess

    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("_quit_during_sync_scenario.py")),
         str(ROOT / "ProSyncStart_V3.1.py"), str(tmp_path / "w")],
        env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    assert result.stdout.strip(), result.stderr[-800:]
    state = json.loads(result.stdout.strip().splitlines()[-1])
    assert state == {"worker_running_after_quit": False}
    assert result.returncode == 0, result.stderr[-800:]


@pytest.mark.parametrize("mode", ["mirror", "two_way"])
def test_folder_sync_never_copies_its_own_index_database(prosync, tmp_path, mode):
    """Mit Indexierung und Standardpfad liegt profiler_index.db in der Quelle. Der Sync kopierte die
    laufend beschriebene DB ins Ziel; bei „two_way“ konnte eine neuere fremde Index-DB im Ziel (zweiter
    Rechner, gleiches NAS-Ziel) die eigene ersetzen."""
    import sqlite3
    import time

    src, tgt = tmp_path / "src", tmp_path / "tgt"
    src.mkdir()
    tgt.mkdir()
    (src / "doc.txt").write_text("inhalt", encoding="utf-8")
    foreign = tgt / "profiler_index.db"
    foreign.write_bytes(b"FREMDER INDEX")
    future = time.time() + 3600
    os.utime(foreign, (future, future))
    conn = {"id": "i", "name": "I", "type": "folder", "source": str(src), "target": str(tgt), "mode": mode,
            "conflict_policy": "newest", "indexing": True, "db_path": str(src / "profiler_index.db"),
            "exclude_patterns": []}
    for _ in range(2):
        errors = []
        worker = prosync.create_cli_worker(conn)
        worker.error.connect(errors.append)
        worker.run()
        assert errors == []
    assert (tgt / "doc.txt").is_file()
    assert foreign.read_bytes() == b"FREMDER INDEX", "eigene Index-DB ins Ziel kopiert"
    with sqlite3.connect(src / "profiler_index.db") as db:  # eigene DB intakt, nicht ersetzt
        assert db.execute("SELECT count(*) FROM versions").fetchone()[0] >= 1
