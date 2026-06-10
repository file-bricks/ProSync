"""
Regressionstests für FolderSyncWorker / FileSyncWorker / ConnectionScheduler Bugs (2026-06-07):

Bug #1: started_at wurde nach dem Sync-Loop gesetzt (enthielt End-Zeit statt Start-Zeit).
        Fix: _started_at = datetime.now(...) wird vor dem Loop gesetzt.

Bug #2: Abgebrochener (killed) FolderSyncWorker emittierte trotzdem progress(100) und finished.
        Fix: before emit-sequence: if self.is_killed: return

Bug #3: Korrupte sync_log.json blockierte alle zukünftigen Report-Speicherungen.
        Fix: except (json.JSONDecodeError, UnicodeDecodeError, OSError): all_reports = []

Bug #4: Abgebrochener (killed) FileSyncWorker emittierte trotzdem finished (kein Guard vor Done-Block).
        Fix: before Done-block: if self.is_killed: return

Bug #8: ConnectionScheduler.update_all() stoppte keine Timer für gelöschte Verbindungen.
        Folge: Auto-Sync-Timer feuerten weiter mit veralteten Verbindungsdaten.
        Fix: update_all() stoppt Timer für IDs, die nicht mehr in der Config vorhanden sind.
"""

import sys
import os
import json
import datetime

import pytest

sys.path.insert(0, os.path.dirname(__file__))

try:
    from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer
    HAS_QT = True
except ImportError:
    HAS_QT = False

pytestmark = pytest.mark.skipif(not HAS_QT, reason="PySide6 nicht verfügbar")


def _get_app():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
    return app


def _load_prosync():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "prosync_fswb",
        os.path.join(os.path.dirname(__file__), "ProSyncStart_V3.1.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_worker_to_completion(worker, timeout_ms=5000):
    """Pumpt den Qt-Event-Loop bis der Worker fertig ist oder Timeout."""
    loop = QEventLoop()
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(loop.quit)
    worker.finished.connect(loop.quit)
    worker.error.connect(loop.quit)
    worker.start()
    timer.start(timeout_ms)
    loop.exec()


def test_started_at_reflects_start_not_end(tmp_path):
    """
    Bug #1: started_at muss die Zeit VOR dem Sync-Loop sein, nicht danach.

    Verifikation: started_at + duration_seconds darf nicht nach dem
    tatsächlichen Abschluss-Zeitstempel liegen. Wenn started_at fälschlicherweise
    am Ende gesetzt wird, gilt: started_at + duration > actual_end → Test ROT.
    """
    _get_app()
    prosync = _load_prosync()
    FolderSyncWorker = prosync.FolderSyncWorker

    src = tmp_path / "src"
    tgt = tmp_path / "tgt"
    src.mkdir()
    (src / "a.txt").write_text("hello")

    cfg = {
        "id": "bug1-test",
        "name": "started_at_test",
        "source": str(src),
        "target": str(tgt),
        "mode": "mirror",
    }

    worker = FolderSyncWorker(cfg)
    reports = []
    worker.sync_report.connect(reports.append)

    t_before = datetime.datetime.now(datetime.timezone.utc)
    _run_worker_to_completion(worker)
    t_after = datetime.datetime.now(datetime.timezone.utc)

    assert len(reports) == 1, "Ein sync_report erwartet"
    report = reports[0]

    started_at = datetime.datetime.fromisoformat(report["started_at"])
    duration = datetime.timedelta(seconds=report["duration_seconds"])

    # started_at muss im Fenster [t_before, t_after] liegen
    assert started_at >= t_before, (
        f"started_at ({started_at}) liegt vor dem Sync-Start ({t_before})"
    )
    assert started_at <= t_after, (
        f"started_at ({started_at}) liegt nach dem Sync-Ende ({t_after})"
    )

    # started_at + duration darf nicht nach t_after liegen (Bug: end + duration > t_after)
    estimated_end = started_at + duration
    slack = datetime.timedelta(seconds=2)
    assert estimated_end <= t_after + slack, (
        f"started_at+duration ({estimated_end}) > t_after ({t_after}) — "
        "started_at wurde offensichtlich am Ende statt am Anfang gesetzt"
    )


def test_killed_worker_does_not_emit_finished(tmp_path):
    """
    Bug #2: Ein per kill() abgebrochener FolderSyncWorker darf finished nicht emittieren.
    """
    _get_app()
    prosync = _load_prosync()
    FolderSyncWorker = prosync.FolderSyncWorker

    src = tmp_path / "src"
    tgt = tmp_path / "tgt"
    src.mkdir()
    for i in range(30):
        (src / f"file_{i:03d}.txt").write_text("x" * 512)

    cfg = {
        "id": "bug2-test",
        "name": "kill_test",
        "source": str(src),
        "target": str(tgt),
        "mode": "mirror",
    }

    worker = FolderSyncWorker(cfg)
    finished_calls = []
    worker.finished.connect(lambda: finished_calls.append(True))

    worker.start()
    worker.kill()
    worker.wait(5000)

    assert not finished_calls, (
        "finished wurde emittiert obwohl der Worker per kill() abgebrochen wurde"
    )


def test_file_sync_worker_killed_does_not_emit_finished(tmp_path):
    """
    Bug #4: Ein per kill() abgebrochener FileSyncWorker darf finished nicht emittieren.
    Analog zu Bug #2, aber für FileSyncWorker (kein is_killed-Guard vor Done-Block).
    """
    _get_app()
    prosync = _load_prosync()
    FileSyncWorker = prosync.FileSyncWorker

    src = tmp_path / "source.db"
    src.write_bytes(b"\x00" * 1024)
    tgt = tmp_path / "target.db"

    cfg = {
        "id": "bug4-test",
        "name": "file_kill_test",
        "source_file": str(src),
        "target_file": str(tgt),
        "checkpoint_before_sync": False,
    }

    worker = FileSyncWorker(cfg)
    finished_calls = []
    worker.finished.connect(lambda: finished_calls.append(True))

    worker.start()
    worker.kill()
    worker.wait(5000)

    assert not finished_calls, (
        "FileSyncWorker: finished wurde emittiert obwohl kill() aufgerufen wurde"
    )


def test_save_sync_report_recovers_from_corrupt_log(tmp_path, monkeypatch):
    """
    Bug #3: Korrupte sync_log.json darf zukünftige Report-Speicherungen nicht blockieren.

    Vorher: json.JSONDecodeError propagierte hoch → alle nachfolgenden Saves schlugen fehl.
    Nachher: except-Block setzt all_reports = [] und speichert den neuen Report sauber.
    """
    prosync = _load_prosync()

    log_file = tmp_path / "sync_log.json"
    log_file.write_text("{ungültiges json###", encoding="utf-8")

    monkeypatch.setattr(prosync, "sync_report_log_path", lambda: log_file)

    report = {
        "id": "bug3-test",
        "started_at": "2026-06-07T12:00:00+00:00",
        "duration_seconds": 0.5,
        "files_copied": 1,
        "files_deleted": 0,
        "files_skipped": 0,
        "bytes_copied": 5,
        "errors": [],
    }

    class _FakeSelf:
        pass

    prosync.MainWindow._save_sync_report(_FakeSelf(), report)

    saved = json.loads(log_file.read_text(encoding="utf-8"))
    assert isinstance(saved, list), "Log muss eine Liste sein"
    assert len(saved) == 1, f"Genau 1 Eintrag erwartet, bekam {len(saved)}"
    assert saved[0]["id"] == "bug3-test", "Report-ID stimmt nicht überein"


def test_scheduler_update_all_stops_timer_for_deleted_connection():
    """
    Bug #8: ConnectionScheduler.update_all() stoppte keinen Timer für gelöschte Verbindungen.
    Nach dem Löschen einer autosync-Verbindung lief deren Timer weiter und löste
    regelmäßig Syncs mit veralteten Daten aus.
    Fix: update_all() stoppt und entfernt Timer für IDs, die nicht mehr in der Config sind.
    """
    _get_app()
    prosync = _load_prosync()
    ConnectionScheduler = prosync.ConnectionScheduler

    class _MockCfg:
        def __init__(self, conns):
            self._conns = list(conns)
        def list_connections(self):
            return list(self._conns)

    conn_a = {"id": "conn-a", "name": "A",
               "autosync": {"enabled": True, "interval_minutes": 60}}
    conn_b = {"id": "conn-b", "name": "B",
               "autosync": {"enabled": True, "interval_minutes": 60}}

    cfg = _MockCfg([conn_a, conn_b])
    scheduler = ConnectionScheduler(cfg)
    scheduler.update_all()

    assert "conn-a" in scheduler.timers, "conn-a Timer soll nach update_all existieren"
    assert "conn-b" in scheduler.timers, "conn-b Timer soll nach update_all existieren"

    # Verbindung B aus Config entfernen, dann update_all aufrufen
    cfg._conns = [conn_a]
    scheduler.update_all()

    assert "conn-a" in scheduler.timers, "conn-a Timer soll weiter laufen"
    assert "conn-b" not in scheduler.timers, (
        "conn-b Timer muss nach Löschung aus Config gestoppt und entfernt werden"
    )
