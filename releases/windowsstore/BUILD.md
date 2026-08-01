# ProSync - Windows Store Build-Anleitung

## Voraussetzungen

1. Python 3.10+ mit PySide6
2. PyInstaller für den Desktop-Build
3. Windows SDK mit `makeappx.exe` und `appcert.exe`
4. Lokaler Schreibpfad außerhalb eines synchronisierten Ordners für große MSIX-Artefakte, z. B. `C:\build\prosync-store`

Die Befehle verwenden bewusst Platzhalter statt personenbezogener Arbeitsverzeichnisse.
Setze `$projectRoot` auf den lokalen ProSync-Checkout und `$softwareRoot` auf den
lokalen `.SOFTWARE`-Pipelineordner, der die Store-Skripte enthält.

## Schritt 0: Store-Material aktualisieren

```powershell
$projectRoot = "C:\path\to\ProSync"
Set-Location $projectRoot
$env:PYTHONIOENCODING="utf-8"
python _WARTUNG\generate_store_screenshots.py
```

Erzeugt:

- `store_assets\Square44x44Logo.png`
- `store_assets\Square150x150Logo.png`
- `store_assets\Wide310x150Logo.png`
- `store_assets\Square310x310Logo.png`
- `releases\windowsstore\screenshots\main-overview.png`
- `releases\windowsstore\screenshots\database-backup.png`
- `releases\windowsstore\screenshots\portable-profile.png`
- `screenshots\main.png`

## Schritt 1: Desktop-EXE bauen

```powershell
Set-Location $projectRoot
build_exe.bat
```

Erwarteter Hauptpfad:

- `dist\ProSync\ProSync.exe`

## Schritt 2: Store-Pretest

```powershell
$softwareRoot = "C:\path\to\.SOFTWARE"
& (Join-Path $softwareRoot "_STORE\msstore_pretest.ps1") `
  -ExePath (Join-Path $projectRoot "dist\ProSync\ProSync.exe") `
  -ProjectRoot $projectRoot `
  -StartWait 8
```

## Schritt 3: MSIX lokal außerhalb von OneDrive bauen

Die PyInstaller-Onefolder-Struktur braucht neben `ProSync.exe` auch `_internal\` und `ProSyncReader.exe`. Deshalb werden diese Pfade explizit als Zusatzdateien übergeben.

```powershell
$outputRoot = "C:\build\prosync-store"
& (Join-Path $softwareRoot "_STORE\msstore_build_msix.ps1") `
  -ProjectRoot $projectRoot `
  -ExePath (Join-Path $projectRoot "dist\ProSync\ProSync.exe") `
  -OutputMsix (Join-Path $outputRoot "ProSync.msix") `
  -ExtraFiles @(
    (Join-Path $projectRoot "dist\ProSync\_internal"),
    (Join-Path $projectRoot "dist\ProSync\ProSyncReader.exe"),
    (Join-Path $projectRoot "ProSync_config.example.json")
  )
```

## Schritt 4: WACK als Administrator

```powershell
$reportRoot = Join-Path $projectRoot "releases\windowsstore\test_reports"
Start-Process powershell -Verb RunAs -ArgumentList @(
  "-ExecutionPolicy Bypass",
  "-File $(Join-Path $softwareRoot '_STORE\msstore_wack.ps1')",
  "-MsixPath $(Join-Path $outputRoot 'ProSync.msix')",
  "-ReportDir $reportRoot"
)
```

Die Ergebnisse danach in `releases\windowsstore\WACK_PROTOCOL.md` eintragen.
