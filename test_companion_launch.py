"""
Smoke tests for the ProFiler companion launcher.
"""

import importlib.util
import os
import sys
import tempfile
from pathlib import Path


EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def load_prosync_module():
    """Load the main ProSync module via importlib."""
    module_path = os.path.join(os.path.dirname(__file__), "ProSyncStart_V3.1.py")
    spec = importlib.util.spec_from_file_location("prosync_companion", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    print("=== ProFiler Companion Launcher Smoke-Test ===\n")

    try:
        prosync = load_prosync_module()

        print("Test 1: Configured file path wins")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            base_dir = tmp / "REL-PUB_ProSync"
            base_dir.mkdir()
            configured_file = tmp / "custom" / "ProFiler.exe"
            configured_file.parent.mkdir()
            configured_file.write_text("", encoding="utf-8")

            resolved = prosync.resolve_profiler_launch_path(base_dir, str(configured_file))
            assert resolved == configured_file
        print("✓ PASS: Direkter Datei-Pfad wird bevorzugt\n")

        print("Test 2: Configured directory path resolves entrypoint")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            base_dir = tmp / "REL-PUB_ProSync"
            base_dir.mkdir()
            configured_dir = tmp / "custom"
            configured_dir.mkdir()
            expected = configured_dir / "Profiler_Suite_V15.py"
            expected.write_text("", encoding="utf-8")

            resolved = prosync.resolve_profiler_launch_path(base_dir, str(configured_dir))
            assert resolved == expected
        print("✓ PASS: Verzeichnis-Pfad wird korrekt aufgelöst\n")

        print("Test 3: Sibling fallback works")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            base_dir = tmp / "REL-PUB_ProSync"
            base_dir.mkdir()
            sibling_root = tmp / "REL-PUB_ProFiler"
            sibling_root.mkdir()
            expected = sibling_root / "Profiler_Suite_V15.py"
            expected.write_text("", encoding="utf-8")

            resolved = prosync.resolve_profiler_launch_path(base_dir)
            assert resolved == expected
        print("✓ PASS: Gemeinsamer Software-Baum wird gefunden\n")

        print("Test 4: Missing tool returns None")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            base_dir = tmp / "REL-PUB_ProSync"
            base_dir.mkdir()

            resolved = prosync.resolve_profiler_launch_path(base_dir)
            assert resolved is None
        print("✓ PASS: Fehlende Tools liefern None\n")

        print("=== ALLE TESTS BESTANDEN ✓ ===")
        return EXIT_SUCCESS

    except AssertionError as exc:
        print(f"\n✗ TEST FEHLGESCHLAGEN: {exc}")
        return EXIT_FAILURE
    except Exception as exc:
        print(f"\n✗ UNERWARTETER FEHLER: {exc}")
        import traceback
        traceback.print_exc()
        return EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
