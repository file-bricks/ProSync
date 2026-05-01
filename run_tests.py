"""Run ProSync smoke tests in the same way locally and in CI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


TEST_FILES = [
    "test_batch_sync_queue.py",
    "test_config_manager.py",
    "test_database_safety.py",
    "test_import_streams.py",
    "test_sync_worker.py",
]


def main() -> int:
    project_root = Path(__file__).resolve().parent
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("QT_QPA_PLATFORM", "offscreen")

    failed: list[str] = []
    for test_file in TEST_FILES:
        print(f"\n=== {test_file} ===", flush=True)
        result = subprocess.run(
            [sys.executable, str(project_root / test_file)],
            cwd=project_root,
            env=env,
            check=False,
        )
        if result.returncode != 0:
            failed.append(test_file)

    if failed:
        print("\nFAILED:", ", ".join(failed), flush=True)
        return 1

    print("\nAll smoke tests passed.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
