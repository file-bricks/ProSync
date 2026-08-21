# Windows Store Preparation & Packaging Guide — ProSync

Stand: 2026-08-21

## Übersicht

ProSync wird als modernes MSIX-Paket für den Microsoft Store paketiert. Das Paket kapselt die lokale PySide6-Desktop-Anwendung in einer sicheren, offline-fähigen Windows-Desktop-Container-Umgebung.

## Metadaten & Identität

- **Publisher:** CN=52596601-BAB4-4F3F-B182-E8F3F273B202
- **Publisher Display:** Geiger
- **Identity Name:** Geiger.ProSync
- **Package Version:** 3.2.0.0
- **Category:** Utilities
- **Capabilities:** runFullTrust, internetClient
- **Languages:** de-DE, en-US
- **Executable:** ProSync.exe

## Erledigte Vorbereitungsschritte

1. **Paketierungs-Metadaten (store_package.json):**
   - Vollständige Publisher-DN, Identity-Name und Versionsangabe (`3.2.0.0`) konfiguriert.
   - Validierte HTTPS-URLs für Datenschutzrichtlinie und GitHub-Issue-Support hinterlegt.

2. **Windows Desktop AppxManifest (store_package/ProSync/AppxManifest.xml):**
   - Kanonisches AppxManifest mit `TargetDeviceFamily Windows.Desktop` (MinVersion `10.0.17763.0`, MaxVersionTested `10.0.26100.0`).
   - Mehrsprachige Ressourcen (`de-de`, `en-us`) und Tile-Deklarationen eingebunden.

3. **MSIX Tile- und Icon-Assets:**
   - Vollständiges Set an Kachel- und Logo-Assets:
     - `icon_44x44.png` (Square44x44Logo / Square71x71Logo)
     - `icon_50x50.png` (Square50x50Logo / StoreLogo)
     - `icon_150x150.png` (Square150x150Logo)
     - `icon_310x150.png` (Wide310x150Logo)
     - `icon_310x310.png` (Square310x310Logo)
   - Synchron gehalten in `assets/icons/`, `store_package/ProSync/icons/` und `store_assets/`.

4. **Store Screenshots:**
   - Drei hochauflösende Screenshots unter `screenshots/store/`, `README/screenshots/store/` und `releases/windowsstore/screenshots/`:
     - `main-overview.png`: Hauptübersicht mit mehreren lokalen Sync-Aufgaben
     - `database-backup.png`: Datei-Backup mit SQLite-Schutz und WAL-Checkpoint
     - `portable-profile.png`: Importiertes Austauschprofil mit Hinweisen zur Pfad-Neu-Zuordnung

5. **Bilingualer Store-Listing-Entwurf (STORE_LISTING.md):**
   - Vollständige deutsche und englische Beschreibungen mit Feature-Listen.
   - Strikt maximal 7 Suchbegriffe pro Sprache gemäß **Microsoft Store Policy 10.1.3** ohne Fremdmarkenverletzungen.

6. **Automatisiertes Readiness-Audit (scripts/check_store_readiness.py):**
   - Automatisierte Validierung aller Manifeste, Metadaten, Icons, Screenshots und Lizenzdokumente.
   - Getestet über Pytest in `tests/test_store_materials.py`.

## Vor der Einreichung im Partner Center (externe Gates)

- **Partner Center Reservierung:** Identität `Geiger.ProSync` und Anzeigename `ProSync` im Microsoft Partner Center bestätigen.
- **MSIX-Erstellung & Signierung:** Produktions-MSIX im Packaging-Workflow erstellen und mit Entwicklerzertifikat signieren.
- **WACK-Zertifizierungstest:** Windows App Certification Kit mit `OVERALL RESULT: PASS` durchlaufen.
- **Partner Center Upload:** Signiertes `.msix`-Paket, Listing-Texte und Screenshots übermitteln.

## Technische Hinweise

- **Lokale Datenhaltung:** ProSync speichert Konfiguration und Logdateien lokal unter `%APPDATA%\ProSync` bzw. im Anwendungsverzeichnis.
- **Datenbankschutz:** Sichere Behandlung von SQLite WAL- und SHM-Dateien vor Sync-Läufen.
- **Datenschutz:** 100% Offline-First, keine Telemetrie, kein Tracking.
