# Portierungsplan: ProSync

Stand: 2026-05-26

## Ausgangslage

ProSync ist eine lokale Desktop-Anwendung für Datei- und Datenbank-Synchronisation mit besonderem Schutz für SQLite- und Access-Dateien. Die aktuelle Codebasis ist PySide6-basiert, nutzt lokale Pfade, System-Tray, Windows-Autostart und optional den ProFiler-Companion. Eine eigenständige Portierungsplanung lag vor diesem Check nicht vor.

Der Mobilitätsfaktor ist mittel: Die eigentliche Synchronisation bleibt wegen Dateisystemrechten, Netzlaufwerken, WAL-Checkpoint und Hintergrundlauf sinnvollerweise eine Desktop-Aufgabe. Mobil und Web sind dennoch nützlich für Statusansicht, Verbindungsprofile, manuelle Trigger und Export/Import zwischen Geräten.

## Entscheidung

1. **Windows Store zuerst.** ProSync ist MIT-lizenziert, PySide6-kompatibel und bereits als Desktop-Tool nutzbar. Der Windows Store ist der passende Hauptkanal für normale Anwender.
2. **macOS und Linux als Desktop-Smoke-Ziele.** Die PySide6-Codebasis kann grundsätzlich plattformübergreifend laufen, aber Autostart, Tray, Pfadwahl, Dateiöffnen und Netzlaufwerke brauchen OS-spezifische Tests. Keine getrennten Desktop-Rebuilds, solange die gemeinsame Codebasis genügt.
3. **Web/PWA als Companion, nicht als Sync-Engine.** Browser können lokale Sync-Jobs nicht zuverlässig und sicher ausführen. Die Web-Linie soll Profile anzeigen, Reports lesen, Aufgaben manuell triggern und ein Austauschformat verwalten.
4. **Android/iOS über PWA/Capacitor prüfen.** Native Mobile-Clones sind nicht sinnvoll, weil mobile Sandboxes keinen freien Zugriff auf lokale Ordner, Netzlaufwerke und Datenbankdateien geben. Mobile bleibt Companion für Status, Reports und Remote-Trigger.
5. **Export/Import als Brücke.** Desktop-ProSync soll ein stabiles Austauschformat `prosync-profile-v1.json` liefern, das Verbindungen, Ausschlussmuster, Scheduler-Einstellungen und Report-Metadaten ohne persönliche Secrets transportiert.

## Plattformbewertung

| Plattform | Bewertung | Entscheidung |
|---|---|---|
| Windows Store | Hoher Nutzen: Zielgruppe sucht ein installierbares Backup-/Sync-Tool mit GUI. | P1: Store-Vorbereitung, Screenshots, Listing, MSIX/WACK. |
| Android | Nur als Companion sinnvoll; echte lokale Ordner-Synchronisation ist sandboxbedingt schwach. | P2: PWA/Capacitor-Status- und Trigger-Companion nach Exportformat. |
| Webapp | Sinnvoll für lokale Statusansicht, Reports, Profilverwaltung und Remote-Trigger über lokale API. | P1/P2: Web/PWA-Companion, keine Browser-Sync-Engine. |
| iOS | Gleiche Einschränkungen wie Android, zusätzlich strengere Hintergrund-/Dateirechte. | P3: Nur PWA-Smoke nach Web-Companion. |
| Mac App | Sinnvoll für Desktop-Nutzer mit lokalen Projekten und externen Laufwerken. | P2: PySide6-Smoke, Pfad-/Tray-/Autostart-Abweichungen dokumentieren. |
| Linux Version | Sinnvoll für Entwickler/Admins; Dateisystem- und rsync-nahe Zielgruppe. | P2: PySide6-Smoke, Desktop-Datei und Autostart-Alternative prüfen. |

## Zielarchitektur

- Desktop bleibt autoritative Sync-Engine: `ProSyncStart_V3.1.py`, lokale Konfiguration, Tray, Scheduler und Dateisystemzugriff.
- Austauschformat `prosync-profile-v1.json` wird der Vertrag zwischen Desktop und Companion.
- Web/PWA-Companion liest exportierte Profile und Reports; spätere lokale API darf Sync-Jobs triggern, aber nicht selbst Dateien synchronisieren.
- ProFiler-Companion bleibt Desktop-nah und wird in Exporten nur als optionale Referenz geführt, nicht als harte Abhängigkeit.
- Plattformtests werden in der Reihenfolge Windows Store, Linux/macOS-Smoke, Web/PWA-Companion, Android/iOS-PWA-Smoke geführt.

## Umsetzungsstatus

| Bereich | Status | Nächster Schritt |
|---|---|---|
| Windows Store | Geplant, Lizenzblocker laut Root-Pipeline erledigt. | Store-Listing, Screenshots, MSIX/WACK und Datenschutztext vorbereiten. |
| Desktop Cross-OS | Nicht geprüft. | Linux/macOS-Smoke mit PySide6, Pfadwahl, Tray und Autostart dokumentieren. |
| Export/Import | Nicht vorhanden. | `prosync-profile-v1.json` spezifizieren und Desktop-Export/Import ergänzen. |
| Web/PWA | Nicht vorhanden. | Companion-Scope auf Status, Reports, Profilanzeige und Trigger begrenzen. |
| Android/iOS | Nicht vorhanden. | Erst nach Web/PWA-Companion als PWA/Capacitor-Smoke prüfen. |

## Offene Risiken

- Zwei-Wege-Sync über mehrere Betriebssysteme braucht klare Konfliktregeln für Groß-/Kleinschreibung, Pfadseparatoren, Unicode-Normalisierung und Symlinks.
- Hintergrund-Sync, Tray und Autostart sind betriebssystemabhängig und dürfen nicht als bereits portiert gelten.
- Mobile Sandboxes verhindern eine vollwertige Sync-Engine; Mobile-Claims müssen deshalb bewusst auf Companion-Funktionen beschränkt bleiben.
- Profile dürfen keine persönlichen Pfade, Tokens oder Secrets in veröffentlichbare Beispiele leaken.
