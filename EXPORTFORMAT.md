# Exportformat: `prosync-profile-v1.json`

Stand: 2026-05-26

## Zweck

`prosync-profile-v1.json` ist das redigierte Austauschformat zwischen dem
lokalen ProSync-Desktop und späteren Companion-Linien wie Web/PWA,
Android/iOS-PWA oder anderen Desktop-Instanzen. Das Format beschreibt
Verbindungen so weit, dass Struktur, Modus und Takt verständlich bleiben,
ohne echte lokale Pfade oder private Systemdetails preiszugeben.

## Enthaltene Daten

- Schemakennung, Exportzeit und ProSync-Version
- App-Einstellung `notifications_enabled`
- Verbindungsmetadaten:
  - `id`, `name`, `type`, `mode`
  - `exclude_patterns`
  - `autosync.enabled` und `autosync.interval_minutes`
  - bei Ordner-Verbindungen zusätzlich `conflict_policy` und `indexing`
  - bei Datei-Verbindungen zusätzlich `checkpoint_before_sync`
- redigierte Pfad-Hinweise:
  - `source_label`
  - `target_label`
  - optional `db_label`
- redigierte Sicherheitszusammenfassungen
- optionale Report-Metadaten aus `sync_log.json` ohne Dateipfade

## Bewusst ausgeschlossene Daten

- echte lokale Quell-, Ziel- und Datenbankpfade
- `app.profiler_path`
- Zugangsdaten, Tokens, Secrets oder Passwörter
- lokale Laufzeitmarker wie `_reason`, temporäre Locks oder Build-Artefakte

## Beispiel

```json
{
  "schema": "prosync-profile-v1",
  "exported_at": "2026-05-26T14:10:00+00:00",
  "exported_from": {
    "app": "ProSync",
    "version": "3.2"
  },
  "app": {
    "notifications_enabled": true
  },
  "connections": [
    {
      "id": "folder-1",
      "name": "Projekt Backup",
      "type": "folder",
      "mode": "mirror",
      "exclude_patterns": [
        "*.tmp",
        "__pycache__"
      ],
      "autosync": {
        "enabled": true,
        "interval_minutes": 60
      },
      "path_hints": {
        "source_label": "Alpha",
        "target_label": "Alpha",
        "db_label": "index.db"
      },
      "conflict_policy": "source",
      "indexing": true,
      "safety_summary": {
        "kind": "folder",
        "databases_found": 2,
        "critical_databases": 1,
        "excluded_databases": 1,
        "total_db_size_mb": 12.5
      }
    }
  ],
  "reports": {
    "count": 1,
    "latest": {
      "connection": "Projekt Backup",
      "connection_id": "folder-1",
      "mode": "mirror",
      "started_at": "2026-05-26T10:00:00+00:00",
      "duration_seconds": 4.5,
      "files_copied": 12,
      "files_deleted": 1,
      "files_skipped": 3,
      "bytes_copied": 2048,
      "total_actions": 16
    }
  }
}
```

## Importverhalten

- Importierte Profile werden **nicht** mit echten Pfaden rekonstruiert.
- Quelle, Ziel und optionale Indexdatenbank bleiben leer.
- Autosync wird beim Import deaktiviert.
- ProSync markiert solche Einträge intern als `requires_mapping`.
- Vor dem ersten Sync müssen Quelle und Ziel im Desktop-Dialog neu gewählt
  werden.

## Stabilitätsregel

Solange die Schemakennung `prosync-profile-v1` gleich bleibt, dürfen neue
optionale Felder ergänzt werden. Bestehende Felder dürfen aber nicht
umgedeutet oder semantisch gebrochen werden.
