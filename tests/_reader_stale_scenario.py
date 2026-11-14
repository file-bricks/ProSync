"""Szenario für test_bugsweep_20261114: zwei Suchen kurz hintereinander im ProSyncReader.

Die erste (alte) Suche liefert erst, nachdem die zweite gestartet wurde. Ausgegeben wird, ob ihre Treffer
in der Liste landen und ob ein laufender Worker hart per terminate() beendet wurde.
Läuft als eigener Prozess, weil das Suchfenster eine QApplication braucht.
Aufruf: python _reader_stale_scenario.py <ProSyncReader.py> <arbeitsordner>
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]).resolve().parent))
os.chdir(sys.argv[2])
from PySide6.QtCore import QObject, Signal  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

app = QApplication(sys.argv)
spec = importlib.util.spec_from_file_location("prosync_reader_stale", sys.argv[1])
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class FakeWorker(QObject):
    """Steht für einen noch laufenden SearchWorker/PreviewWorker."""

    results_found = Signal(list)
    preview_ready = Signal(str)
    finished = Signal()
    created = []

    def __init__(self, *_args):
        super().__init__()
        self.terminated = False
        FakeWorker.created.append(self)

    def isRunning(self):  # noqa: N802
        return True

    def start(self):
        pass

    def terminate(self):
        self.terminated = True


reader.SearchWorker = FakeWorker
reader.PreviewWorker = FakeWorker
reader.config_path = lambda: str(Path(sys.argv[2]) / "search_config.json")

window = reader.SearchWindow(reader.DBManager())
window.search_field.setText("alt")
window.execute_search()
window.search_field.setText("neu")
window.execute_search()
old_search, new_search = FakeWorker.created[0], FakeWorker.created[1]
old_search.results_found.emit([{"name": "VERALTET.txt", "path": "x/VERALTET.txt", "mtime": 0, "type": "file"}])
new_search.results_found.emit([{"name": "aktuell.txt", "path": "x/aktuell.txt", "mtime": 0, "type": "file"}])
app.processEvents()
shown = [window.results_list.item(i).text() for i in range(window.results_list.count())]

item = window.results_list.item(0)
window.on_item_clicked(item)
window.on_item_clicked(item)
old_preview, new_preview = FakeWorker.created[2], FakeWorker.created[3]
new_preview.preview_ready.emit("NEUE VORSCHAU")
old_preview.preview_ready.emit("ALTE VORSCHAU")
app.processEvents()

print(json.dumps({
    "shown": shown,
    "preview": window.preview_text.toPlainText(),
    "terminated": any(w.terminated for w in FakeWorker.created),
}))
