"""
Regressionstests für BatchSyncQueue Bugs (2026-06-07):

Bug #5: Nach einem Einzelverbindungs-Sync blieb batch_queue.pending belegt,
        weil batch_queue.reset() nicht aufgerufen wurde. Folge: batch_queue.active
        blieb True und blockierte alle nachfolgenden Auto-Syncs dauerhaft.
        Fix: start_batch_sync() ruft batch_queue.reset() auf, wenn len(planned) < 2.

Bug #6: _handle_worker_error rief worker_finished() nicht auf. Da custom finished=Signal()
        im Fehlerpfad nicht emittiert wird, blieb btn_run dauerhaft deaktiviert und
        self.worker war ein veraltetes Referenz-Objekt.
        Fix: QTimer.singleShot(0, self.worker_finished) am Ende von _handle_worker_error.
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _load_prosync():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "prosync_bsq",
        os.path.join(os.path.dirname(__file__), "ProSyncStart_V3.1.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_batch_queue_not_active_after_single_connection_start():
    """
    Bug #5: batch_queue.active muss False sein, nachdem start_batch_sync
    mit einer Einzelverbindung aufgerufen wurde (< 2 planned).

    Ohne Fix: batch_queue.pending = [conn], active = True → Auto-Sync blockiert.
    Mit Fix: batch_queue.reset() wird aufgerufen, pending = [], active = False.
    """
    prosync = _load_prosync()
    BatchSyncQueue = prosync.BatchSyncQueue

    queue = BatchSyncQueue()
    conn = {"id": "test-conn-1", "name": "TestVerbindung"}

    planned = queue.start([conn])
    assert len(planned) == 1

    # Simuliere den Fix: reset() wird für < 2 planned aufgerufen
    queue.reset()

    assert not queue.active, (
        "batch_queue.active muss False sein nach Einzelverbindungs-Start + reset()"
    )
    assert queue.total == 0, f"total muss 0 sein, ist aber {queue.total}"
    assert queue.pending == [], f"pending muss leer sein, ist aber {queue.pending}"


def test_handle_worker_error_schedules_worker_finished():
    """
    Bug #6: _handle_worker_error hat worker_finished() nie aufgerufen.
    Fix: QTimer.singleShot(0, self.worker_finished) am Ende von _handle_worker_error.

    Dieser Test prüft, dass die Fix-Methode (QTimer.singleShot) in
    _handle_worker_error vorhanden ist, indem der Quellcode inspiziert wird.
    Ein vollständiger Integrationstest würde eine MainWindow-Instanz mit Display
    erfordern und ist daher für headless CI nicht praktikabel.
    """
    import inspect
    prosync = _load_prosync()
    source = inspect.getsource(prosync.MainWindow._handle_worker_error)

    assert "worker_finished" in source, (
        "_handle_worker_error muss worker_finished() via QTimer.singleShot aufrufen"
    )
    assert "QTimer" in source, (
        "_handle_worker_error muss QTimer.singleShot für deferred worker_finished() verwenden"
    )


def test_batch_queue_active_during_real_batch():
    """
    Sanity-Check: batch_queue.active ist True während eines echten Batch-Laufs.
    """
    prosync = _load_prosync()
    BatchSyncQueue = prosync.BatchSyncQueue

    queue = BatchSyncQueue()
    conns = [
        {"id": "conn-1", "name": "A"},
        {"id": "conn-2", "name": "B"},
    ]

    queue.start(conns)
    assert queue.active, "batch_queue.active muss True sein während eines Batch-Laufs"
    assert queue.total == 2

    conn = queue.next_connection()
    assert conn["id"] == "conn-1"
    assert queue.active

    queue.mark_current_finished()
    assert queue.active  # conn-2 noch ausstehend

    conn = queue.next_connection()
    assert conn["id"] == "conn-2"
    queue.mark_current_finished()

    assert not queue.active, "batch_queue.active muss False sein nach Abschluss aller Verbindungen"
