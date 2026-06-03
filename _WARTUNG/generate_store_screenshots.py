from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import time
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "ProSyncStart_V3.1.py"
SCREENSHOT_DIR = PROJECT_ROOT / "releases" / "windowsstore" / "screenshots"
STORE_ASSET_DIR = PROJECT_ROOT / "store_assets"
README_MAIN = PROJECT_ROOT / "screenshots" / "main.png"

SCREENSHOTS = (
    ("main-overview.png", "Hauptübersicht mit mehreren lokalen Sync-Aufgaben"),
    ("database-backup.png", "Datei-Backup mit SQLite-Schutz und WAL-Checkpoint"),
    ("portable-profile.png", "Importiertes Austauschprofil mit Hinweisen zur Neu-Zuordnung"),
)

STORE_ASSETS = (
    ("Square44x44Logo.png", 44, 44),
    ("Square150x150Logo.png", 150, 150),
    ("Wide310x150Logo.png", 310, 150),
    ("Square310x310Logo.png", 310, 310),
)


def load_prosync_module():
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    spec = importlib.util.spec_from_file_location("prosync_store_module", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def ensure_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        app.setQuitOnLastWindowClosed(False)
    return app


def build_demo_config():
    return {
        "app": {"notifications_enabled": True},
        "connections": [
            {
                "id": "folder-demo",
                "name": "Projektspiegel Laptop → NAS",
                "type": "folder",
                "source": r"C:\Users\User\Documents\Projektordner",
                "target": r"\\NAS\Backups\Projektordner",
                "mode": "mirror",
                "conflict_policy": "source",
                "indexing": True,
                "db_path": r"C:\Users\User\AppData\Roaming\ProSync\indexes\project_index.db",
                "exclude_patterns": ["*.tmp", "*.lock", "__pycache__"],
                "autosync": {"enabled": True, "interval_minutes": 30},
                "_safety_analysis": {
                    "databases_found": 3,
                    "critical_databases": 1,
                    "excluded_databases": 1,
                    "total_db_size_mb": 184.2,
                },
            },
            {
                "id": "file-demo",
                "name": "SQLite Backup Buchhaltung",
                "type": "file",
                "source_file": r"C:\Daten\Buchhaltung\data.db",
                "target_file": r"D:\Backups\Buchhaltung\data.db",
                "mode": "one_way",
                "checkpoint_before_sync": True,
                "autosync": {"enabled": True, "interval_minutes": 240},
                "_file_analysis": {
                    "type": "sqlite",
                    "wal_mode": True,
                    "is_critical": True,
                    "size_mb": 86.4,
                },
            },
            {
                "id": "portable-demo",
                "name": "Importiertes Team-Profil",
                "type": "folder",
                "source": "",
                "target": "",
                "mode": "two_way",
                "conflict_policy": "newest",
                "indexing": True,
                "db_path": "",
                "exclude_patterns": ["Thumbs.db", ".DS_Store"],
                "autosync": {
                    "enabled": False,
                    "interval_minutes": 60,
                    "_reason": "Pfadzuordnung nach Import erforderlich",
                },
                "_portable_import": {
                    "schema": "prosync-profile-v1",
                    "requires_mapping": True,
                    "original_id": "portable-origin",
                    "path_hints": {
                        "source_label": "Teamordner",
                        "target_label": "Archivlaufwerk",
                        "db_label": "index.db",
                    },
                },
                "safety_summary": {
                    "kind": "folder",
                    "databases_found": 1,
                    "critical_databases": 0,
                    "excluded_databases": 0,
                    "total_db_size_mb": 12.5,
                },
            },
        ],
    }


def wait_for_ui(app, pause: float = 0.2) -> None:
    app.processEvents()
    time.sleep(pause)
    app.processEvents()


def _select_rows(window, rows: list[int]) -> None:
    window.list.clearSelection()
    current_item = None
    for row in rows:
        item = window.list.item(row)
        if item is None:
            continue
        item.setSelected(True)
        current_item = item
    if current_item is not None:
        window.list.setCurrentItem(current_item)
    window.refresh_selection_state()


def capture_window(window, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    pixmap = window.grab()
    pixmap.save(str(target), "PNG")


def write_manifest(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Store-Screenshots", ""]
    for filename, caption in SCREENSHOTS:
        lines.append(f"- `{filename}` - {caption}")
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_asset_manifest(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Store-Assets", ""]
    for filename, width, height in STORE_ASSETS:
        lines.append(f"- `{filename}` - {width}x{height}px")
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _render_icon(icon: QIcon, width: int, height: int) -> QPixmap:
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    icon.paint(painter, 0, 0, width, height)
    painter.end()
    return pixmap


def generate_store_assets(output_dir: Path | None = None) -> list[Path]:
    ensure_app()
    output_dir = output_dir or STORE_ASSET_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    icon = QIcon(str(PROJECT_ROOT / "ICO.ico"))
    if icon.isNull():
        raise RuntimeError("ICO.ico konnte nicht als Store-Icon geladen werden")

    generated: list[Path] = []
    for filename, width, height in STORE_ASSETS:
        target = output_dir / filename
        pixmap = _render_icon(icon, width, height)
        if not pixmap.save(str(target), "PNG"):
            raise RuntimeError(f"Konnte Store-Asset nicht speichern: {target}")
        generated.append(target)

    write_asset_manifest(output_dir)
    return generated


def generate_store_screenshots(output_dir: Path | None = None) -> list[Path]:
    app = ensure_app()
    output_dir = output_dir or SCREENSHOT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    prosync = load_prosync_module()
    with tempfile.TemporaryDirectory(prefix="prosync-store-") as temp_dir:
        config_path = Path(temp_dir) / "ProSync_config.json"
        config_path.write_text(
            json.dumps(build_demo_config(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        cfg = prosync.ConfigManager(str(config_path))
        window = prosync.MainWindow(cfg)
        window.resize(1500, 940)
        window.show()
        wait_for_ui(app, pause=0.4)

        targets: list[Path] = []
        try:
            _select_rows(window, [0])
            wait_for_ui(app)
            target = output_dir / SCREENSHOTS[0][0]
            capture_window(window, target)
            targets.append(target)

            _select_rows(window, [1])
            wait_for_ui(app)
            target = output_dir / SCREENSHOTS[1][0]
            capture_window(window, target)
            targets.append(target)

            _select_rows(window, [2])
            wait_for_ui(app)
            target = output_dir / SCREENSHOTS[2][0]
            capture_window(window, target)
            targets.append(target)
        finally:
            window.tray_icon.hide()
            window.close()
            wait_for_ui(app, pause=0.1)

    README_MAIN.parent.mkdir(parents=True, exist_ok=True)
    README_MAIN.write_bytes((output_dir / SCREENSHOTS[0][0]).read_bytes())
    write_manifest(output_dir)
    return targets


def main() -> int:
    asset_targets = generate_store_assets()
    screenshot_targets = generate_store_screenshots()
    for target in [*asset_targets, *screenshot_targets]:
        print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
