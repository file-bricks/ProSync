# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Behoben / Fixed (2026-10-02)
- **Cross-OS Pfadregeln, Normalisierung & Kalender-Zeitplanung Resilienz (Bugsweep 2026-10-02):**
  - **Falsch-positive "redundant-segments"-Erkennung in `cross_os_rules.py` behoben:** `describe_path_normalization` nutzte `_SEPARATOR_RE.search(...)` mit `r"/+"`, wodurch ausnahmslos jeder POSIX-Pfad mit regulärem Schrägstrich (z. B. `"docs/readme.txt"`) fälschlich als pfadverändernd mit `"redundant-segments"` deklariert wurde. Behoben durch gezielte Erkennung echter Redundanzen (mehrfache Slashes `/{2,}`, trailing Slashes auf Nicht-Root-Dateipfaden, Whitespace oder relative Segmente wie `./`).
  - **Reine Case-Konflikte in `find_cross_os_path_conflicts` bereinigt:** Bei Pfadkollisionen, die sich nur in Groß-/Kleinschreibung unterscheiden (z. B. `["folder/A", "folder/a"]`), wird nun präzise `('case', 'case-insensitive-key')` statt fälschlichem `"redundant-segments"` gemeldet.
  - **Empty-Path & Dot-Kollisionsschutz in `portable_path_key`:** `portable_path_key("")` und `portable_path_key(None)` liefern jetzt einen leeren String `""` statt `"."` (verhindert irrtümliche Kollision leerer Pfade mit dem aktuellen Verzeichnis `"."`).
  - **Vollständige englische 2-Letter-Wochentagscodes in `schedule_time.py`:** `WEEKDAY_ALIASES` um die fehlenden englischen Standardkürzel `"tu"` (Dienstag), `"we"` (Mittwoch), `"th"` (Donnerstag) und `"su"` (Sonntag) ergänzt.
  - **Spanische Wochentage und Gruppen-Aliase in `schedule_time.py`:** Vollständige Unterstützung der spanischen Wochentage (`"lunes"`, `"martes"`, `"miercoles"`, `"miércoles"`, `"jueves"`, `"viernes"`, `"sabado"`, `"sábado"`, `"domingo"`, Kürzel `"lu"`, `"ma"`, `"ju"`, `"vi"`) sowie Gruppen-Aliase (`"laborables"`, `"dias laborables"`, `"fin de semana"`, `"diario"`, `"todos"`).
  - **Wochentags-Bereichssyntax (Range Parsing):** Unterstützung von Bereichstokens wie `"mon-wed"`, `"mo-mi"`, `"1-4"`, `"0..2"` sowie Wochenend-Wrap-Arounds (`"fri-mon"`) in `parse_weekdays()`.
  - **Kombinierte Wochentagstokens:** Gruppen-Aliase können nun nahtlos mit Einzeltagen kombiniert werden (z. B. `"workdays,sat"`, `"mon-fri,sun"` oder als Liste `["workdays", "sun"]`).
  - **Strikter Typenschutz gegen Booleans:** `parse_weekdays()` weist `bool` (die in Python Subtypen von `int` sind) explizit mit `TypeError` ab, statt sie stumm als Wochentage 0 (Montag) oder 1 (Dienstag) zu interpretieren.
  - **Mixed-Type Sortierresilienz in `ConfigManager._portable_autosync`:** `weekdays`-Listen mit gemischten Typen (`int` und `str`) werden sortiersicher serialisiert ohne `TypeError`.
  - **RuntimeError-Abfang in `ConnectionScheduler._start_daily_timer`:** Abfang von `(TypeError, ValueError, RuntimeError)` verhindert unhandled Scheduler-Abstürze bei unauflösbaren Zeitplänen.
  - **11 neue hermetische Regressionstests:** In `tests/test_bugsweep_cross_os_and_schedule_resilience_20261002.py` verankert (Gesamtsuite: 194/194 passed).

### Hinzugefügt / Added (2026-10-01)
- **Linux XDG Desktop-Integration, Autostart-Manager & Phase 3 Wochentags-Zeitpläne (TW-PS-09 / Platform P2):**
  - **Plattformübergreifender `AutostartManager`:** Unterstützung der XDG Autostart-Spezifikation unter Linux (`$XDG_CONFIG_HOME/autostart/prosync.desktop` bzw. `~/.config/autostart/prosync.desktop`); atomares Schreiben mit `fsync` und `os.replace`, defensives Auslesen (`X-GNOME-Autostart-enabled`) und transparente Windows-Registry-Parität.
  - **Linux Desktop Packaging:** Standardisierte XDG `.desktop`-Datei unter `packaging/linux/prosync.desktop` sowie Installationsdokumentation `packaging/linux/README.md` für systemweite und benutzerweite Desktop-Integration (GNOME, KDE Plasma, XFCE).
  - **Erweiterte 9-Punkte Linux-Platform-Smoke-Suite:** `tests/linux_platform_smoke.py` um Check 9 (`test_linux_autostart_and_desktop_entry`) erweitert; in Standalone-Runner und `tests/test_platform_smoke_contract.py` integriert (9/9 Checks bestanden).
  - **Wochentags-Zeitpläne (Phase 3 `SCHEDULE_CONTRACT.md`):** `schedule_time.py` um `parse_weekdays()` und flexible Wochentagsfilterung in `next_daily_run()` erweitert (Aliase: `workdays`/`werktage`, `weekend`/`wochenende`, `all`/`täglich`, Wochentagsnamen DE/EN sowie kommagetrennte Token/Zahlen); automatischer Wochenend-Übersprung und daylight-saving-sichere Berechnung über bis zu 14 Tage Suchfenster.
  - **Scheduler- & Profil-Integration:** `ConnectionScheduler._start_daily_timer` übergibt konfigurierte `weekdays` an `next_daily_run()`; `_portable_autosync()` erhält Wochentage im redigierten Export-Format `prosync-profile-v1.json`.
  - **12 neue automatisierte Tests:** 6 Tests in `tests/test_autostart_cross_platform.py` und 6 neue Testfälle in `test_schedule_time.py`; Vollsuite 183/183 passed (100% grün).

### Behoben / Fixed (2026-09-30)
- **FileSyncWorker, _atomic_copy2 & FolderSyncWorker Resilienz (Bugsweep 2026-09-30):**
  - **Zieldatei-Verifizierung in `FileSyncWorker`:** Stille Falsch-Positiv-Meldung behoben: Fehlende Zieldateien nach dem Kopiervorgang (`if not os.path.exists(target_file)`) lösen nun einen sauberen Fehler aus (`error.emit`), statt die Prüfung zu überspringen und fälschlicherweise Erfolg zu melden.
  - **Sync-Report Signal & Integration:** `sync_report = Signal(dict)` in `FileSyncWorker` ergänzt, sodass Einzeldatei-Synchronisationen vollständige Laufstatistiken (`connection`, `connection_id`, `mode`, `duration_seconds`, `files_copied`, `bytes_copied`) emittieren; Speicherung in `sync_log.json` via `MainWindow` und CLI `run_headless_connection` angebunden.
  - **Pause-Unterstützung (`is_paused`):** `FileSyncWorker.run()` respektiert nun `self.is_paused` vor Checkpoint-, Kopiervorgangs- und Verifizierungsphasen, anstatt Pause-Signale der Benutzeroberfläche zu ignorieren.
  - **Defensive Pfadvalidierung:** Abweisung von Verzeichnissen als `source_file` oder `target_file` sowie Erkennung und Abweisung identischer Quell- und Zieldateien (`os.path.normcase(os.path.abspath(...))`) vor dem Kopiervorgang.
  - **Windows Read-Only Resilienz in `_atomic_copy2`:** `_atomic_copy2` entfernt Schreibschutz-Attribute (`S_IREAD`) auf existierenden Zieldateien vor `os.replace` (verhindert Windows `PermissionError [WinError 5]`) und stellt sicher, dass temporäre `.prosync_tmp`-Dateien auch bei schreibgeschützter Quelldatei im Fehlerfall restlos aufgeräumt werden.
  - **Windows Read-Only Resilienz in `FolderSyncWorker` (`DELETE_R`):** Schreibgeschützte Zieldateien werden im Mirror-Modus vor dem Löschen schreibbar gemacht, wodurch `os.remove` nicht mehr mit `PermissionError` abbricht.
  - **8 neue hermetische Regressionstests:** In `tests/test_bugsweep_file_sync_and_atomic_copy_resilience_20260930.py` implementiert (100% grün).

### Geändert / Changed (2026-09-29)
- **Pfad A Repository-Hygiene, CI Lifecycle Workflows, Multi-Host Lock-Schutz, Level 1 SBOM Text-Companion & Vertragstest-Erweiterung:**
  - **Version-Freeze Disziplin (`T-20260920-167562623`):** Versionsnummer `3.2.0` in `pyproject.toml`, Quellcode und Manifesten strikt unverändert beibehalten.
  - **CI Lifecycle Workflows & Governance-Labels:** `.github/workflows/auto-assign.yml` (actions/github-script@v7, timeout-minutes: 5, Concurrency cancel-in-progress: true, least-privilege permissions: pull-requests: write, issues: write) und `.github/workflows/label-sync.yml` (EndBug/label-sync@v2, timeout-minutes: 5, Concurrency cancel-in-progress: true, least-privilege permissions: issues: write) neu provisioniert; kanonische `.github/labels.yml` mit 11 Standard-Governance-Labels gemäß GOVERNANCE.md §4.2 etabliert.
  - **Multi-Host Sync-, Lock- & Cache-Defense (`.gitignore`):** Schutzregeln für erweiterte Host-Tokens (`Desktop.ini`, `*_WORKSTATION*`, `*_WORKSTATION-LG*`, `*-WORKSTATION.*`, `*-WORKSTATION-LG.*`) und kanonische Lock-Dateien (`LOCK.user.*`, `LOCK.until.*`, `LOCK.condition.*`) gehärtet.
  - **Level 1 SBOM Text-Companion & Lizenzaudit (`THIRD_PARTY_LICENSES.txt` & `THIRD_PARTY_LICENSES.md`):** Re-Auditiert auf Stand 2026-09-29 mit Bestätigung der kanonischen `NOTICE`-Attribution, unprivilegierter `RunAsInvoker` Non-Elevation Zertifizierung (`INV-RUNAS-02`), Zero-Copyleft & 100% permissiven/LGPL-isolierten Laufzeitabhängigkeiten sowie Verifikation aller 10 Governance-Invarianten `INV-LOCAL-01` bis `INV-SLA-10`.
  - **PEP 621 Standardisierung & Paketierung (`pyproject.toml`):** `Level 1 SBOM` URL in `[project.urls]` registriert; `[tool.pytest.ini_options]` `norecursedirs` um `.turbo` und `.nyc_output` erweitert.
  - **Dokumentations-, Badge- & RAG-Kontext-Aktualisierung:** Shields.io Badges für `Verified: 2026-09-29` (`Geprüft` / `Verificado`) und verifizierte Tests über alle drei Sprachfassungen (`README.md`, `README_de.md`, `README.es.md`) synchronisiert; `llms.txt` auf Stand 2026-09-29 aktualisiert.
  - **Automatisierte Vertragstests (`tests/test_metadata.py`):** Neue Contract-Tests für CI Lifecycle Workflows (`auto-assign.yml`, `label-sync.yml`, `.github/labels.yml`), `Level 1 SBOM` Plaintext Companion Recency und Invarianten, `pyproject.toml` URL-Registrierung und CHANGELOG `[Unreleased]` implementiert.

### Geändert / Changed (2026-09-28)
- **Pfad B Marketing, Discoverability, Visual Architecture & Trilinguale 18-Punkte-Navigationsparität:**
  - **Version-Freeze Disziplin (`T-20260920-167562623`):** Versionsnummer `3.2.0` in `pyproject.toml`, Quellcode und Manifesten strikt unverändert beibehalten.
  - **Trilinguale 18-Punkte-Schnellnavigation mit reziproken dualen HTML-Ankern:** Vollständige Harmonisierung von `README.md`, `README_de.md` und `README.es.md` mit reziproken dualen HTML-Anker-Aliasen (`<a id="sec-01"></a>` bis `<a id="sec-18"></a>`) über alle 18 Standardabschnitte unter lückenloser Erhaltung aller historischen Legacy-Anker.
  - **Statutory Notice & 48h Security Response SLA:** Gesetzlicher Haftungsausschluss gemäß § 521 BGB (Gefälligkeitsrecht) und verbindliche 48h Security Response SLA über alle drei Sprachfassungen (`README.md`, `README_de.md`, `README.es.md`) sowie `SECURITY.md` harmonisiert.
  - **Level 1 SBOM Invariant Cross-Reference Matrix (`THIRD_PARTY_LICENSES.md`):** Re-Auditiert auf Stand 2026-09-28 (v3.2.0) mit formaler 10-Invarianten-Kreuztabelle (`INV-LOCAL-01` bis `INV-SLA-10`), `RunAsInvoker` Non-Elevation Zertifizierung, Zero-Copyleft & Zero-Egress isolation guarantee, Verlinkung von `NOTICE` und `THIRD_PARTY_LICENSES.txt`.
  - **Kanonische NOTICE Attribution:** Formale `NOTICE`-Datei im Repo-Root um Querverweis auf `THIRD_PARTY_LICENSES.txt` ergänzt; in `pyproject.toml` Notice URL und `license-files` Whitelist verankert.
  - **Paketierung & Pytest-Härtung (`pyproject.toml`):** `addopts = "-ra -v --basetemp=.pytest_temp"` und gehärtetes `norecursedirs` mit `.pytest_temp` verankert; kanonische Homepage-URL auf `https://github.com/file-bricks/ProSync#readme` und `Third-Party Licenses (Text)` URL registriert.
  - **Dokumentations-, Badge- & RAG-Kontext-Aktualisierung:** Shields.io Badges für `Attribution: NOTICE`, `Level 1 SBOM: Verified`, `Tests: 158 passed | 100% green`, `Python: 3.10 | 3.11 | 3.12 | 3.13` und `Verified: 2026-09-28` (`Geprüft` / `Verificado`) über alle drei Sprachfassungen synchronisiert; `llms.txt` auf Stand 2026-09-28 und 158 verifizierte Tests Baseline aktualisiert.
  - **Automatisierte Vertragstests (`tests/test_metadata.py`):** Contract-Tests für trilinguale `sec-01`..`sec-18` Anker-Parität, Level 1 SBOM Invariant Cross-Reference Matrix, § 521 BGB Rechtsbelehrung, aktualisierte Badges und Pytest `--basetemp` Härtung erweitert.

### Geändert / Changed (2026-09-26)
- **Pfad A Technische Hygiene, CI/CD Lifecycle Hardening, NOTICE Attribution & PEP 621 Standardisierung:**
  - **Version-Freeze Disziplin (`T-20260920-167562623`):** Versionskonstante `version = "3.2.0"` in `pyproject.toml`, Quellcode und Manifesten strikt unverändert beibehalten.
  - **Kanonische NOTICE Attributionsdatei:** Neu im Repository-Root angelegt (`NOTICE`) mit formaler Urheberrechts- und Open-Source-Attribution für Lukas Geiger, file-bricks und open-bricks unter MIT-Lizenz; verknüpft in `pyproject.toml` (`[project.urls]` Notice URL und `license-files`), `README.md`, `README_de.md`, `README.es.md` und `THIRD_PARTY_LICENSES.md`.
  - **PEP 621 Standardisierung & 20/20 Keywords (`pyproject.toml`):** `license-files` Whitelist standardisiert (`["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md", "THIRD_PARTY_LICENSES.txt"]`), 20/20 Keywords gesättigt abgestimmt auf GitHub Topics (`backup`, `cross-platform`, `data-integrity`, `database-backup`, `database-protection`, `desktop-app`, `file-bricks`, `file-sync`, `local-first`, `offline-first`, `open-bricks`, `privacy-first`, `pyside6`, `python`, `sqlite`, `sqlite-backup`, `sync`, `wal-checkpoint`, `windows-desktop`, `zero-egress`), `norecursedirs` in `[tool.pytest.ini_options]` um `.hypothesis` und `.pytest_temp` gehärtet.
  - **CI/CD Lifecycle Hardening (`.github/workflows/`):** Bytecode-Validierungsgate `python -m compileall -q .` in `tests.yml` und `source-platform-smoke.yml` verankert; Concurrency-Gruppe mit `cancel-in-progress: true` und Timeouts verifiziert.
  - **Multi-Host Sync-, Lock- & Cache-Defense (`.gitignore`):** Schutzregeln für erweiterte Host-Tokens (`*-MacBook*`, `*-IDEAPAD*`), kanonische Lock-Dateien (`.automation-lock`), Test-Runner Caches (`.pytest_temp/`, `.pytest_tmp*/`) und Synchronisationskonflikt-Muster (`*.conflict-*`, `*-CONFLIT-*`, `*-conflict-*`) implementiert.
  - **Level 1 SBOM & Lizenzaudit (`THIRD_PARTY_LICENSES.md`):** Re-Auditiert auf Stand 2026-09-26 mit formalem Querverweis auf `[NOTICE](NOTICE)`, Bestätigung aller 10 Governance-Invarianten `INV-LOCAL-01` bis `INV-SLA-10`, unprivilegierter `RunAsInvoker` Non-Elevation Zertifizierung und 100% permissiver/LGPL dynamischer Verlinkungsisolation.
  - **Dokumentation & Badges (`README.md`, `README_de.md`, `README.es.md`, `llms.txt`):** Shields.io Badges für `Attribution: NOTICE` und `Last-Checked: 2026-09-26` harmonisiert; `llms.txt` Stand 2026-09-26 mit 153+ Tests Baseline und kanonischer NOTICE-Verlinkung aktualisiert.
  - **Automatisierte Vertragstests (`tests/test_metadata.py`):** Neue Contract-Tests für `NOTICE`-Attributionsdatei, PEP 621 Notice URL, license-files und Keywords, erweiterte `.gitignore` Multi-Host/Lock-Muster, Level 1 SBOM Recency & NOTICE Querverweis und CHANGELOG `[Unreleased]` implementiert.

### Hinzugefügt / Added (2026-09-19)
- **Internationalisierung (I18N) & Mehrsprachen-Parität (Policy P-006 Tier-2 Standard):**
  - **Vollständiger 6-Sprachen-Katalog (`locales/translations.json`):** Übersetzungskatalog auf 100 UI-, Dialog-, Status- und Aktionsschlüssel mit 100% Parität über alle 6 Standard-Sprachen (Deutsch `de`, Englisch `en`, Spanisch `es`, vereinfachtes Chinesisch `zh`, Japanisch `ja`, Russisch `ru`) ausgebaut; inklusive `_meta`-Block v2.0.0.
  - **Upgrade `translator.py`:** Deterministische 4-stufige Fallback-Hierarchie (`target_lang -> en -> de -> key`), Singleton `get_translator()`, Modul-Shortcut `t(key, **kwargs)`, `set_language()`, `SUPPORTED_LANGUAGES`, `LANGUAGE_NAMES` und `LANGUAGE_DISPLAY_NAMES` implementiert; Rückwärtskompatibilität für bestehende Testsuiten vollständig bewahrt.
  - **CI-Gate Scanner (`manage_translations.py`):** CLI-Option `--check` implementiert, die den Übersetzungskatalog auf Vollständigkeit und 100% Sprachabdeckung aller 6 Zielsprachen validiert (Exit Code 0/1).
  - **Spanische Dokumentation (`README.es.md`):** Vollständige spanische Übersetzung mit identischer 18-Punkte-Schnellnavigation, reziproken Ankern, dualen Mermaid-Diagrammen, Ziel-Personas, Vergleichsmatrix und Ökosystem-Tabelle bereitgestellt; Sprachwechsler in `README.md` und `README_de.md` harmonisiert.
  - **Vertragstests (`tests/test_i18n.py`):** 10 umfassende Contract-Tests für Sprachlisten, native Bezeichnungen, Fallback-Hierarchie, 100% Übersetzungsparität, Singleton-API, CLI-Gate und dreisprachige Dokumentationsparität implementiert.

### Geändert / Changed (2026-09-18)
- **Pfad B Marketing, Discoverability, Visual Architecture & 18-Punkte-Navigationsparität:**
  - **18-Punkte Quick Navigation & Reziproke Anker:** Symmetrische Harmonisierung von `README.md` und `README_de.md` mit dualen HTML-Ankern (`<a id="..."></a>`) über alle 18 Standardabschnitte unter vollständiger Erhaltung historischer Legacy-Anker.
  - **Zielgruppen-Personas & Discoverability:** Strukturierte Personas (`[PERSONA-01]` bis `[PERSONA-04]`) mit Kontext, Pain Points und Lösungsarchitektur sowie zweisprachigen High-Intent-Suchbegriffen.
  - **10-Dimensionen Vergleichsmatrix:** Strukturierte Gegenüberstellung mit 4 Alternativen (FreeFileSync, Robocopy / Rsync, Syncthing, Commercial Cloud SaaS) abgebildet auf die Governance-Invarianten `INV-LOCAL-01` bis `INV-SLA-10`.
  - **Duale Mermaid-Diagramme:** 5-schichtiges System-Architekturdiagramm (`flowchart TB`) und Sequenzdiagramm (`sequenceDiagram`) für den SQLite-WAL-Checkpoint- und Backup-Lebenszyklus mit strikter Fail-Closed-Verzweigung (`SQLITE_BUSY`).
  - **Drittanbieter-Lizenzinventar & Non-Elevation (`THIRD_PARTY_LICENSES.md`):** Vollständiges Markdown-SBOM mit SPDX-Matrix, LGPL-3.0/2.1 dynamischer Verlinkungsisolation, Zero-Copyleft-Bestätigung und unprivilegierter `RunAsInvoker`-Zertifizierung.
  - **Deutscher Rechtsbelehrungshinweis:** Aufnahme des Haftungsausschlusses gemäß § 521 BGB (Gefälligkeitsrecht) in `README_de.md`.
  - **Vertragstests (`tests/test_metadata.py`):** Erweiterte Contract-Tests für Navigationsparität, Personas, Vergleichsmatrix, Mermaid-Syntax und Lizenzinventar.

### Geändert / Changed (2026-09-16)
- **Pfad A Technische Hygiene, CI-Hardening & Contract-Test-Parität:**
  - **CI Workflow Hardening (`.github/workflows/`):** Concurrency-Gruppen mit `cancel-in-progress: true` und explizite `timeout-minutes` (15 Min für Tests und Smoke, 10 Min für Stale, 5 Min für Welcome) in `tests.yml`, `source-platform-smoke.yml`, `stale.yml` und `welcome.yml` eingezogen; Testausführung auf `python -m pytest -ra -v` standardisiert.
  - **PWA Web Companion Regression Fix:** Fehlenden SVG-Icon-Eintrag (`./icon.svg`, `type: "image/svg+xml"`) im Manifest (`web_companion/manifest.webmanifest`) ergänzt; 29/29 Node.js-PWA-Tests bestanden.
  - **Multi-Host Sync- & Lock-Defense (`.gitignore`):** Schutzregeln für kanonische Sperren (`LOCK`, `LOCK.*`, `*.lock`, `uv.lock`, `!package-lock.json`), Cloud-Sync-Konfliktkopien (`* (copy)*`, `* (Copy)*`, `* (Kopie)*`, `*conflicted copy*`, `*-WORKSTATION*`, `*-ASUS*`, `*-LAPTOP*`, `*-Mac Studio*`, `*.sync-temp-*`, `*.sync-conflict-*`, `*.orig`, `*.rej`) sowie Test-/Build-Caches (`.coverage.*`, `.hypothesis/`, `.turbo/`, `.nyc_output/`, `wheelhouse/`, `.wheel-smoke/`) implementiert.
  - **PEP 621 Standardisierung (`pyproject.toml`):** `[project.urls]` um `Parent Organization`, `Umbrella Ecosystem`, `LLM Ready` und `Marketing Log` erweitert; `[tool.pytest.ini_options]` addopts auf `-ra -v` standardisiert.
  - **Marketing & Governance Log (`MARKETING-LOG.txt`):** Vollständiges Register mit Executive Value Proposition, 4 Ziel-Personas, EN/DE High-Intent-Suchbegriffen, Wettbewerbsmatrix, 10 Governance-Invarianten (`INV-LOCAL-01` bis `INV-SLA-10`), Ökosystem-Synergien und Pfad-A-Audit protokolliert.
  - **Vertragstests & Dokumentation (`tests/test_metadata.py`, `README.md`, `README_de.md`, `llms.txt`):** 4 neue Contract-Tests (`test_ci_concurrency_and_timeout_guardrails`, `test_gitignore_multihost_and_lock_defense`, `test_marketing_log_recent_hygiene_entry`, `test_web_companion_pwa_svg_parity`) implementiert; Suite auf 124 Python- und 29 Node-Tests (153 Gesamt-Tests) erweitert und dokumentiert.

### Hinzugefügt / Added (2026-09-13)
- **App Icon Generator, Multi-Resolution Icon Suite & Asset Parity Check:**
  - Authentische 1024x1024 Master-PNGs (`icon.png`, `DesktopIcon.png`, `ProSync.png`, `assets/icon.png`, `assets/DesktopIcon.png`, `assets/ProSync.png`, `mobile_icons/icon.png`) generiert.
  - Vollwertige 7-Layer Windows ICOs (16x16, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256 px @ 32bpp RGBA) für `ICO.ico`, `ProSync.ico`, `DesktopIcon.ico`, `icon.ico`, `assets/icon.ico`, `assets/app_icon.ico`, `assets/prosync.ico`, `assets/DesktopIcon.ico` sowie 4-Layer Favicon-ICOs (16, 24, 32, 48 px) für `favicon.ico`, `assets/favicon.ico`, `mobile_icons/favicon.ico` bereitgestellt.
  - Mobile & PWA Icon Suite unter `mobile_icons/` (`icon-192.png`, `icon-512.png`, `icon-maskable-192.png`, `icon-maskable-512.png`, `apple-touch-icon.png`, `apple-touch-icon-180.png`, `favicon.png`, `favicon.ico`, `manifest.json`, `icons/` Unterordner) standardkonform aufgebaut.
  - Laufzeit-Code-Integration: `load_app_icon()` und `get_app_icon()` mit Multi-Pfad-Fallback in `ProSyncStart_V3.1.py` implementiert; verdrahtet in `MainWindow.__init__()`, `setup_tray_icon()` und `main()`.
  - Automatisierte Asset-Vertragstestsuite `tests/test_assets_and_icons.py` (5 Contract-Tests) implementiert und in `run_tests.py` aufgenommen; 100% grün über alle 21 Testsuiten (119 Unit- & Contract-Tests).

### Geändert / Changed (2026-09-12)
- **GitHub Sync, Document Preview Fallback & Test Parity Check:**
  - `ProSyncReader.py`: Modernes `pypdf` als primären PDF-Reader für Dokument-Vorschauen integriert mit defensivem Fallback auf `PyPDF2` und `None`-Absicherung bei fehlender Bibliothek.
  - Regressionstest `TestPdfReaderFallback` in `tests/test_bug_regressions.py` implementiert; `tests/test_bug_regressions.py` in `run_tests.py` aufgenommen (jetzt 20 Testsuiten).
  - `.gitignore` um Multi-Host- (`*-WORKSTATION-LG.md`) und Cloud-Konfliktmuster (`* (kopie)*`, `* (konflikt)*`, `* (sync-conflict)*`, `* - Kopie.*`) gehärtet.
  - `README.md`, `README_de.md` und `llms.txt` auf 133 bestandene Tests (104 Python + 29 Node.js) sowie `tests/test_metadata.py` auf `Last-checked: 2026-09-12` synchronisiert.

### Hinzugefügt / Added (2026-08-22)
- **Discoverability, Visual Showcase, Sequence Diagram, Security Policy & Metadata Parity Check:**
  - Zweisprachige `SECURITY.md` mit Local-First- und Zero-Egress-Garantien (100% Offline-Betrieb, 0 Telemetrie), unprivilegiertem User-Mode (Non-Elevation), SQLite-WAL-Datenbankschutz-Invarianten (`PRAGMA wal_checkpoint(TRUNCATE)`), Pfad- & Geheimnishygienen sowie direkten Sicherheitskontaktadressen (`security@file-bricks.org`, `security@ellmos.ai`, `support@lukasgeiger.com`, `lukas@open-bricks.org`) und GitHub Security Advisories Link implementiert.
  - Interaktives zweisprachiges Mermaid-Sequenzdiagramm für den End-to-End Backup- & SQLite-WAL-Checkpoint-Lebenszyklus (Trigger -> Checkpoint-Validierung -> Safe-Copy vs. SQLITE_BUSY Abbruch -> Status-Update -> PWA-Export) in `README.md` & `README_de.md` integriert.
  - Visual Showcase & UI-Galerie mit Store-Screenshot-Assets (`screenshots/store/main-overview.png`, `database-backup.png`, `portable-profile.png`) und detaillierten Bildunterschriften eingebunden.
  - Shields.io Badges in `README.md` & `README_de.md` um CI-Status, Python (3.10 | 3.11 | 3.12), Plattformen (Windows | Linux | macOS), Testbadge (128 passed), Datenschutz (100% Local / Zero-Egress), Sicherheit (Local-First / WAL-Protected), Ökosystem (`file-bricks`), Dachorganisation (`open-bricks`), LLM-Kontext (`llms.txt`) und strukturierte Schnellnavigation synchronisiert.
  - Geschwisterwerkzeuge-Matrix auf 13 Partner-Repositories über 5 Organisationen (`file-bricks`, `doc-bricks`, `ellmos-ai`, `dev-bricks`, `open-bricks`) erweitert.
  - `pyproject.toml` um `Security`-URL in `[project.urls]` sowie POSIX Linux, MacOS und OS Independent Classifiers erweitert.
  - Automatisierte Metadaten-, Manifest-, CI-Matrix-, Sicherheits- und Paritätstestsuite `tests/test_metadata.py` (8 Contract-Tests) implementiert und in `run_tests.py` integriert.
  - `llms.txt` Last-checked Zeitstempel auf `2026-08-22`, Sicherheitsrichtlinie, aktualisierte Prüfbefehle und 128 verifizierte Tests (99 Python + 29 Node.js) synchronisiert.
  - Pytest-Gesamtsuite auf 99/99 Tests (Gesamt 128 verifizierte Tests: 99 Python + 29 Node.js) erweitert (100% grün).

### Hinzugefügt / Added (2026-08-21)
- **Windows Store Readiness, Packaging & Asset Parity Check (Microsoft Store Policy 10.1.3):**
  - Kanonisches Desktop-Bridge-AppxManifest `store_package/ProSync/AppxManifest.xml` mit Identity `Geiger.ProSync`, Publisher `CN=52596601-BAB4-4F3F-B182-E8F3F273B202`, Version `3.2.0.0`, `runFullTrust`, `TargetDeviceFamily Windows.Desktop` und Tile-Deklarationen implementiert.
  - Vollständiges Kachel- und Icon-Asset-Set (`icon_44x44.png`, `icon_50x50.png`, `icon_150x150.png`, `icon_310x150.png`, `icon_310x310.png`, `Square*Logo.png`, `Wide310x150Logo.png`) generiert und über alle 3 Standardstandorte (`store_assets/`, `assets/icons/`, `store_package/ProSync/icons/`) synchronisiert.
  - Microsoft Store Policy 10.1.3 Compliance für Schlüsselwörter hergestellt: Streng auf maximal 7 hochrelevante Suchbegriffe in Deutsch und Englisch in `STORE_LISTING.md`, `releases/windowsstore/store_listing_*.md` und `releases/windowsstore/store_settings.json` gehärtet.
  - Vorbereitungs- und Zertifizierungsleitfaden `WINDOWS_STORE_PREP.md` mit Offline-First-Garantien, WACK-Zertifizierungsschritten und Partner-Center-Metadaten erstellt.
  - Automatisierter 5-Stufen-Auditor `scripts/check_store_readiness.py` zur Verifikation von Store-Paketen, Manifesten, Pflichtdokumenten und Kacheln implementiert.
  - Vertragstestsuite `tests/test_store_materials.py` (11 Tests) für Store-Metadaten, XML-Manifest, Bilddimensionen, Richtlinienkonformität und Umlaut-Integrität implementiert.
  - Pytest-Gesamtsuite auf 91/91 Tests (Gesamt 120 verifizierte Tests: 91 Python + 29 Node.js) erweitert.

- **Cross-Platform macOS & Linux Smoke Suites (8-Punkte-Standard):**
  - Dedizierte Testsuite `tests/macos_platform_smoke.py` mit 8 Prüfpunkten für macOS/Darwin (System-Öffner `open`, Offscreen PySide6 `MainWindow` & Tray-Lifecycle, POSIX `~/.config/ProSync/reports` Pfadauflösung, Sibling-Launcher ohne Windows-`creationflags`, redigierter `prosync-profile-v1.json` Export ohne Pfad-Leaks, APFS/HFS+ Unicode-NFC- und Case-Folding-Regeln, TranslationSystem Sprachumschaltung und SQLite WAL-Checkpointing).
  - Dedizierte Testsuite `tests/linux_platform_smoke.py` mit 8 Prüfpunkten für Linux (System-Öffner `xdg-open`, Offscreen PySide6 UI, XDG App-Pfade, Sibling Launcher, redigierter Export, ext4/btrfs Case-Regeln, TranslationSystem, SQLite WAL Checkpoint).
  - Vertragstestsuite `tests/test_platform_smoke_contract.py` integriert beide Suiten nahtlos in die Pytest-Vollsuite (erhöht auf 83 Tests).
  - Standalone-Runner `source_platform_smoke.py` modularisiert und `run_tests.py` auf 18 Testdateien erweitert.
  - CI-Workflow `.github/workflows/source-platform-smoke.yml` mit dedizierten Schritten für `ubuntu-latest` und `macos-latest` aktualisiert.
  - Gesamtzahl verifizierter Tests auf 112/112 (83 Pytest + 29 Node.js) erhöht.
### Geändert / Changed (2026-08-11)
- **UX- & Barrierefreiheits-Review:** `ProSyncStart_V3.1.py` und `ProSyncReader.py` mit umfassenden Screenreader-Attributen (`AccessibleName`, `AccessibleDescription`, `ToolTip`, `StatusTip`) für Hauptfenster-Buttons (`➕ Neue Aufgabe`, `🛡️ Sicherheitsprüfung`, `📚 ProFiler öffnen`, `⇄ Profil austauschen`, `🔍 Datenbank durchsuchen`, `▶ Start Sync`, `⏸ Pause`, `⏹ Stop`), Aufgabenliste (`Synchronisations-Aufgaben`), Suchdialoge und Suchergebnis-Listen ausgestattet. Statusleiste (`status_bar`) mit dynamischem accessible Indikator (`lbl_status_summary`: Aufgaben- und Auto-Sync-Anzahl) und Tastatur-Shortcuts (`Strg+N`, `Strg+Shift+A`, `Strg+F`, `F5`) nachgerüstet. Echte deutsche Umlaute verifiziert. Pytest-Suite (82/82 passed, 100% grün) inklusive neuem Regressionstest `test_main_window_controls_and_indicators_expose_accessible_context` bestanden.

### Geändert / Changed (2026-08-01)
- **GitHub Privacy & Metadata Check:** konkrete lokale Beispiel- und Store-Pfade
  durch portable Platzhalter ersetzt; die Testfixture nutzt jetzt
  `C:\\Users\\Example`. `pyproject.toml` übernimmt den dokumentierten Python-Mindeststand
  3.10. `README.md`, `README_de.md` und `llms.txt` dokumentieren die aktuelle
  Verifikation mit 110/110 bestandenen Tests.

### Geändert / Changed (2026-07-30)
- **Technische Hygiene & Maintenance Check:** `llms.txt` Header & Footer auf `Last-checked: 2026-07-30` und 110/110 Tests (81 pytest + 29 node:test) aktualisiert. Test-Status-Badges in `README.md` und `README_de.md` auf 110 passed nachgeführt. Test-Suite (81 Pytest + 29 Node) und compileall 100% grün.

### Hinzugefügt / Added (2026-07-29, TW-PS-09 Phase 2)
- Täglicher, IANA-zeitzonenbasierter Autosync-Modus mit persistierten
  `daily_time`- und `timezone`-Feldern pro Verbindung.
- Kontextmenü für die tägliche Uhrzeit; ungültige `HH:MM`-Werte und unbekannte
  IANA-Zeitzonen werden vor dem Speichern abgewiesen.
- Einmalige tägliche `QTimer`-Ausführung mit Neuplanung nach Trigger und nach
  dem Wiederaktivieren der Anwendung; kein Catch-up-Sync nach Standby.
- Regressionen für Schema-Persistenz, One-shot-Timer und Neuplanung ergänzt.

### Hinzugefügt / Added (2026-07-27, TW-PS-09 Phase 1)
- Reine, IANA-zeitzonenbewusste Berechnung des nächsten täglichen
  Ausführungszeitpunkts mit explizitem Vertrag für Sommerzeit-Sprung und
  doppelte Herbststunde.
- Regressionstests für Mitternacht, bereits verstrichene Uhrzeiten,
  nicht existierende lokale Zeiten und die wiederholte Stunde.
- `tzdata` als Windows-Laufzeitabhängigkeit für die IANA-Zeitzonendaten
  deklariert.
- Testnachweis und öffentliche Zählung auf 77/77 Python- plus 29/29
  Web-Companion-Tests (106/106 insgesamt) aktualisiert.

### Geändert / Changed (2026-07-27)
- **Technische Hygiene & Doku-Korrekturen:** HTML-Banner-Syntax in `README.md` und `README_de.md` korrigiert (`<img ...>`). `llms.txt` Header auf `Last-checked: 2026-07-27` aktualisiert. `.gitignore` um lokale Generator-Artefakte ergänzt. 97/97 grüne Tests (68 Pytest + 29 Web-Companion Node.js Tests) vollständig re-verifiziert.

### Geändert / Changed (2026-07-26)
- **Technische Hygiene & Metadata-Update:** Standarisierte PEP 621 `pyproject.toml` mit Projekt-Metadaten, PySide6/paramiko/pypdf Abhängigkeiten und `[tool.pytest.ini_options]` Test-Konfiguration erstellt. `llms.txt` Header auf `Last-checked: 2026-07-26` aktualisiert und 97/97 grüne Tests (68 Pytest + 29 Web-Companion Node.js Tests) verifiziert.

### Dokumentiert / Documented (2026-07-24)
- **Repository Discoverability & Marketing Update:** README.md und README_de.md um Test-Statusbadge (97 Tests grün), Disambiguation-Sektion (Abgrenzung zu Enterprise-CDC/Tibero ProSync) und Mermaid-Systemarchitekturdiagramm erweitert. `llms.txt` auf Datum `2026-07-24` und erweiterte Suchphrasen für offline/local-first PySide6 Backup-Synchronisation und SQLite WAL-Schutz aktualisiert.

### Behoben / Fixed (2026-07-22)
- Ordner-`mirror` bricht bei fehlenden oder nicht lesbaren Quellen fail-closed ab; Kopier-/Löschfehler erzeugen keinen Erfolgsreport mehr.
- Überlappende oder identische Quell-/Zielordner werden vor dem Scan abgelehnt, damit kein Sync rekursiv in seinen eigenen Arbeitsbaum schreibt.
- Ordner-`one_way` überträgt neue und geänderte Quelldateien wie `update`, löscht aber keine reinen Zieldateien.
- Datei-Syncs mit aktiviertem SQLite-WAL-Checkpoint kopieren nur nach erfolgreichem Checkpoint.
- SFTP-Uploads ersetzen Dateien atomar via `posix_rename` oder über einen rückrollbaren Fallback und räumen fehlgeschlagene Temporärdateien auf.
- Beschädigte oder schemawidrige Konfigurationen bleiben unverändert, werden gesichert und blockieren das Laden statt still überschrieben zu werden.
- Extrem große Autosync-Intervalle werden auf den sicheren `QTimer`-Maximalwert begrenzt.
- Python-Support und CI sind auf 3.10 bis 3.12 vereinheitlicht; CI führt zusätzlich die vollständige Pytest-Suite aus.

### Behoben / Fixed (2026-07-11)
- `paramiko` ist jetzt als SFTP-/SSH-Abhängigkeit in `requirements.txt` deklariert, damit `test_sftp_target.py` im CI-Smoke nicht mehr an einem fehlenden optionalen Paket scheitert.

### Dokumentiert / Documented (2026-07-02, Mobile smoke)
- `web_companion/MOBILE_SMOKE.md` dokumentiert den lokal ausgeführten Mobile-Viewport-Smoke gegen `http://127.0.0.1:4179/` mit Demo-Import, Offline-Restore nach Reload, Filter `Autosync -> Aktiv`, Suche `ledger` und konsolenfreiem Lauf bei `390x844`.
- `AUFGABEN.txt` und `PORTIERUNGSPLAN.md` unterscheiden jetzt sauber zwischen lokal verifiziertem Mobile-Viewport-Smoke und weiter offenem echten Android-/iOS-Geräte- oder Emulator-Smoke.

### Behoben / Fixed (2026-07-02, PWA smoke follow-up)
- `web_companion/manifest.webmanifest` führt `./icon.svg` wieder im `icons`-Array. Damit stimmen Manifest und bestehende PWA-Regressions-Tests wieder überein; SVG bleibt als installierbares Vektor-Icon neben den PNG- und maskable-Icons erhalten.

### Hinzugefügt / Added (2026-06-28, PWA-Feature sortConnections)
- **web_companion: Verbindungs-Sortierung** — `sortConnections(connections, sortBy)` in `library.js` als reine Logikfunktion (immutable, DOM-frei). Unterstützt `name-asc`, `name-desc`, `autosync-first` und `type`. In `app.js` und `index.html` als Sort-Dropdown im Filter-Panel verdrahtet; wird bei jedem Filter-Event und nach `clearStoredProfile` zurückgesetzt.
- 6 neue Unit-Tests für `sortConnections` in `web_companion/tests/library.test.mjs`.
- Manifest-Fix: `icon.svg` ins `icons`-Array aufgenommen, `purpose: "any"` bei Icon-192 und Icon-512 ergänzt — repariert 4 pre-existierende Bugsweep-13-Regressionen.

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
