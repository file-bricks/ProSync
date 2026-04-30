# Changelog / Aenderungsprotokoll

Alle wesentlichen Aenderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefuegt / Added
- Batch-Sync ueber Mehrfachauswahl mit Kontextmenue-Einstieg und deduplizierter Queue
- Smoke-Test `test_batch_sync_queue.py` fuer Reihenfolge, Deduplizierung und Reset-Verhalten
- Sichere Beispielkonfiguration `ProSync_config.example.json`

### Geaendert / Changed
- Hauptliste erlaubt jetzt Mehrfachauswahl fuer sequenzielle Batch-Laeufe
- Laufende Batchs werden bei Fehler oder manuellem Stop kontrolliert beendet
- Lokale `ProSync_config.json` und `SKILL.md` werden nicht mehr im GitHub-Repo getrackt

### Behoben / Fixed
- Erfolgreiche Einzel-Sync-Benachrichtigungen werden nach Fehler oder manuellem Abbruch nicht mehr faelschlich als Erfolg gemeldet

## [1.0.0] - YYYY-MM-DD

### Hinzugefuegt / Added
- Erstveroeffentlichung / Initial release
