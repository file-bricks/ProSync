# Security Policy / Sicherheitsrichtlinie

## Deutsch

### Sicherheitsphilosophie & Leitlinien

`file-bricks/ProSync` ist als rein lokale Desktop- und Hintergrundanwendung für Dateisynchronisation und SQLite-WAL-Datenbankschutz konzipiert. Sicherheit und Datenschutz basieren auf folgenden Kernprinzipien:

- **Local-First & Zero-Egress:** ProSync überträgt keinerlei Nutzdaten oder Telemetrie über das Netzwerk. Alle Synchronisationsoperationen verbleiben vollständig auf der lokalen Maschine bzw. den vom Nutzer explizit konfigurierten Zielen (lokale Platten, NAS-Freigaben, SFTP-Endpunkte).
- **Keine Cloud-Pflicht:** Es existieren keine Zwangsverbindungen zu Cloud-Diensten.
- **Unprivilegierter User-Mode (Non-Elevation):** ProSync benötigt und verlangt keine Administratorrechte. Alle Dateioperationen laufen streng im Benutzerkontext ab.
- **SQLite WAL-Konsistenzschutz:** Vor dem Kopieren von SQLite-Datenbanken führt ProSync ein `PRAGMA wal_checkpoint(TRUNCATE)` durch. Bei Sperren oder Fehlern bricht der Schutzmechanismus ab, um unvollständige oder inkonsistente Kopien zu verhindern.
- **Geheimnis- und Pfad-Hygiene:** Konfigurationsdateien mit realen Pfaden (`ProSync_config.json`), Logs und temporäre Arbeitsdateien werden niemals im Repository getrackt. Der Export für den Web-Companion (`prosync-profile-v1.json`) ist vollständig redigiert und enthält keine Pfade oder Anmeldedaten.

### Unterstützte Versionen

| Version | Unterstützt | Anmerkungen |
| ------- | ----------- | ----------- |
| 3.2.x   | Ja          | Aktuelle Hauptversion mit SQLite WAL Guard, Batch Queue & Store Readiness |
| < 3.2.0 | Eingeschränkt | Bitte auf die aktuelle Version aktualisieren |

### Sicherheitslücken melden

Wenn Sie eine Sicherheitslücke oder ein kritisches Datenintegritätsproblem in ProSync entdecken:

1. **Bevorzugter Meldeweg:** Nutzen Sie die private Vulnerability-Reporting-Funktion direkt auf GitHub:
   - Öffnen Sie den Tab **Security** in diesem Repository
   - Wählen Sie **Report a vulnerability**
   - Beschreiben Sie das Verhalten, Schritte zur Reproduktion und mögliche Auswirkungen
2. **Direkter E-Mail-Kontakt:** Alternativ können Sie sich direkt an unser Sicherheitsteam wenden:
   - `security@file-bricks.org`
   - `security@ellmos.ai`
   - `support@lukasgeiger.com`
   - `lukas@open-bricks.org`

Bitte öffnen Sie für Sicherheitslücken **keine öffentlichen Issues** und veröffentlichen Sie keine Pfade, Konfigurationsdaten oder vertrauliche Informationen. Bestätigte Sicherheitsprobleme werden mit höchster Priorität behoben.

---

## English

### Security Principles & Core Guarantees

`file-bricks/ProSync` is engineered as a strictly local desktop and background system-tray application for file synchronization and SQLite WAL database safety. Security and data integrity are grounded in the following guarantees:

- **Local-First & Zero-Egress:** ProSync never transmits telemetry, user data, or sync statistics over the network. All file operations execute entirely on local drives or user-configured targets (external storage, local NAS shares, or user-defined SFTP destinations).
- **Zero Cloud Requirement:** No mandatory cloud accounts or external telemetry endpoints.
- **Unprivileged User-Mode Operation (Non-Elevation):** ProSync operates strictly within standard user privileges and does not require elevated administrator rights.
- **SQLite WAL Consistency Guard:** Before synchronizing active SQLite databases, ProSync executes an automated `PRAGMA wal_checkpoint(TRUNCATE)`. If the database is busy or locked, the sync safely aborts to prevent corrupted backups.
- **Path & Credential Boundary Hygiene:** Real configuration files (`ProSync_config.json`), runtime logs, and sync caches are ignored by Git. The portable Web/PWA companion export format (`prosync-profile-v1.json`) is fully redacted and excludes absolute local paths and credentials.

### Supported Versions

| Version | Supported | Notes |
| ------- | --------- | ----- |
| 3.2.x   | Yes       | Active production release with SQLite WAL Guard, Batch Queue & Store Readiness |
| < 3.2.0 | Deprecated | Upgrade to the latest version recommended |

### Reporting a Vulnerability

If you discover a security vulnerability or critical data integrity issue in ProSync:

1. **Preferred Method:** Report privately via GitHub's Security Advisories flow:
   - Navigate to the **Security** tab of this repository
   - Click **Report a vulnerability**
   - Provide reproduction steps, affected environment, and potential impact
2. **Direct Security Email:** Alternatively, email the security coordinators directly:
   - `security@file-bricks.org`
   - `security@ellmos.ai`
   - `support@lukasgeiger.com`
   - `lukas@open-bricks.org`

Please **do not disclose vulnerabilities in public issues**. Confirmed security patches are prioritized and released promptly.
