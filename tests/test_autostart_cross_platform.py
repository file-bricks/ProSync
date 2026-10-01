"""Tests for cross-platform AutostartManager and Linux desktop packaging."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = PROJECT_ROOT / "ProSyncStart_V3.1.py"


def _load_prosync_module():
    spec = importlib.util.spec_from_file_location("prosync_autostart_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_linux_autostart_enable_creates_desktop_file() -> None:
    """AutostartManager.set_autostart(True) creates XDG autostart .desktop file on Linux."""
    prosync = _load_prosync_module()
    AutostartManager = prosync.AutostartManager

    with tempfile.TemporaryDirectory(prefix="prosync-xdg-") as tmp_dir:
        xdg_home = Path(tmp_dir) / ".config"
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg_home)}), mock.patch.object(
            sys, "platform", "linux"
        ):
            assert AutostartManager.is_autostart_enabled() is False

            success = AutostartManager.set_autostart(True)
            assert success is True

            desktop_file = xdg_home / "autostart" / "prosync.desktop"
            assert desktop_file.exists() is True

            content = desktop_file.read_text(encoding="utf-8")
            assert "[Desktop Entry]" in content
            assert "Type=Application" in content
            assert "Name=ProSync" in content
            assert "Exec=" in content
            assert "Icon=prosync" in content
            assert "StartupWMClass=ProSync" in content
            assert "X-GNOME-Autostart-enabled=true" in content

            assert AutostartManager.is_autostart_enabled() is True


def test_linux_autostart_disable_removes_desktop_file() -> None:
    """AutostartManager.set_autostart(False) removes XDG autostart .desktop file on Linux."""
    prosync = _load_prosync_module()
    AutostartManager = prosync.AutostartManager

    with tempfile.TemporaryDirectory(prefix="prosync-xdg-") as tmp_dir:
        xdg_home = Path(tmp_dir) / ".config"
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg_home)}), mock.patch.object(
            sys, "platform", "linux"
        ):
            AutostartManager.set_autostart(True)
            assert AutostartManager.is_autostart_enabled() is True

            success = AutostartManager.set_autostart(False)
            assert success is True

            desktop_file = xdg_home / "autostart" / "prosync.desktop"
            assert desktop_file.exists() is False
            assert AutostartManager.is_autostart_enabled() is False


def test_linux_autostart_honors_disabled_flag_in_content() -> None:
    """AutostartManager.is_autostart_enabled() returns False when X-GNOME-Autostart-enabled=false."""
    prosync = _load_prosync_module()
    AutostartManager = prosync.AutostartManager

    with tempfile.TemporaryDirectory(prefix="prosync-xdg-") as tmp_dir:
        xdg_home = Path(tmp_dir) / ".config"
        desktop_dir = xdg_home / "autostart"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        desktop_file = desktop_dir / "prosync.desktop"
        desktop_file.write_text(
            "[Desktop Entry]\nType=Application\nName=ProSync\nX-GNOME-Autostart-enabled=false\n",
            encoding="utf-8",
        )

        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg_home)}), mock.patch.object(
            sys, "platform", "linux"
        ):
            assert AutostartManager.is_autostart_enabled() is False


def test_linux_autostart_fallback_to_home_config() -> None:
    """AutostartManager uses ~/.config when XDG_CONFIG_HOME is empty."""
    prosync = _load_prosync_module()
    AutostartManager = prosync.AutostartManager

    with tempfile.TemporaryDirectory(prefix="prosync-home-") as tmp_dir:
        fake_home = Path(tmp_dir)
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": ""}), mock.patch(
            "os.path.expanduser", return_value=str(fake_home / ".config")
        ), mock.patch.object(sys, "platform", "linux"):
            p = AutostartManager._linux_autostart_path()
            expected = os.path.join(str(fake_home / ".config"), "autostart", "prosync.desktop")
            assert p == expected


def test_packaging_linux_desktop_file_contract() -> None:
    """Verify packaging/linux/prosync.desktop file conforms to XDG Desktop Entry Spec."""
    desktop_file = PROJECT_ROOT / "packaging" / "linux" / "prosync.desktop"
    assert desktop_file.exists() is True

    content = desktop_file.read_text(encoding="utf-8")
    assert "[Desktop Entry]" in content
    assert "Type=Application" in content
    assert "Name=ProSync" in content
    assert "Exec=prosync" in content
    assert "Icon=prosync" in content
    assert "Terminal=false" in content
    assert "Categories=Utility;FileTools;Qt;" in content
    assert "StartupWMClass=ProSync" in content


def test_packaging_linux_readme_exists() -> None:
    """Verify packaging/linux/README.md documentation exists."""
    readme_file = PROJECT_ROOT / "packaging" / "linux" / "README.md"
    assert readme_file.exists() is True
    assert "prosync.desktop" in readme_file.read_text(encoding="utf-8")
