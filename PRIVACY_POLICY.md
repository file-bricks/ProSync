# Datenschutzerklärung / Privacy Policy

## Deutsch

ProSync ist eine lokale Desktop-Anwendung. Die Software verarbeitet Dateien, Ordner und Konfigurationsdaten grundsätzlich auf dem Gerät des Nutzers oder auf ausdrücklich ausgewählten Netzlaufwerken.

### Welche Daten ProSync verarbeitet

- Lokale Quell- und Zielpfade, die der Nutzer selbst in Verbindungen hinterlegt
- Verbindungsnamen, Modi, Ausschlussmuster und Zeitpläne
- Lokale Sync-Reports mit Zeitstempeln und Zählern wie kopierte, gelöschte oder übersprungene Dateien
- Optionale Startpfade für den ProFiler-Companion

### Was ProSync nicht tut

- Keine Nutzerkonten anlegen
- Keine Telemetrie oder Analytics an Dritte senden
- Keine Cloud-Synchronisation im Hintergrund erzwingen
- Keine persönlichen Pfade oder Secrets in das redigierte Austauschformat `prosync-profile-v1.json` exportieren

### Netzwerke und Drittziele

ProSync kann lokale Netzlaufwerke oder Freigaben synchronisieren, wenn der Nutzer solche Pfade selbst auswählt. Dabei überträgt die Anwendung nur die Dateien, die für den jeweiligen Sync-Auftrag erforderlich sind.

### Speicherung

Die lokale Konfiguration (`ProSync_config.json`), Logdateien und Sync-Reports bleiben auf dem Gerät des Nutzers. Diese Dateien werden nicht automatisch an den Autor oder an Dritte übermittelt.

### Sicherheitshinweis

Bei Datei- und Datenbank-Synchronisationen trägt der Nutzer die Verantwortung für Zielpfade, Zugriffsrechte und Backup-Strategie. Vor produktiven Zwei-Wege-Syncs sollten neue Verbindungen immer zuerst manuell getestet werden.

## English

ProSync is a local desktop application. It processes files, folders, and configuration data on the user's device or on explicitly selected network shares.

### Data ProSync processes

- Local source and target paths defined by the user
- Connection names, modes, exclude patterns, and schedules
- Local sync reports with timestamps and counters for copied, deleted, or skipped files
- Optional launch paths for the ProFiler companion

### What ProSync does not do

- It does not create user accounts
- It does not send telemetry or analytics to third parties
- It does not force background cloud synchronization
- It does not export personal paths or secrets in the redacted `prosync-profile-v1.json` exchange format

### Networks and third-party destinations

ProSync can synchronize local network shares or mapped drives when the user explicitly selects them. In that case the application transfers only the files required for the chosen sync job.

### Storage

The local configuration (`ProSync_config.json`), logs, and sync reports remain on the user's machine. They are not automatically transmitted to the author or to third parties.
