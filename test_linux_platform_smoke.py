"""Linux platform smoke test for ProSync."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
PROJECT_ROOT = Path(__file__).resolve().parent


def load_prosync_module():
    """Load the main ProSync module via importlib."""
    sys.path.insert(0, str(PROJECT_ROOT))
    module_path = PROJECT_ROOT / "ProSyncStart_V3.1.py"
    spec = importlib.util.spec_from_file_location("prosync_linux_smoke", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    print("=== ProSync Linux Platform Smoke-Test ===\n")

    try:
        prosync = load_prosync_module()
        import prosync_utils
        from PySide6.QtWidgets import QApplication

        print("Test 1: Linux opener uses xdg-open and ignores missing paths")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            probe_file = tmp / "Überblick.txt"
            probe_file.write_text("Test", encoding="utf-8")
            captured_calls: list[list[str]] = []

            def fake_call(command):
                captured_calls.append(command)
                return 0

            with mock.patch.object(prosync_utils.sys, "platform", "linux"), mock.patch.object(
                prosync_utils.subprocess,
                "call",
                side_effect=fake_call,
            ):
                prosync_utils.open_file_cross_platform(str(probe_file))
                prosync_utils.open_folder_cross_platform(str(probe_file))
                prosync_utils.open_file_cross_platform(str(tmp / "fehlt.txt"))

            assert captured_calls == [
                ["xdg-open", str(probe_file)],
                ["xdg-open", str(probe_file.parent)],
            ]
        print("PASS: xdg-open path handling behaves as expected\n")

        print("Test 2: Linux smoke covers resolver, redacted export and UTF-8")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            os.environ["APPDATA"] = str(tmp / "appdata")
            base_dir = tmp / "REL-PUB_ProSync"
            base_dir.mkdir()
            profiler_root = tmp / "REL-PUB_ProFiler"
            profiler_root.mkdir()
            profiler_entry = profiler_root / "Profiler_Suite_V15.py"
            profiler_entry.write_text("# smoke\n", encoding="utf-8")

            resolved = prosync.resolve_profiler_launch_path(base_dir)
            assert resolved == profiler_entry

            reports_path = Path(os.environ["APPDATA"]) / "ProSync" / "reports" / "sync_log.json"
            reports_path.parent.mkdir(parents=True, exist_ok=True)
            reports_path.write_text(
                json.dumps(
                    [
                        {
                            "connection": "Über Sync",
                            "connection_id": "conn-linux",
                            "mode": "mirror",
                            "started_at": "2026-06-03T08:00:00+00:00",
                            "duration_seconds": 4.25,
                            "files_copied": 3,
                            "files_deleted": 0,
                            "files_skipped": 1,
                            "bytes_copied": 4096,
                            "total_actions": 4,
                        }
                    ],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            cfg = prosync.ConfigManager(str(base_dir / "ProSync_config.json"))
            cfg.data["app"] = {"notifications_enabled": True}
            cfg.data["connections"] = [
                {
                    "id": "conn-linux",
                    "name": "Über Sync",
                    "type": "folder",
                    "source": "/srv/Überblick/Projekt",
                    "target": "/mnt/Archiv/Größe",
                    "mode": "mirror",
                    "exclude_patterns": ["*.tmp", "__pycache__"],
                    "autosync": {"enabled": True, "interval_minutes": 30},
                    "conflict_policy": "source",
                    "indexing": True,
                    "db_path": "/srv/Überblick/Projekt/index.db",
                }
            ]

            export_path = tmp / "prosync-profile-v1.json"
            payload = cfg.export_portable_profile(str(export_path))
            exported = json.loads(export_path.read_text(encoding="utf-8"))
            export_text = export_path.read_text(encoding="utf-8")

            assert payload["schema"] == "prosync-profile-v1"
            assert exported["connections"][0]["path_hints"] == {
                "source_label": "Projekt",
                "target_label": "Größe",
                "db_label": "index.db",
            }
            assert exported["reports"]["count"] == 1
            assert exported["reports"]["latest"]["connection"] == "Über Sync"
            assert "/srv/Überblick/Projekt" not in export_text
            assert "/mnt/Archiv/Größe" not in export_text
        print("PASS: Redacted Linux export keeps reports and real umlauts\n")

        print("Test 3: Headless window starts and Linux launcher skips Windows flags")
        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            cfg = prosync.ConfigManager(str(tmp / "ProSync_config.json"))
            window = prosync.MainWindow(cfg)
            tool_path = tmp / "dummy_tool.py"
            tool_path.write_text("print('smoke')\n", encoding="utf-8")

            with mock.patch.object(prosync.sys, "platform", "linux"), mock.patch.object(
                prosync.subprocess,
                "Popen",
            ) as popen_mock:
                window._launch_tool_process(tool_path)

            launch_cmd = popen_mock.call_args.args[0]
            launch_kwargs = popen_mock.call_args.kwargs
            assert launch_cmd == [sys.executable, str(tool_path)]
            assert launch_kwargs["cwd"] == str(tool_path.parent)
            assert "creationflags" not in launch_kwargs
            assert window.tray_icon is not None

            window.tray_icon.hide()
            window.close()
        app.quit()
        print("PASS: Headless main window and Linux launch path work\n")

        print("=== ALL TESTS PASSED ===")
        return EXIT_SUCCESS

    except AssertionError as exc:
        print(f"\nTEST FAILED: {exc}")
        return EXIT_FAILURE
    except Exception as exc:
        print(f"\nUNEXPECTED ERROR: {exc}")
        import traceback

        traceback.print_exc()
        return EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
