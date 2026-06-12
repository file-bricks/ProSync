# ProSync Companion

Der Ordner `web_companion/` enthält einen statischen Web/PWA-Companion für
`prosync-profile-v1.json`.

## Zweck

- Read-only Profilansicht für Desktop, Android und iPhone/iPad
- Lokales Lesen der redigierten Report-Metadaten aus dem Desktop-Export
- Suche und Filter nach Verbindungstyp, Modus und Autosync-Status
- Offline-Wiederherstellung des zuletzt geladenen Profils im Browser
- Kein Browser-Sync, keine Cloud und keine versteckten lokalen Pfade

## Start

```bash
cd web_companion
python -m http.server 4179
```

Danach im Browser öffnen:

- `http://127.0.0.1:4179/`
- `http://127.0.0.1:4179/?demo=1` für das eingebaute Demo-Profil

## Import

1. In der Desktop-App ein Profil als `prosync-profile-v1.json` exportieren.
2. Im Companion `Profil importieren` wählen oder das JSON in das Textfeld einfügen.
3. Der letzte geladene Stand bleibt lokal im Browser-Speicher für Offline-Starts erhalten.

## Qualität

```bash
npm test
node --check app.js
node --check library.js
node --check sw.js
```

## Abgrenzung

- Lokale API-Trigger sind im Companion bewusst noch nicht verdrahtet.
- Die Browser-Linie ersetzt keine Desktop-Synchronisation.
- Android und iOS bleiben vorerst PWA-Ziele; native Mobile-Apps sind kein aktuelles Ziel.
