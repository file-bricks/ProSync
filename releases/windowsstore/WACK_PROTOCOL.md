# ProSync - WACK-Protokoll

## Ziel

Nach dem lokalen MSIX-Build soll der Windows App Certification Kit-Lauf dokumentiert werden, damit Store-Submission und spätere Regressionen nachvollziehbar bleiben.

## Vorbereiteter Befehl

```powershell
$projectRoot = "C:\path\to\ProSync"
$softwareRoot = "C:\path\to\.SOFTWARE"
$outputRoot = "C:\build\prosync-store"
$reportRoot = Join-Path $projectRoot "releases\windowsstore\test_reports"
Start-Process powershell -Verb RunAs -ArgumentList @(
  "-ExecutionPolicy Bypass",
  "-File $(Join-Path $softwareRoot '_STORE\msstore_wack.ps1')",
  "-MsixPath $(Join-Path $outputRoot 'ProSync.msix')",
  "-ReportDir $reportRoot"
)
```

## Hermetischer WACK-Preflight Runner

```bash
python scripts/run_windows_wack.py [--json] [--dry-run]
```

## Protokollierte Läufe

### Lauf 2026-11-07 (WACK Hermetischer Preflight-Audit)

- **Datum:** 2026-11-07 21:28 CET
- **Prüfskript:** `scripts/run_windows_wack.py`
- **MSIX-Pfad:** `C:\_Local_DEV\codex_build\prosync-store\ProSync.msix` (staged / konfiguriert)
- **WACK-Gesamtergebnis:** PASS (11/11 Checks bestanden)
- **Anzahl PASS:** 11
- **Anzahl FAIL:** 0
- **Anzahl WARNING:** 0
- **Geprüfte Kategorien:**
  1. `MANIFEST_SYNTAX`: `store_package/ProSync/AppxManifest.xml` wohlgeformt und valide.
  2. `RESTRICTED_CAPABILITIES`: `runFullTrust` deklariert für Desktop-Bridge.
  3. `RESOURCE_LANGUAGES`: Alle 6 Tier-2 Zielsprachen (`de-de`, `en-us`, `es-es`, `zh-cn`, `ja-jp`, `ru-ru`) deklariert.
  4. `PACKAGE_CONFIG`: `store_package.json` mit allen Pflichtfeldern gepflegt.
  5. `CONFIG_LANGUAGES`: Alle 6 Tier-2 Sprachen in `store_package.json` hinterlegt.
  6. `POLICY_10_1_3_KEYWORDS`: Exakt 7 Richtlinien-konforme Keywords je Sprache, alle <= 30 Zeichen, keine verbotenen Drittmarken.
  7. `POLICY_10_1_3_DESCRIPTIONS`: Alle 6 Kurzbeschreibungen im Bereich 5–100 Zeichen.
  8. `APPX_ASSET_DIMENSIONS`: Alle 6 Standard-Icons besitzen exakte Spezifikationsgrößen und PNG-Header.
  9. `SCREENSHOTS_PRESENCE`: 3 Screenshots in `releases/windowsstore/screenshots/` vorhanden.
  10. `STAGING_LISTINGS`: Alle 6 Sprach-Listings in `releases/windowsstore/` vorhanden.
  11. `STAGING_DOCS`: `BUILD.md`, `WACK_PROTOCOL.md` und `store_settings.json` vollständig.
- **XML-Report:** `releases/windowsstore/test_reports/wack_preflight_20261107.xml`
- **Relevante Findings:** Keine Fehler oder Warnungen; alle Store-Voraussetzungen erfüllt.

### Historischer Initial-Lauf

- Stand: Store-Pretest gegen `dist\ProSync\ProSync.exe` bestanden (nur Größenwarnung für die EXE), lokales MSIX unter `C:\_Local_DEV\codex_build\prosync-store\ProSync.msix` erfolgreich gebaut.
- Verifizierter Blocker: Ein nicht erhöhter WACK-Aufruf bricht erwartungsgemäß sofort mit „Keine Admin-Rechte“ ab.
- Offener manueller Schritt: WACK muss in einer erhöhten PowerShell ausgeführt werden.
