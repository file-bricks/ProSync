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

## Aktueller Status

- Stand dieses Laufs: Store-Pretest gegen `dist\ProSync\ProSync.exe` bestanden (nur Größenwarnung für die EXE), lokales MSIX unter `C:\_Local_DEV\codex_build\prosync-store\ProSync.msix` erfolgreich gebaut.
- Verifizierter Blocker: Ein nicht erhöhter WACK-Aufruf bricht erwartungsgemäß sofort mit „Keine Admin-Rechte“ ab.
- Offener manueller Schritt: WACK muss in einer erhöhten PowerShell ausgeführt werden.
- Erwartete Ablage:
  - XML-Report unter `releases\windowsstore\test_reports\`
  - Konsolenlog unter `releases\windowsstore\test_reports\`

## Eintrag für den nächsten Lauf

- Datum:
- MSIX-Pfad:
- WACK-Gesamtergebnis:
- Anzahl PASS:
- Anzahl FAIL:
- Anzahl WARNING:
- Relevante Findings:
- Nächste Korrektur:
