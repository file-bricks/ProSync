# Store Listing - ProSync

## Deutsch

### Kurzbeschreibung (max 100 Zeichen)
Lokales Backup- und Sync-Tool mit Datenbankschutz, Batch-Sync und redigiertem Profil-Export.

### Beschreibung (max 10.000 Zeichen)
ProSync ist eine lokale Desktop-Anwendung für Datei- und Ordner-Synchronisation mit besonderem Fokus auf sichere Backups für SQLite- und Access-Dateien. Das Tool läuft ohne Cloud-Zwang, arbeitet direkt mit lokalen Pfaden oder Netzlaufwerken und hilft dabei, wiederkehrende Sync-Jobs planbar und transparent auszuführen.

**Was ProSync kann:**

- Ordner-Synchronisation: Einweg, Update, Spiegelung oder Zwei-Wege-Sync für lokale Ordner und Freigaben
- Datei-Synchronisation: Einzelne Dateien separat absichern, ideal für Datenbanken oder sensible Projektdateien
- Datenbankschutz: SQLite- und Access-Dateien werden erkannt; WAL-Dateien und kritische Fälle werden sicher behandelt
- Batch-Sync: Mehrere ausgewählte Verbindungen in einem Lauf nacheinander starten
- Geplante Backups: Intervalle pro Verbindung festlegen und im Hintergrund über das Tray ausführen
- Sync-Reports: Kopierte, gelöschte und übersprungene Dateien werden lokal protokolliert
- Companion-Export: Redigierte Profile als `prosync-profile-v1.json` ohne echte lokale Pfade und ohne Secrets austauschen
- ProFiler-Companion: Optionalen ProFiler direkt aus ProSync starten

**Warum ProSync?**

- Lokal zuerst: Keine Pflicht-Cloud, keine Kontoregistrierung, keine versteckte Datensynchronisation
- Sicherer Umgang mit Datenbanken: Kritische SQLite-Dateien werden nicht wie normale Dateien behandelt
- Praktisch für den Alltag: Tray-Betrieb, Zeitpläne, Batch-Läufe und klare Statusanzeige
- Austauschfähig: Profile können redigiert exportiert werden, ohne private Pfade oder Tokens offenzulegen

**Für wen ist ProSync gedacht?**

Für Entwickler, Selbstständige, Power-User und kleine Teams, die lokale Projektordner, Dokumente oder Datenbanken regelmäßig sichern oder zwischen Geräten abgleichen möchten, ohne daraus gleich eine Cloud-Plattform zu machen.

### Schlüsselwörter
Backup, Synchronisation, Datei-Sync, Ordner-Sync, SQLite, Datenbankschutz, Batch-Sync, Netzlaufwerk, Profil-Export, lokale Backups

### Kategorie
Utilities

---

## English

### Short Description (max 100 chars)
Local backup and sync tool with database safety, batch runs, and redacted profile exchange.

### Description (max 10,000 chars)
ProSync is a local desktop application for file and folder synchronization with a strong focus on safe backups for SQLite and Access data. It works directly with local paths or network shares, avoids cloud lock-in, and makes recurring sync jobs transparent and repeatable.

**What ProSync does:**

- Folder synchronization: One-way, update, mirror, or two-way sync for local folders and shares
- File synchronization: Protect individual files separately, ideal for databases or sensitive project files
- Database safety: Detects SQLite and Access files and handles WAL-related edge cases deliberately
- Batch sync: Run multiple selected connections sequentially in one batch
- Scheduled backups: Configure per-connection intervals and keep jobs running in the tray
- Sync reports: Stores local reports with copied, deleted, and skipped file counters
- Companion export: Exchange redacted `prosync-profile-v1.json` profiles without real local paths or secrets
- ProFiler companion: Launch an optional ProFiler sidecar directly from ProSync

**Why ProSync?**

- Local first: No required cloud account, no forced online backend, no hidden remote sync
- Safer database handling: Critical SQLite files are not treated like ordinary documents
- Practical desktop workflow: Tray mode, schedules, batch execution, and clear status feedback
- Portable collaboration: Exchange profiles without exposing private paths or tokens

**Who is ProSync for?**

Developers, freelancers, power users, and small teams who want to back up or synchronize project folders, documents, and database files across devices without turning the workflow into a cloud platform.

### Keywords
backup, sync, file sync, folder sync, SQLite, database safety, batch sync, network share, profile export, local backup

### Category
Utilities
