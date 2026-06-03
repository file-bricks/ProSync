# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- ProFiler-Companion: Toolbar-Button startet die optionale Companion-App über `app.profiler_path` oder den gemeinsamen Software-Baum
- GitHub Actions Smoke-Test-Workflow für Python 3.10 bis 3.12
- Gemeinsamer lokaler/CI-Teststarter `run_tests.py`
- `.gitattributes` für stabile Text- und Binärbehandlung im Repository
- Redigiertes Austauschformat `prosync-profile-v1.json` mit `EXPORTFORMAT.md`
- Toolbar-Menü `⇄ Profil austauschen` für Export/Import zwischen Desktop und Companion-Linien
- Regressionstest `test_portable_profile.py` für Redaction-, Import- und ID-Kollisionspfade
- Windows-Store-Material: `store_package.json`, `STORE_LISTING.md`, `PRIVACY_POLICY.md`, `SUPPORT.md` und `releases/windowsstore/`
- Reproduzierbarer Generator `_WARTUNG/generate_store_screenshots.py` für Store-Screenshots und `store_assets/`
- Smoke-Test `test_store_materials.py` für Demo-Konfiguration, Screenshot-Manifest und Store-Asset-Größen
- Linux-Plattform-Smoke `test_linux_platform_smoke.py` für `xdg-open`, redigierten UTF-8-Export, Tray-Initialisierung und Launch ohne Windows-Flags

### Geändert / Changed
- `.gitignore` deckt lokale Test-, Coverage- und Datenbank-Nebendateien vollständiger ab
- `requirements.txt` auf den aktuellen Projektstand 3.2.0 nachgezogen
- README dokumentiert lokale Datenschutzgrenzen, Tests und CI-Prüfung
- CI installiert die nötigen Qt-Laufzeitbibliotheken für PySide6 auf Ubuntu-Runnern
- `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` und README-Hinweise auf aktuelle Repo-Hygiene und echte deutsche Umlaute nachgezogen
- `app.profiler_path` akzeptiert jetzt auch relative Pfade und Windows-Umgebungsvariablen wie `%USERPROFILE%`
- `ConfigManager` exportiert/importiert portable Profile jetzt mit echter UTF-8-Ausgabe und ohne Rekonstruktion privater Pfade
- Importierte Austauschprofile erscheinen bewusst als lokale Entwürfe mit deaktiviertem Autosync und Pfad-Neuzuordnungs-Hinweis in der UI
- `run_tests.py` deckt jetzt zusätzlich die Store-Material-Checks und den Linux-Smoke ab
- Windows-Store-Pipeline ist jetzt bis zum lokalen Pretest und MSIX-Build dokumentiert; offen bleibt nur der erhöhte WACK-Lauf
- README, Aufgabenliste, Portierungsplan und CI-Compile-Liste dokumentieren den Linux-Quellpfad jetzt explizit

### Behoben / Fixed
- ProFiler-Companion fand konfigurierte Pfade aus `ProSync_config.json` bisher nicht, wenn sie relativ gespeichert oder über `%VAR%` referenziert waren
- Smoke-Test `test_companion_launch.py` deckt diese beiden Pfadvarianten jetzt explizit ab

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
