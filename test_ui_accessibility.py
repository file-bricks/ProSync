"""Offscreen accessibility regression checks for compact ProSync dialog buttons."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication, QPushButton


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parent
MODULE_PATH = PROJECT_ROOT / "ProSyncStart_V3.1.py"


def load_prosync_module():
    spec = importlib.util.spec_from_file_location("prosync_ui_accessibility", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _button_map(dialog):
    return {button.accessibleName(): button for button in dialog.findChildren(QPushButton)}


def test_folder_connection_dialog_compact_buttons_expose_accessible_context():
    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()
    dialog = prosync.ConnectionDialog()
    buttons = _button_map(dialog)

    assert buttons["Quellordner auswählen"].toolTip() == "Quellordner auswählen"
    assert buttons["Zielordner auswählen"].toolTip() == "Zielordner auswählen"
    assert buttons["Datenbank-Datei auswählen"].toolTip() == "Datenbank-Datei auswählen"
    assert buttons["Quelle auf Datenbanken scannen"].toolTip() == "Quelle auf Datenbanken scannen"

    dialog.close()
    app.processEvents()


def test_file_connection_dialog_compact_buttons_expose_accessible_context():
    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()
    dialog = prosync.FileConnectionDialog()
    buttons = _button_map(dialog)

    assert buttons["Quelldatei auswählen"].toolTip() == "Quelldatei auswählen"
    assert buttons["Zieldatei auswählen"].toolTip() == "Zieldatei auswählen"
    assert buttons["Datei analysieren"].toolTip() == "Datei analysieren"

    dialog.close()
    app.processEvents()
