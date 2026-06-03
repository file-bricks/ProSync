# ProSync - Windows Store Build-Anleitung

## Voraussetzungen

1. Python 3.10+ mit PySide6
2. PyInstaller für den Desktop-Build
3. Windows SDK mit `makeappx.exe` und `appcert.exe`
4. Lokaler Schreibpfad außerhalb von OneDrive für große MSIX-Artefakte, z. B. `C:\_Local_DEV\codex_build\prosync-store`

## Schritt 0: Store-Material aktualisieren

```powershell
cd "C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\DATA\REL-PUB_ProSync"
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
cd "C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\DATA\REL-PUB_ProSync"
build_exe.bat
```

Erwarteter Hauptpfad:

- `dist\ProSync\ProSync.exe`

## Schritt 2: Store-Pretest

```powershell
cd "C:\Users\User\OneDrive\.TOPICS\.SOFTWARE"
.\_STORE\msstore_pretest.ps1 `
  -ExePath "C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\DATA\REL-PUB_ProSync\dist\ProSync\ProSync.exe" `
  -ProjectRoot "C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\DATA\REL-PUB_ProSync" `
  -StartWait 8
```

## Schritt 3: MSIX lokal außerhalb von OneDrive bauen

Die PyInstaller-Onefolder-Struktur braucht neben `ProSync.exe` auch `_internal\` und `ProSyncReader.exe`. Deshalb werden diese Pfade explizit als Zusatzdateien übergeben.

```powershell
cd "C:\Users\User\OneDrive\.TOPICS\.SOFTWARE"
.\_STORE\msstore_build_msix.ps1 `
  -ProjectRoot "C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\DATA\REL-PUB_ProSync" `
  -ExePath "C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\DATA\REL-PUB_ProSync\dist\ProSync\ProSync.exe" `
  -OutputMsix "C:\_Local_DEV\codex_build\prosync-store\ProSync.msix" `
  -ExtraFiles @(
    "C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\DATA\REL-PUB_ProSync\dist\ProSync\_internal",
    "C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\DATA\REL-PUB_ProSync\dist\ProSync\ProSyncReader.exe",
    "C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\DATA\REL-PUB_ProSync\ProSync_config.example.json"
  )
```

## Schritt 4: WACK als Administrator

```powershell
Start-Process powershell -Verb RunAs -ArgumentList @(
  "-ExecutionPolicy Bypass",
  "-File C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\_STORE\msstore_wack.ps1",
  "-MsixPath C:\_Local_DEV\codex_build\prosync-store\ProSync.msix",
  "-ReportDir C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\DATA\REL-PUB_ProSync\releases\windowsstore\test_reports"
)
```

Die Ergebnisse danach in `releases\windowsstore\WACK_PROTOCOL.md` eintragen.
