"""Szenario für test_bugsweep_20261114: „Beenden“ im Tray-Menü, während ein Sync läuft.

Startet einen Ordner-Sync mit vielen Dateien, ruft force_quit() und lässt app.exec() zurückkehren.
Gibt den Worker-Zustand nach dem Beenden aus; der Prozess-Exitcode zeigt, ob Qt beim Aufräumen abbricht.
Aufruf: python _quit_during_sync_scenario.py <ProSyncStart_V3.1.py> <arbeitsordner>
"""
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]).resolve().parent))
from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

app = QApplication(sys.argv)
QMessageBox.warning = staticmethod(lambda *a, **k: None)
spec = importlib.util.spec_from_file_location("prosync_quit", sys.argv[1])
prosync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prosync)

root = Path(sys.argv[2])
src, tgt = root / "src", root / "tgt"
src.mkdir(parents=True)
tgt.mkdir()
for i in range(3000):
    (src / f"f{i}.txt").write_text("x" * 2000, encoding="utf-8")
conn = {"id": "q", "name": "Q", "type": "folder", "source": str(src), "target": str(tgt),
        "mode": "mirror", "indexing": False}
cfg = prosync.ConfigManager(str(root / "cfg.json"))
cfg.add_or_update_connection(conn)
window = prosync.MainWindow(cfg)
window.start_batch_sync([conn])
worker = window.worker
QTimer.singleShot(50, window.force_quit)
app.exec()
print(json.dumps({"worker_running_after_quit": bool(worker.isRunning())}), flush=True)
