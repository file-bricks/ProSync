@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

python -m PyInstaller --noconfirm --clean --onedir --windowed --name ProSync --icon ICO.ico --add-data "locales;locales" --add-data "ICO_TRAY.ico;." ProSyncStart_V3.1.py
if errorlevel 1 (
    echo FEHLER: ProSync Build fehlgeschlagen.
    pause
    exit /b 1
)

python -m PyInstaller --noconfirm --clean --onefile --windowed --name ProSyncReader ProSyncReader.py
if errorlevel 1 (
    echo FEHLER: ProSyncReader Build fehlgeschlagen.
    pause
    exit /b 1
)

copy /Y "dist\\ProSyncReader.exe" "dist\\ProSync\\ProSyncReader.exe" >nul
if errorlevel 1 (
    echo FEHLER: ProSyncReader.exe konnte nicht in den ProSync Build kopiert werden.
    pause
    exit /b 1
)

if exist "dist\\ProSyncReader.exe" del /Q "dist\\ProSyncReader.exe"

echo Build fertig: dist\\ProSync\\ProSync.exe + dist\\ProSync\\ProSyncReader.exe
