# SFTP-/SSH-Ziele in ProSync

ProSync unterstützt SFTP als Remote-Zieltyp für lokale Ordner. Der Zieltyp ist
für Mirror-/Backup-Flüsse zu einem per SSH erreichbaren Host gedacht, etwa einen
Mac im Tailscale-Netz. Er ersetzt kein lokales gemountetes Laufwerk, speichert
keine Passwörter und nutzt `paramiko` nur optional zur Laufzeit.

## Konfigurationsfelder

```json
{
  "id": "conn-mac-mirror",
  "name": "Mac Mirror",
  "type": "sftp",
  "source": "C:\\Users\\lukas\\Documents\\Projekt",
  "target": "/Users/lukas/Backups/Projekt",
  "remote_host": "macstudio.tailnet",
  "remote_port": 22,
  "remote_username": "lukas",
  "remote_key_file": "",
  "mode": "update",
  "exclude_patterns": ["*.tmp", "__pycache__"],
  "autosync": {
    "enabled": false,
    "interval_minutes": 30
  }
}
```

Unterstützte Modi:

- `update`: lädt neue und geänderte lokale Dateien hoch.
- `mirror`: lädt neue und geänderte lokale Dateien hoch und löscht entfernte
  Dateien, die lokal nicht mehr existieren.
- `one_way`: konservativer Upload wie `update`, ohne Remote-Löschungen.

## Sicherheitsgrenze

SFTP-Ziele sind nicht datenbanksicher: WAL-/Lock-Dateien und Remote-Atomizität
können nicht wie bei lokalen Datei-Verbindungen garantiert werden. Für SQLite-
oder Access-Dateien bleibt eine lokale Datei-Verbindung mit WAL-Checkpoint der
sichere Weg. Der SFTP-Zieltyp lehnt `checkpoint_before_sync` deshalb ab und
zeigt in GUI und Audit eine Warnung.

## Authentifizierung

ProSync speichert keine SSH-Passwörter. Nutze einen SSH-Agent, vorhandene
System-Host-Keys oder optional `remote_key_file`. Unbekannte Host-Keys werden
standardmäßig nicht automatisch akzeptiert; die GUI bietet dafür nur eine
bewusste Warn-Option.

## Portable Profile

`prosync-profile-v1.json` exportiert SFTP-Ziele redigiert. Remote-Host,
Remote-Pfad, Benutzername und Schlüsselpfad werden nicht übernommen; importierte
SFTP-Profile müssen lokal neu zugeordnet werden.
