# ProSync

Intelligente Backup-Synchronisation mit Datenbankschutz.

> [English Documentation](README.md)

## Features

- **Ordner-Synchronisation** (einseitig / beidseitig)
- **Datei-Synchronisation** für einzelne Dateien
- **Automatische Datenbank-Erkennung** und Schutz
- **WAL Checkpoint** für SQLite-Dateien vor dem Kopieren
- **System Tray Integration** für Hintergrundbetrieb
- **Geplante Backups** mit konfigurierbaren Intervallen
- **Batch-Sync** für mehrere ausgewählte Verbindungen in einem Lauf
- **Datenbank-Indexierung** für Suche und Versionierung (optional)
- **ProFiler-Companion** — optionaler Start von ProFiler aus dem Hauptfenster

## Screenshots

![Hauptfenster](screenshots/main.png)

## Installation

```bash
pip install -r requirements.txt
```

### Erforderliche Pakete

- PySide6
- (Optional) PyPDF2 für PDF-Vorschau im Reader
- (Optional) python-docx für Word-Vorschau im Reader

## Verwendung

### Via Python

```bash
python ProSyncStart_V3.1.py
```

### Via Batch-Datei

```bash
START.bat
```

Die Anwendung startet im System Tray. Rechtsklick auf das Icon für Optionen.

## Windows-Build

Für einen reproduzierbaren lokalen Windows-Build steht `build_exe.bat` bereit.
Das Skript erzeugt `dist/ProSync/ProSync.exe` und kopiert `ProSyncReader.exe`
in denselben Ausgabeordner, damit die Suchoberfläche auch im Frozen-Modus
weiterhin separat gestartet werden kann.
Build-Artefakte in `build/`, `dist/` und `releases/` werden bewusst nicht versioniert.

## Qualitätssicherung

```bash
python -m compileall -q ProSyncStart_V3.1.py ProSyncReader.py prosync_utils.py logger.py run_tests.py _WARTUNG/generate_store_screenshots.py test_batch_sync_queue.py test_config_manager.py test_database_safety.py test_import_streams.py source_platform_smoke.py test_portable_profile.py test_store_materials.py test_sync_worker.py
python run_tests.py
```

GitHub Actions führt dieselben Smoke-Tests für Python 3.10, 3.11 und 3.12 aus.

### Linux-Quell-Smoke

Der zusätzliche Smoke `source_platform_smoke.py` prüft den Linux- und macOS-Pfad der
Desktop-App reproduzierbar:

- `xdg-open` für Datei- und Ordneröffnen
- redigierten UTF-8-Export `prosync-profile-v1.json` mit Report-Metadaten
- headless PySide6-Start mit Tray-Initialisierung
- Linux-Launch ohne Windows-spezifische `creationflags`

Der Lauf ist absichtlich read-only und startet keinen echten Sync gegen lokale
Produktivordner.

## Datenschutz und lokale Dateien

`ProSync_config.json`, Logs, Build-Artefakte und lokale Host-Notizen bleiben außerhalb des Repositories. Die getrackte Datei `ProSync_config.example.json` enthält nur eine leere Beispielstruktur und keine persönlichen Quell- oder Zielpfade.

Für GitHub werden nur Quellcode, Tests, Beispielkonfiguration und Projektdokumentation versioniert. Persönliche Sync-Ziele, Datenbanken, WAL-Dateien, temporäre Locks und lokale Build-Ausgaben sind über `.gitignore` ausgeschlossen.

Sicherheitslücken bitte nicht als öffentliches Issue melden, sondern über GitHubs private Vulnerability-Reporting-Funktion im Tab **Security**.

## Batch-Ausführung

Wähle mehrere Aufgaben mit `Ctrl` oder `Shift` in der Liste aus und starte sie gesammelt mit
`▶ Batch starten` oder per Kontextmenü. ProSync arbeitet die Auswahl nacheinander ab,
doppelte IDs werden ignoriert und der Batch wird bei Fehlern oder manuellem Stop kontrolliert beendet.

## Synchronisationsmodi

| Modus | Beschreibung | Anwendungsfall |
|-------|-------------|----------------|
| **mirror** | Ziel = exakte Kopie der Quelle | Vollständiges Backup |
| **update** | Nur neuere Dateien übertragen | Inkrementelles Backup |
| **two_way** | Bidirektionale Synchronisation | Sync zwischen zwei Rechnern |
| **one_way** | Quelle → Ziel, keine Löschungen | Sichere Archivierung |
| **index_only** | Nur Indexierung, kein Kopieren | Dateiverwaltung ohne Sync |

## Beispielszenarien

### 1. Projektordner-Backup

**Aufgabe:** Tägliches Backup eines Entwicklungsprojekts

**Konfiguration:**
- **Quelle:** `C:\Projekte\MeinProjekt`
- **Ziel:** `D:\Backups\MeinProjekt`
- **Modus:** `mirror`
- **Geplant:** Täglich um 18:00 Uhr
- **Indexierung:** Aktiviert (für Suche)

**Ergebnis:** Vollständiges Backup mit Dateiversionierung und Suchfunktion

### 2. Synchronisation zwischen Laptop und Desktop

**Aufgabe:** Dateien zwischen zwei PCs synchronisieren

**Konfiguration:**
- **Quelle:** `C:\Dokumente`
- **Ziel:** `\\Desktop-PC\Dokumente`
- **Modus:** `two_way`
- **Geplant:** Alle 30 Minuten
- **Konfliktlösung:** `newest` (neueste Datei gewinnt)

**Ergebnis:** Bidirektionaler Sync, beide PCs haben immer die aktuellen Dateien

### 3. Datenbank-Backup (SQLite mit WAL-Modus)

**Aufgabe:** Sicheres Backup einer SQLite-Datenbank

**Konfiguration:**
- **Typ:** Datei-Verbindung (nicht Ordner!)
- **Quelle:** `C:\App\data.db`
- **Ziel:** `D:\Backups\data.db`
- **Modus:** `one_way`
- **WAL Checkpoint:** Aktiviert
- **Geplant:** Alle 4 Stunden

**Ergebnis:** Konsistente DB-Backups ohne Korruption

## Datenbankschutz (V3.2)

ProSync erkennt kritische Datenbanken automatisch und wendet sichere Einstellungen an:

### Unterstützte Datenbanktypen

- **SQLite** (.sqlite, .sqlite3, .db, .db3)
- **MS Access** (.mdb, .accdb)

### Automatische Sicherheitsmaßnahmen

#### Für Ordner-Verbindungen:

- Kritische DBs (im WAL-Modus) werden **automatisch ausgeschlossen**
- WAL-Dateien (.db-wal, .db-shm, .db-journal) werden **nie kopiert**
- Empfehlung: **Datei-Verbindungen** für einzelne DBs erstellen

#### Für Datei-Verbindungen:

- **WAL Checkpoint** wird automatisch aktiviert
- **Einweg-Modus** wird empfohlen
- Checkpoint vor jeder Kopieroperation

### Was ist ein WAL Checkpoint?

WAL (Write-Ahead Logging) speichert SQLite-Änderungen in einer separaten `-wal`-Datei.
Ein Checkpoint führt diese Änderungen in die Haupt-DB-Datei zurück.

**Ohne Checkpoint:** Inkonsistente Backups möglich.
**Mit Checkpoint:** Konsistente DB-Kopie intendiert (abhängig von SQLite-Checkpoint-Implementierung, keine Gewähr).

## Konfigurationsdatei

`ProSync_config.json` — Wird lokal automatisch erstellt und verwaltet. Die Datei ist ignoriert, weil sie persönliche Quell-/Zielpfade enthalten kann.
Ein sicheres Beispiel liegt in `ProSync_config.example.json`.

### Beispiel (Ordner-Verbindung):

```json
{
  "connections": [
    {
      "id": "conn-abc123",
      "name": "Projekt Backup",
      "type": "folder",
      "source": "C:\\Projekte\\MeinProjekt",
      "target": "D:\\Backups\\MeinProjekt",
      "mode": "mirror",
      "conflict_policy": "source",
      "indexing": true,
      "db_path": "C:\\Projekte\\MeinProjekt\\profiler_index.db",
      "exclude_patterns": ["*.tmp", "*.lock", "__pycache__"],
      "autosync": {
        "enabled": true,
        "interval_minutes": 60
      }
    }
  ]
}
```

### Beispiel (Datei-Verbindung):

```json
{
  "connections": [
    {
      "id": "conn-def456",
      "name": "Datenbank Backup",
      "type": "file",
      "source_file": "C:\\App\\data.db",
      "target_file": "D:\\Backups\\data.db",
      "mode": "one_way",
      "checkpoint_before_sync": true,
      "autosync": {
        "enabled": true,
        "interval_minutes": 240
      }
    }
  ]
}
```

## ProSyncReader

Ein separates Tool zur Suche in den Sync-Datenbanken.

```bash
python ProSyncReader.py
```

**Features:**
- Volltextsuche in synchronisierten Dateien
- Tag-basierte Suche
- Datei-Vorschau (PDF, DOCX)
- Direktes Öffnen von Dateien/Ordnern

## ProFiler-Companion

ProSync kann ProFiler direkt aus dem Hauptfenster starten. Die Suche prüft
zuerst `app.profiler_path` in `ProSync_config.json`, danach lokale Standardpfade
und zuletzt den gemeinsamen Software-Baum `REL-PUB_ProFiler`. Konfigurierte
Pfade dürfen absolut, relativ zum ProSync-Ordner oder über Umgebungsvariablen
wie `%USERPROFILE%\\...` angegeben werden.

## Tipps & Best Practices

### Empfohlen:

- **Datei-Verbindungen** für einzelne Datenbanken verwenden
- **WAL Checkpoint** für SQLite-DBs aktivieren
- Neue Verbindungen zuerst mit einem **manuellen Sync** testen
- **exclude_patterns** für temporäre Dateien verwenden

### Vermeiden:

- **two_way** für kritische Datenbanken
- **Laufende** Anwendungen synchronisieren
- **.db-wal**-Dateien manuell kopieren
- **mirror** verwenden, wenn keine Löschungen gewünscht sind

## Fehlerbehebung

### „Checkpoint failed"

Datenbank ist gerade geöffnet/gesperrt. Anwendung schließen oder Timeout erhöhen.

### „Sync hängt"

Große Dateien oder langsame Netzwerkverbindung. `update` statt `mirror` für schnellere Syncs verwenden.

### „Datei wurde ausgeschlossen"

`exclude_patterns` in der Konfiguration prüfen. Kritische DBs werden automatisch ausgeschlossen (bei Ordner-Verbindungen).

## System Tray Befehle

- **Linksklick:** Hauptfenster öffnen
- **Rechtsklick → Ausführen:** Verbindung manuell starten
- **Rechtsklick → Auto-Ausführung:** Geplanten Sync aktivieren
- **Rechtsklick → Beenden:** ProSync beenden

## Austauschformat `prosync-profile-v1.json`

ProSync kann Verbindungen über **`⇄ Profil austauschen`** als redigiertes JSON
exportieren und wieder importieren. Das Austauschformat ist für Web/PWA- oder
Geräte-Companions gedacht und enthält deshalb bewusst **keine** echten lokalen
Pfadwerte, keine Secrets und keinen `app.profiler_path`.

- Exportiert werden Name, Typ, Modus, Autosync-Takt, Ausschlussmuster, Sicherheitszusammenfassungen und redigierte Pfad-Hinweise wie `Alpha` oder `data.db`.
- Importierte Profile landen als lokale Entwürfe mit leerer Quelle/Ziel-Pfadzuordnung und deaktiviertem Autosync.
- Vor dem ersten Sync müssen Quell- und Zielpfade deshalb im Desktop-Client neu gewählt werden.

Details stehen in `EXPORTFORMAT.md`.

## Lizenz

MIT — Siehe [LICENSE](LICENSE)

Dieses Projekt verwendet PySide6 (LGPL).

---

**Version:** 3.2
**Autor:** Lukas Geiger
**Zuletzt aktualisiert:** Juni 2026

---

## Haftung

Dieses Projekt ist eine **unentgeltliche Open-Source-Schenkung** im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gelten die Haftungsausschlüsse aus der MIT-Lizenz.

Nutzung auf eigenes Risiko. Keine Wartungszusage, keine Verfügbarkeitsgarantie, keine Gewähr für Fehlerfreiheit oder Eignung für einen bestimmten Zweck.
