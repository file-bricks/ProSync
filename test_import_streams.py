"""
Regression tests for import-time stream handling.
"""

import importlib.util
import os
import sys

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def test_import_keeps_existing_std_stream_objects():
    """Importing the GUI module must not replace stdout/stderr capture objects."""
    module_path = os.path.join(os.path.dirname(__file__), "ProSyncStart_V3.1.py")
    spec = importlib.util.spec_from_file_location("prosync_stream_regression", module_path)
    module = importlib.util.module_from_spec(spec)

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    spec.loader.exec_module(module)

    assert sys.stdout is original_stdout
    assert sys.stderr is original_stderr


def main():
    """Run the import stream regression as a standalone smoke test."""
    try:
        test_import_keeps_existing_std_stream_objects()
        print("PASS: import keeps existing stdout/stderr objects")
        return EXIT_SUCCESS
    except AssertionError as exc:
        print(f"FAIL: import stream regression failed: {exc}")
        return EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
