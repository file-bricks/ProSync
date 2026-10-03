"""Contract tests for ProSync macOS and Linux platform smoke suites."""

from __future__ import annotations

import tests.linux_platform_smoke as linux_smoke
import tests.macos_platform_smoke as macos_smoke


def test_macos_platform_smoke_suite() -> None:
    """Run full suite of 8 macOS platform smoke checks."""
    macos_smoke.test_macos_open_dispatch()
    macos_smoke.test_macos_offscreen_window_lifecycle()
    macos_smoke.test_macos_app_paths_and_reports()
    macos_smoke.test_macos_sibling_and_tool_launcher()
    macos_smoke.test_macos_redacted_profile_export_import()
    macos_smoke.test_macos_cross_os_conflict_rules()
    macos_smoke.test_macos_translation_parity()
    macos_smoke.test_macos_sqlite_safety_and_wal_checkpoint()


def test_linux_platform_smoke_suite() -> None:
    """Run full suite of 9 Linux platform smoke checks."""
    linux_smoke.test_linux_open_dispatch()
    linux_smoke.test_linux_offscreen_window_lifecycle()
    linux_smoke.test_linux_app_paths_and_reports()
    linux_smoke.test_linux_sibling_and_tool_launcher()
    linux_smoke.test_linux_redacted_profile_export_import()
    linux_smoke.test_linux_cross_os_conflict_rules()
    linux_smoke.test_linux_translation_parity()
    linux_smoke.test_linux_sqlite_safety_and_wal_checkpoint()
    linux_smoke.test_linux_autostart_and_desktop_entry()


def test_platform_smokes_preserve_environment() -> None:
    """Ensure that running smoke suites does not pollute or corrupt os.environ (e.g. APPDATA)."""
    import os
    appdata_before = os.environ.get("APPDATA")
    test_macos_platform_smoke_suite()
    test_linux_platform_smoke_suite()
    assert os.environ.get("APPDATA") == appdata_before
