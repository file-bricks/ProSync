# Mobile-Smoke – web_companion

Stand: 2026-07-02

## Lokal geprüfter Smoke

- Surface: `web_companion/` lokal über `python -m http.server 4179`
- URL: `http://127.0.0.1:4179/`
- Viewports:
  - Desktop-Standard im In-App-Browser
  - Mobile-Override `390x844`
- Geprüfter Flow:
  1. Companion laden
  2. `Demo laden`
  3. Wiederherstellung aus Browser-Speicher nach Reload prüfen
  4. Filter `Autosync -> Aktiv`
  5. Suche `ledger`

## Ergebnis

- Seite rendert auf Desktop und Mobile ohne Blank-State oder Framework-Overlay.
- Browser-Konsole blieb im geprüften Flow ohne relevante Warnungen oder Fehler.
- Demo-Profil, Statistik-Karten, Filter und Report-Metadaten bleiben im Mobile-Viewport ohne horizontales Overflow sichtbar.
- Der letzte Profilstand wird nach Reload lokal wiederhergestellt.
- Filter und Suche reagieren korrekt; bei `Autosync = Aktiv` bleibt nur die aktive Verbindung sichtbar, die Suche `ledger` reduziert die sichtbare Liste korrekt auf `0 sichtbar`.

## Offen

- Kein echter Android- oder iOS-Geräte-Smoke in Safari/Chrome/Capacitor.
- Kein Dateiupload-Test über reale mobile Dateiauswahl.
- Kein Install-/Add-to-Home-Screen-Check auf echten Geräten.
