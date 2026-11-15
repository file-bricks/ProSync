"""Szenario für test_bugsweep_20261114: Batch starten, sofort abbrechen, UI-/Queue-Zustand ausgeben.

Läuft als eigener Prozess, weil das Hauptfenster eine QApplication braucht, andere Testmodule im
selben pytest-Prozess aber bereits eine QCoreApplication anlegen.
Aufruf: python _batch_stop_scenario.py <ProSyncStart_V3.1.py> <arbeitsordner>
"""
import importlib.util
import json
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

sys.path.insert(0, str(Path(sys.argv[1]).resolve().parent))  # logger, prosync_utils, …
app = QApplication(sys.argv)
QMessageBox.warning = staticmethod(lambda *a, **k: None)
spec = importlib.util.spec_from_file_location("prosync_batch_stop", sys.argv[1])
prosync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prosync)

root = Path(sys.argv[2])
connections = []
for name in ("A", "B"):
    src, tgt = root / name / "src", root / name / "tgt"
    src.mkdir(parents=True)
    tgt.mkdir()
    for i in range(50):
        (src / f"f{i}.txt").write_text("x", encoding="utf-8")
    connections.append({"id": name, "name": name, "type": "folder", "source": str(src),
                        "target": str(tgt), "mode": "mirror", "indexing": False})
cfg = prosync.ConfigManager(str(root / "cfg.json"))
for conn in connections:
    cfg.add_or_update_connection(conn)

window = prosync.MainWindow(cfg)
window.start_batch_sync(connections)
worker = window.worker
window.stop_worker()
worker.wait(10000)
for _ in range(20):
    app.processEvents()
print(json.dumps({
    "batch_active": window.batch_queue.active,
    "run_enabled": window.btn_run.isEnabled(),
    "worker_none": window.worker is None,
}))
window.scheduler.stop_all()
