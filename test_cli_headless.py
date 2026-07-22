"""Regression tests for the headless ProSync CLI."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication


_QT_APP = None


def ensure_qt_app():
    """Use QApplication in the shared pytest process so later UI tests stay valid."""
    global _QT_APP
    _QT_APP = QApplication.instance() or QApplication([])
    return _QT_APP


def load_prosync_module():
    module_path = Path(__file__).with_name("ProSyncStart_V3.1.py")
    spec = importlib.util.spec_from_file_location("prosync_cli", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_config(path: Path, connections: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"app": {}, "connections": connections}, ensure_ascii=False),
        encoding="utf-8",
    )


def run_cli_capture(prosync, args: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = prosync.run_cli(args)
    return code, stdout.getvalue(), stderr.getvalue()


def test_cli_lists_connections(tmp_path: Path) -> None:
    ensure_qt_app()
    tmp_path.mkdir(parents=True, exist_ok=True)
    prosync = load_prosync_module()
    config_path = tmp_path / "ProSync_config.json"
    write_config(
        config_path,
        [
            {
                "id": "conn-1",
                "name": "Tägliches Backup",
                "type": "file",
                "mode": "one_way",
            }
        ],
    )

    code, stdout, stderr = run_cli_capture(
        prosync,
        ["--config", str(config_path), "--list"],
    )

    assert code == 0
    assert stderr == ""
    assert "conn-1" in stdout
    assert "Tägliches Backup" in stdout
    assert "file" in stdout


def test_cli_runs_file_connection_by_id(tmp_path: Path) -> None:
    ensure_qt_app()
    tmp_path.mkdir(parents=True, exist_ok=True)
    prosync = load_prosync_module()
    config_path = tmp_path / "ProSync_config.json"
    source_file = tmp_path / "Quelle.txt"
    target_file = tmp_path / "ziel" / "Kopie.txt"
    source_file.write_text("Hallo äöü", encoding="utf-8")
    write_config(
        config_path,
        [
            {
                "id": "copy-1",
                "name": "Datei Kopie",
                "type": "file",
                "source_file": str(source_file),
                "target_file": str(target_file),
                "mode": "one_way",
                "checkpoint_before_sync": False,
            }
        ],
    )

    code, stdout, stderr = run_cli_capture(
        prosync,
        ["--config", str(config_path), "--run", "copy-1"],
    )

    assert code == 0
    assert stderr == ""
    assert "Starte: Datei Kopie" in stdout
    assert target_file.read_text(encoding="utf-8") == "Hallo äöü"


def test_cli_all_runs_connections_sequentially(tmp_path: Path) -> None:
    ensure_qt_app()
    tmp_path.mkdir(parents=True, exist_ok=True)
    prosync = load_prosync_module()
    config_path = tmp_path / "ProSync_config.json"
    first_source = tmp_path / "eins.txt"
    second_source = tmp_path / "zwei.txt"
    first_target = tmp_path / "out" / "eins.txt"
    second_target = tmp_path / "out" / "zwei.txt"
    first_source.write_text("eins", encoding="utf-8")
    second_source.write_text("zwei", encoding="utf-8")
    write_config(
        config_path,
        [
            {
                "id": "first",
                "name": "Erster Lauf",
                "type": "file",
                "source_file": str(first_source),
                "target_file": str(first_target),
                "mode": "one_way",
                "checkpoint_before_sync": False,
            },
            {
                "id": "second",
                "name": "Zweiter Lauf",
                "type": "file",
                "source_file": str(second_source),
                "target_file": str(second_target),
                "mode": "one_way",
                "checkpoint_before_sync": False,
            },
        ],
    )

    code, stdout, stderr = run_cli_capture(
        prosync,
        ["--config", str(config_path), "--all"],
    )

    assert code == 0
    assert stderr == ""
    assert "[1/2]" in stdout
    assert "[2/2]" in stdout
    assert first_target.read_text(encoding="utf-8") == "eins"
    assert second_target.read_text(encoding="utf-8") == "zwei"


def main() -> int:
    try:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            test_cli_lists_connections(base / "list")
            test_cli_runs_file_connection_by_id(base / "run")
            test_cli_all_runs_connections_sequentially(base / "all")
        print("=== CLI-Tests bestanden ===")
        return 0
    except Exception as exc:
        print(f"CLI-Test fehlgeschlagen: {exc}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
