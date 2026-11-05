from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COMPANION_DIR = ROOT / "web_companion"


def test_companion_directory_structure_and_assets() -> None:
    assert COMPANION_DIR.is_dir(), "web_companion directory must exist"
    required_files = [
        "index.html",
        "app.css",
        "app.js",
        "manifest.webmanifest",
        "sw.js",
        "package.json",
        "apple-touch-icon-180.png",
        "icon.svg",
        "icon-192.png",
        "icon-512.png",
        "tests/pwa.test.mjs",
        "tests/library.test.mjs",
        "tests/companion_i18n.test.mjs",
    ]
    for rel_path in required_files:
        p = COMPANION_DIR / rel_path
        assert p.is_file(), f"Missing companion file: {rel_path}"
        assert p.stat().st_size > 0, f"Empty companion file: {rel_path}"


def test_companion_html5_structure_and_meta() -> None:
    html_path = COMPANION_DIR / "index.html"
    content = html_path.read_text(encoding="utf-8")

    assert "<!DOCTYPE html>" in content
    assert '<html lang="de">' in content or '<html lang="de"' in content
    assert '<meta charset="utf-8">' in content or '<meta charset="UTF-8">' in content
    assert 'name="viewport"' in content
    assert "viewport-fit=cover" in content
    assert 'rel="manifest" href="./manifest.webmanifest"' in content or 'rel="manifest"' in content
    assert 'rel="stylesheet" href="./app.css"' in content or 'rel="stylesheet" href="app.css"' in content
    assert 'src="./app.js"' in content or 'src="app.js"' in content


def test_companion_i18n_selector_and_options() -> None:
    html_path = COMPANION_DIR / "index.html"
    content = html_path.read_text(encoding="utf-8")

    assert '<select id="lang-select"' in content or 'id="lang-select"' in content
    for code, label in [
        ("de", "Deutsch"),
        ("en", "English"),
        ("es", "Español"),
        ("zh", "简体中文"),
        ("ja", "日本語"),
        ("ru", "Русский"),
    ]:
        pattern = rf'<option\s+value="{code}"[^>]*>[^<]*{re.escape(label)}'
        assert re.search(pattern, content), f"Option for language '{code}' ({label}) missing in index.html"


def test_companion_data_i18n_attributes() -> None:
    html_path = COMPANION_DIR / "index.html"
    content = html_path.read_text(encoding="utf-8")

    matches = re.findall(r'data-i18n="([^"]+)"', content)
    assert len(matches) >= 10, f"Expected data-i18n attributes in index.html, found {len(matches)}"

    expected_keys = {
        "app_eyebrow",
        "app_title",
        "hero_text",
        "btn_demo",
        "btn_paste",
        "btn_import",
        "btn_reset",
        "heading_connections",
        "connections_desc",
        "heading_reports",
    }
    found_keys = set(matches)
    for expected in expected_keys:
        assert expected in found_keys, f"Expected key '{expected}' missing in index.html data-i18n attributes"


def test_companion_app_js_translations_and_supported_languages() -> None:
    app_js_path = COMPANION_DIR / "app.js"
    content = app_js_path.read_text(encoding="utf-8")

    assert "SUPPORTED_LANGUAGES" in content
    for code in ("de", "en", "es", "zh", "ja", "ru"):
        assert f'"{code}"' in content or f"'{code}'" in content

    assert "function getTranslation(" in content
    assert "function setLanguage(" in content
    assert "function applyTranslations(" in content
    assert "prosync_companion_lang" in content


def test_companion_manifest_validity() -> None:
    manifest_path = COMPANION_DIR / "manifest.webmanifest"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert data["name"] == "ProSync Companion"
    assert data["short_name"] == "ProSync"
    assert data["display"] == "standalone"
    assert data["start_url"] in (".", "./", "index.html", "./index.html")
    assert len(data.get("icons", [])) >= 2


def test_companion_node_tests_pass() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is not installed in the environment")

    res = subprocess.run(
        [node, "--test", "tests/library.test.mjs", "tests/pwa.test.mjs", "tests/companion_i18n.test.mjs"],
        cwd=COMPANION_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, f"Web companion tests failed:\n{res.stdout}\n{res.stderr}"
    assert "pass 35" in res.stdout or "pass" in res.stdout
