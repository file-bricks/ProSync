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


def test_main_window_menubar_structure_and_mnemonics(tmp_path):
    """Verify accessible QMenuBar with Alt-Mnemonics and required submenus."""
    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()
    cfg_file = tmp_path / "prosync_test_config.json"
    cfg = prosync.ConfigManager(str(cfg_file))
    window = prosync.MainWindow(cfg)

    assert hasattr(window, "menubar")
    assert window.menubar.accessibleName() == "Hauptmenüleiste"

    # Verify menu titles and Mnemonics
    titles = [menu.title() for menu in window.menubar.findChildren(prosync.QMenu) if menu.title()]
    assert "&Datei" in titles
    assert "&Bearbeiten" in titles
    assert "&Aktionen" in titles
    assert "&Ansicht" in titles
    assert "&Sprache" in titles
    assert "&Hilfe" in titles

    # Check &Datei actions
    file_actions = {act.text(): act for act in window.menu_file.actions() if act.text()}
    assert any("Ordner" in k for k in file_actions)
    assert any("Datei" in k for k in file_actions)
    assert any("SFTP" in k for k in file_actions)
    assert any("exportieren" in k for k in file_actions)
    assert any("importieren" in k for k in file_actions)
    assert any("Beenden" in k for k in file_actions)

    # Check &Bearbeiten actions
    edit_actions = {act.text(): act for act in window.menu_edit.actions() if act.text()}
    assert any("bearbeiten" in k for k in edit_actions)
    assert any("löschen" in k for k in edit_actions)
    assert any("kopieren" in k for k in edit_actions)
    assert any("Sicherheitsprüfung" in k for k in edit_actions)

    # Check &Aktionen actions
    action_actions = {act.text(): act for act in window.menu_actions.actions() if act.text()}
    assert any("starten" in k for k in action_actions)
    assert any("pausieren" in k for k in action_actions)
    assert any("abbrechen" in k for k in action_actions)
    assert any("durchsuchen" in k for k in action_actions)
    assert any("ProFiler" in k for k in action_actions)

    # Check &Sprache actions
    lang_codes = [act.data() for act in window.lang_action_group.actions()]
    assert set(lang_codes) == {"de", "en", "es", "zh", "ja", "ru"}

    # Check &Hilfe actions
    help_actions = {act.text(): act for act in window.menu_help.actions() if act.text()}
    assert any("Tastaturkürzel" in k for k in help_actions)
    assert any("Über ProSync" in k for k in help_actions)

    window.close()
    app.processEvents()


def test_shortcuts_dialog_lifecycle_and_wcag():
    """Verify ShortcutsDialog has categories, BITV/WCAG notice and escape handling."""
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QKeyEvent

    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()

    dlg = prosync.ShortcutsDialog()
    assert dlg.isModal()
    assert "Tastaturkürzel & Barrierefreiheit" in dlg.windowTitle()
    assert dlg.accessibleName() == "Tastaturkürzel und Barrierefreiheits-Übersicht"

    # Verify categories in tree
    root_items = [dlg.tree.topLevelItem(i).text(0) for i in range(dlg.tree.topLevelItemCount())]
    assert "Datei & Profile" in root_items
    assert "Synchronisation & Aktionen" in root_items
    assert "Bearbeiten & Listen-Navigation" in root_items
    assert "Ansicht & Hilfe" in root_items

    # Verify BITV 2.0 / WCAG 2.1 notice label is present
    labels = [lbl.text() for lbl in dlg.findChildren(prosync.QLabel)]
    assert any("WCAG 2.1" in text and "BITV 2.0" in text for text in labels)

    # Test escape key closes
    event_esc = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
    dlg.keyPressEvent(event_esc)
    assert dlg.result() == prosync.QDialog.DialogCode.Accepted

    dlg.close()
    app.processEvents()


def test_about_dialog_lifecycle_and_metadata():
    """Verify AboutDialog exposes version, license and offline-first invariants."""
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QKeyEvent

    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()

    dlg = prosync.AboutDialog()
    assert dlg.isModal()
    assert "Über ProSync" in dlg.windowTitle()
    assert dlg.accessibleName() == "Über ProSync Dialog"

    labels = [lbl.text() for lbl in dlg.findChildren(prosync.QLabel)]
    assert any("ProSync V3.2" in text for text in labels)
    assert any("MIT Lizenz" in text for text in labels)
    assert any("Local-First" in text and "Zero-Egress" in text for text in labels)

    # Test escape key closes
    event_esc = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
    dlg.keyPressEvent(event_esc)
    assert dlg.result() == prosync.QDialog.DialogCode.Accepted

    dlg.close()
    app.processEvents()


def test_main_window_keyboard_shortcuts_and_dialog_methods(tmp_path):
    """Verify global keyboard shortcuts and helper methods for accessible dialogs."""
    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()
    cfg_file = tmp_path / "prosync_test_config.json"
    cfg = prosync.ConfigManager(str(cfg_file))
    window = prosync.MainWindow(cfg)

    # Global shortcuts
    assert hasattr(window, "shortcut_shortcuts_f1")
    assert window.shortcut_shortcuts_f1.key().toString() == "F1"

    assert hasattr(window, "shortcut_about_f1")
    assert window.shortcut_about_f1.key().toString() in ("Shift+F1", "Umschalt+F1")

    assert hasattr(window, "shortcut_focus_list")
    assert window.shortcut_focus_list.key().toString() in ("Ctrl+1", "Strg+1")

    assert hasattr(window, "shortcut_focus_ctrl")
    assert window.shortcut_focus_ctrl.key().toString() in ("Ctrl+2", "Strg+2")

    # In offscreen mode, helper methods return the dialog instance
    dlg_sc = window.show_shortcuts_dialog()
    assert isinstance(dlg_sc, prosync.ShortcutsDialog)
    dlg_sc.close()

    dlg_ab = window.show_about_dialog()
    assert isinstance(dlg_ab, prosync.AboutDialog)
    dlg_ab.close()

    window.close()
    app.processEvents()


def test_main_window_language_switching_and_retranslation(tmp_path):
    """Verify dynamic runtime language switching and UI retranslation."""
    app = QApplication.instance() or QApplication([])
    prosync = load_prosync_module()
    cfg_file = tmp_path / "prosync_test_config.json"
    cfg = prosync.ConfigManager(str(cfg_file))
    window = prosync.MainWindow(cfg)

    assert window.current_language == "de"
    assert window.menu_file.title() == "&Datei"

    # Switch to English
    window.switch_language("en")
    assert window.current_language == "en"
    assert window.menu_file.title() == "&File"
    assert window.menu_help.title() == "&Help"

    # Switch back to German
    window.switch_language("de")
    assert window.current_language == "de"
    assert window.menu_file.title() == "&Datei"
    assert window.menu_help.title() == "&Hilfe"

    window.close()
    app.processEvents()
