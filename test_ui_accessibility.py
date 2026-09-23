"""Offscreen accessibility regression checks for compact ProSync controls."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication, QPushButton


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parent
MODULE_PATH = PROJECT_ROOT / "ProSyncStart_V3.1.py"
READER_MODULE_PATH = PROJECT_ROOT / "ProSyncReader.py"


def load_prosync_module():
    spec = importlib.util.spec_from_file_location("prosync_ui_accessibility", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_reader_module():
    spec = importlib.util.spec_from_file_location("prosync_reader_ui_accessibility", READER_MODULE_PATH)
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


def test_reader_settings_button_exposes_accessible_context():
    app = QApplication.instance() or QApplication([])
    reader = load_reader_module()
    manager = reader.DBManager()
    window = reader.SearchWindow(manager)
    buttons = {
        button.accessibleName() or button.text(): button
        for button in window.findChildren(QPushButton)
    }

    settings_button = buttons["Suchdatenbanken verwalten"]
    assert settings_button.toolTip() == "Suchdatenbanken verwalten"
    assert settings_button.statusTip() == "Öffnet die Liste der eingebundenen Suchdatenbanken."
    assert settings_button.accessibleDescription() == (
        "Öffnet den Dialog zum Hinzufügen oder Entfernen eingebundener Suchdatenbanken."
    )

    window.close()
    app.processEvents()


def test_main_window_controls_and_indicators_expose_accessible_context(tmp_path):
    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()
    cfg_file = tmp_path / "prosync_test_config.json"
    cfg = prosync.ConfigManager(str(cfg_file))
    window = prosync.MainWindow(cfg)

    buttons = {
        button.accessibleName() or button.text(): button
        for button in window.findChildren(QPushButton)
    }

    assert "Neue Aufgabe hinzufügen" in buttons
    assert buttons["Neue Aufgabe hinzufügen"].statusTip() == "Öffnet das Menü zum Erstellen einer Ordner-, Datei- oder SFTP-Synchronisation."
    assert "Sicherheitsprüfung ausführen" in buttons
    assert "Synchronisation starten" in buttons
    assert buttons["Synchronisation starten"].statusTip() == "Startet die Ausführung der aktuell ausgewählten Synchronisationsaufgabe(n)."

    assert window.list.accessibleName() == "Synchronisations-Aufgaben"
    assert window.lbl_status_summary.accessibleName() == "Synchronisations-Statusübersicht"

    window.close()
    app.processEvents()


def test_file_connection_dialog_safety_info_case_insensitive(tmp_path):
    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()

    db_file = tmp_path / "orders.MDB"
    db_file.write_bytes(b"orders")

    dialog = prosync.FileConnectionDialog()
    dialog.source_file.setText(str(db_file))
    dialog.analyze_file()

    assert "MS Access" in dialog.safety_info.toPlainText()
    assert dialog.mode.currentText() == "one_way"
    dialog.close()
    app.processEvents()


def test_connection_dialog_form_inputs_expose_accessible_context():
    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()
    dialog = prosync.ConnectionDialog()

    assert dialog.name.accessibleName() == "Name der Aufgabe"
    assert dialog.name.placeholderText() != ""
    assert dialog.source.accessibleName() == "Quellordner"
    assert dialog.target.accessibleName() == "Zielordner"
    assert dialog.mode.accessibleName() == "Synchronisationsmodus"
    assert dialog.conflict.accessibleName() == "Konfliktbehandlung"
    assert dialog.chk_indexing.accessibleName() == "Datenbank-Indexierung & Historie aktivieren"
    assert dialog.chk_tags.accessibleName() == "Auto-Tags aus Ordnernamen generieren"
    assert dialog.db_path.accessibleName() == "Datenbank-Dateipfad"
    assert dialog.safety_info.accessibleName() == "Datenbank-Sicherheitsbericht"

    dialog.close()
    app.processEvents()


def test_file_connection_dialog_form_inputs_expose_accessible_context():
    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()
    dialog = prosync.FileConnectionDialog()

    assert dialog.name.accessibleName() == "Name der Aufgabe"
    assert dialog.name.placeholderText() != ""
    assert dialog.source_file.accessibleName() == "Quelldatei"
    assert dialog.target_file.accessibleName() == "Zieldatei"
    assert dialog.mode.accessibleName() == "Synchronisationsmodus"
    assert dialog.chk_checkpoint.accessibleName() == "WAL-Checkpoint vor Sync (für SQLite)"
    assert dialog.safety_info.accessibleName() == "Datei-Sicherheitsbericht"

    dialog.close()
    app.processEvents()


def test_sftp_target_dialog_accessible_context():
    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()
    dialog = prosync.SftpTargetDialog()

    assert dialog.name.accessibleName() == "Name der Aufgabe"
    assert dialog.source.accessibleName() == "Lokaler Quellordner"
    assert dialog.remote_host.accessibleName() == "SFTP-Host"
    assert dialog.remote_port.accessibleName() == "SFTP-Port"
    assert dialog.remote_username.accessibleName() == "SFTP-Benutzername"
    assert dialog.remote_key_file.accessibleName() == "SSH-Schlüsseldatei"
    assert dialog.target.accessibleName() == "Remote-Zielpfad"
    assert dialog.mode.accessibleName() == "Synchronisationsmodus"
    assert dialog.exclude_patterns.accessibleName() == "Dateiausschluss-Muster"
    assert dialog.allow_unknown_host_key.accessibleName() == "Unbekannten Host-Key beim ersten Verbinden automatisch vertrauen"

    dialog.close()
    app.processEvents()


def test_connection_list_widget_keyboard_navigation_and_shortcuts(tmp_path):
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QKeyEvent

    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()
    cfg_file = tmp_path / "prosync_test_config.json"
    cfg = prosync.ConfigManager(str(cfg_file))
    cfg.add_or_update_connection({
        "id": "c1",
        "name": "Test Aufgabe",
        "source": str(tmp_path / "src"),
        "target": str(tmp_path / "tgt"),
        "mode": "mirror",
        "type": "folder",
    })

    window = prosync.MainWindow(cfg)
    assert window.list.count() == 1
    window.list.setCurrentRow(0)

    # Test F2 triggers edit_selected_connection
    edit_called = []
    window.edit_selected_connection = lambda item=None: edit_called.append(True)
    event_f2 = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_F2, Qt.KeyboardModifier.NoModifier)
    window.list.keyPressEvent(event_f2)
    assert len(edit_called) == 1

    # Test Return triggers start_sync
    sync_called = []
    window.start_sync = lambda: sync_called.append(True)
    event_return = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    window.list.keyPressEvent(event_return)
    assert len(sync_called) == 1

    # Test Delete triggers delete_selected_connection
    delete_called = []
    window.delete_selected_connection = lambda: delete_called.append(True)
    event_del = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Delete, Qt.KeyboardModifier.NoModifier)
    window.list.keyPressEvent(event_del)
    assert len(delete_called) == 1

    # Test Ctrl+C triggers copy_selected_connection_info
    copy_called = []
    window.copy_selected_connection_info = lambda: copy_called.append(True)
    event_copy = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
    window.list.keyPressEvent(event_copy)
    assert len(copy_called) == 1

    # Test Ctrl+R shortcut exists and is connected
    assert hasattr(window, "shortcut_sync_r")
    assert window.shortcut_sync_r.key().toString() in ("Ctrl+R", "Strg+R")

    window.close()
    app.processEvents()


def test_reader_settings_dialog_keyboard_delete(tmp_path):
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QKeyEvent

    app = QApplication.instance() or QApplication([])
    reader = load_reader_module()
    manager = reader.DBManager()
    dummy_db = tmp_path / "test.db"
    dummy_db.write_bytes(b"")
    manager.add_db(str(dummy_db))

    dlg = reader.SettingsDialog(manager)
    assert dlg.list.count() == 1
    dlg.list.setCurrentRow(0)

    # Press Delete on list
    event_del = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Delete, Qt.KeyboardModifier.NoModifier)
    dlg.list.keyPressEvent(event_del)

    assert str(dummy_db) not in manager.dbs
    assert dlg.list.count() == 0

    dlg.close()
    app.processEvents()

