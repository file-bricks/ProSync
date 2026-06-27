# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Behoben / Fixed (2026-06-28, Bugsweep 27)
- **ConnectionDB.close() Hardening:** `self.conn` wird jetzt nach `self.conn.close()` auf `None` gesetzt — ein zweiter `close()`-Aufruf bricht sauber im Guard ab statt einen spurious `ProgrammingError` zu erzeugen.
- **FolderSyncWorker WAL-Checkpoint:** `run()` ruft `self.db.close()` jetzt im `finally`-Block auf — `PRAGMA wal_checkpoint(FULL)` wird deterministisch ausgelöst statt auf den Python-GC zu warten.
- Regressionstest `test_bugsweep_resweep_20260628.py` (4 Tests) ergänzt.

### Hinzugefügt / Added
- `llms.txt` für LLM-Crawler-Indexierung mit Audience, Search Phrases und Last-checked
- Headless-CLI für Automationen: `--list`, `--run <id|name>`, `--all`, `--config` und `--quiet` starten vorhandene ProSync-Verbindungen ohne GUI über dieselben Datei-/Ordner-Worker.
- Regressionstest `test_batch_sync_queue_bugs.py` für Bugs #5 (BatchQueue.reset fehlt) und #6 (worker_finished fehlt im Fehlerpfad)
- Regressionstest `test_cli_headless.py` für Verbindungsauflistung, Einzeldatei-Sync und sequenziellen `--all`-Lauf.
- Regressionstest `test_folder_sync_worker_bugs.py` für Bugs #1–#4 (started_at, is_killed-Guards, sync_log-Korruption) und #8 (stale Timer in ConnectionScheduler)
- `web_companion/` als statischer Web/PWA-Companion für `prosync-profile-v1.json` mit Datei-/JSON-Import, Demo-Profil, Offline-Restore, Service Worker und Node-Tests
- Regressionstest `test_ui_accessibility.py` für sprechende Accessible Names und Tooltips an symbolischen Pfad-Auswahlbuttons

### Geändert / Changed
- README von Deutsch-first auf English-first umgebaut; Deutsch als sekundäre Sektion
- `.gitignore` schließt interne Planungsdokumente (`ENTWICKLUNGSPLAN*.md`, `Feature_Analyse*.md`) aus
- GitHub-Actions-Workflows auf aktuelle Major-Versionen aktualisiert (`actions/checkout@v6`, `actions/setup-python@v6`, `actions/stale@v10`, `actions/first-interaction@v3`)
- `PORTIERUNGSPLAN.md` und `AUFGABEN.txt` dokumentieren den Companion jetzt als erledigten P2-Web/PWA-Schritt; Android/iOS bleiben nachgelagerte PWA-Smokes
- Symbolische Ordner-/Datei-Auswahlbuttons in beiden Verbindungsdialogen exponieren jetzt sprechende Accessible Names und Tooltips statt nur `📂`, `📄` und `💾`

### Behoben / Fixed (2026-06-07)
- `run_tests.py` und README-Testbefehle verwenden wieder den vorhandenen Source-Smoke `source_platform_smoke.py` statt des alten Namens `test_linux_platform_smoke.py`
- **Bug #1:** `started_at` enthielt End-Zeit statt Start-Zeit — `_started_at` wird nun vor dem Sync-Loop erfasst
- **Bug #2:** Abgebrochener `FolderSyncWorker` emittierte fälschlich `progress(100)` und `finished` — `is_killed`-Guard vor Emit-Sequenz
- **Bug #3:** Korrupte `sync_log.json` blockierte alle zukünftigen Report-Speicherungen — `except (json.JSONDecodeError, UnicodeDecodeError, OSError)` hinzugefügt
- **Bug #4:** Abgebrochener `FileSyncWorker` emittierte fälschlich `finished` — `is_killed`-Guard vor Done-Block
- **Bug #5:** `batch_queue.pending` blieb nach Einzelverbindungs-Sync belegt — `batch_queue.reset()` bei `len(planned) < 2`
- **Bug #6:** `_handle_worker_error` rief `worker_finished()` nicht auf — `QTimer.singleShot(0, self.worker_finished)` ergänzt
- **Bug #8:** `ConnectionScheduler.update_all()` stoppte keine Timer für gelöschte Verbindungen — stale-Timer-Cleanup hinzugefügt
- **Bug #9:** `ConnectionScheduler.update_connection()` crasht nicht mehr bei ungültigem `autosync.interval_minutes` aus Alt-/manuellen Konfigurationen — ungültige Werte fallen jetzt defensiv auf 15 Minuten zurück, Regressionstest ergänzt


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
- Source-Plattform-Smoke `source_platform_smoke.py` (umbenannt von `test_linux_platform_smoke.py`) für `xdg-open`, redigierten UTF-8-Export, Tray-Initialisierung und plattformspezifische Launch-Logik
- CI-Workflow `.github/workflows/source-platform-smoke.yml` führt den Smoke auf ubuntu-latest und macos-latest aus

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
- Leeres `APPDATA` erzeugt für Sync-Reports und den portablen Profil-Export keinen relativen Pfad im Arbeitsordner mehr, sondern fällt sauber auf das Nutzerverzeichnis zurück

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
