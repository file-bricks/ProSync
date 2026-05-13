# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- ProFiler-Companion: Toolbar-Button startet die optionale Companion-App über `app.profiler_path` oder den gemeinsamen Software-Baum
- GitHub Actions Smoke-Test-Workflow für Python 3.10 bis 3.12
- Gemeinsamer lokaler/CI-Teststarter `run_tests.py`

### Geändert / Changed
- `.gitignore` deckt lokale Test-, Coverage- und Datenbank-Nebendateien vollständiger ab
- `requirements.txt` auf den aktuellen Projektstand 3.2.0 nachgezogen
- README dokumentiert lokale Datenschutzgrenzen, Tests und CI-Prüfung
- CI installiert die nötigen Qt-Laufzeitbibliotheken für PySide6 auf Ubuntu-Runnern

## [3.2.0] - 2026-05-01

### Hinzugefügt / Added
- Batch-Sync über Mehrfachauswahl mit Kontextmenü-Einstieg und deduplizierter Queue
- Smoke-Test `test_batch_sync_queue.py` für Reihenfolge, Deduplizierung und Reset-Verhalten
- Sichere Beispielkonfiguration `ProSync_config.example.json`
- Reproduzierbares Windows-Build-Skript `build_exe.bat` für ProSync und ProSyncReader

### Geändert / Changed
- Hauptliste erlaubt jetzt Mehrfachauswahl für sequenzielle Batch-Läufe
- Laufende Batchs werden bei Fehler oder manuellem Stop kontrolliert beendet
- Lokale `ProSync_config.json` und `SKILL.md` werden nicht mehr im GitHub-Repo getrackt
- Frozen-Builds verwenden das EXE-Verzeichnis für Icons, Konfiguration und Reader-Start

### Behoben / Fixed
- Erfolgreiche Einzel-Sync-Benachrichtigungen werden nach Fehler oder manuellem Abbruch nicht mehr fälschlich als Erfolg gemeldet
- ProSyncReader wird im PyInstaller-Build als `ProSyncReader.exe` gestartet, statt eine Python-Datei neben der EXE vorauszusetzen

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
