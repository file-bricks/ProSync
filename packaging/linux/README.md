# Linux Integration & Desktop Packaging für ProSync

Dieses Verzeichnis enthält die standardisierten Integrationsdateien für Linux-Desktop-Umgebungen (GNOME, KDE Plasma, XFCE u.a.) gemäß XDG Desktop Entry Specification.

## 1. Desktop-Integration (`prosync.desktop`)

### Systemweite Installation
```bash
sudo cp packaging/linux/prosync.desktop /usr/share/applications/
sudo cp ProSync.png /usr/share/icons/hicolor/256x256/apps/prosync.png
sudo update-desktop-database /usr/share/applications/
```

### Benutzerweite Installation (ohne Root-Rechte)
```bash
mkdir -p ~/.local/share/applications ~/.local/share/icons/hicolor/256x256/apps
cp packaging/linux/prosync.desktop ~/.local/share/applications/
cp ProSync.png ~/.local/share/icons/hicolor/256x256/apps/prosync.png
update-desktop-database ~/.local/share/applications/
```

## 2. Autostart-Verhalten (XDG Autostart)

ProSync implementiert in `AutostartManager` die XDG Autostart Specification:
- **Zielverzeichnis:** `$XDG_CONFIG_HOME/autostart/` (Standard: `~/.config/autostart/`)
- **Autostart-Datei:** `prosync.desktop`
- **Aktivierung/Deaktivierung:** Kann direkt über das Anwendungsmenü (Bearbeiten → Autostart) oder programmatisch über `AutostartManager.set_autostart(True/False)` geschaltet werden.
- **Sicherheit:** Das Schreiben erfolgt atomar über temporäre Zwischendatei mit `fsync` und `os.replace`.
