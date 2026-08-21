#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Source platform smoke test runner for ProSync (Linux + macOS)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import tests.linux_platform_smoke as linux_smoke
import tests.macos_platform_smoke as macos_smoke

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def main() -> int:
    print("=== ProSync Cross-Platform Source Smoke Runner ===\n")
    try:
        print("--- Running Linux Platform Smoke Suite ---")
        ret_linux = linux_smoke.main()
        if ret_linux != EXIT_SUCCESS:
            print("Linux Platform Smoke Suite failed.")
            return EXIT_FAILURE

        print("\n--- Running macOS Platform Smoke Suite ---")
        ret_macos = macos_smoke.main()
        if ret_macos != EXIT_SUCCESS:
            print("macOS Platform Smoke Suite failed.")
            return EXIT_FAILURE

        print("\n=== ALL CROSS-PLATFORM SOURCE SMOKES PASSED ===")
        return EXIT_SUCCESS
    except Exception as exc:
        print(f"\nUNEXPECTED ERROR: {exc}")
        import traceback

        traceback.print_exc()
        return EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
