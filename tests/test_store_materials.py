from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PySide6.QtGui import QImage


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "_WARTUNG" / "generate_store_screenshots.py"


def _load_screenshot_module():
    spec = importlib.util.spec_from_file_location("prosync_store_materials", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build_demo_config_contains_store_relevant_examples():
    module = _load_screenshot_module()
    config = module.build_demo_config()

    assert "app" in config
    assert len(config["connections"]) == 3
    assert {conn["type"] for conn in config["connections"]} == {"folder", "file"}
    assert any("_portable_import" in conn for conn in config["connections"])


def test_write_manifest_lists_expected_screenshots(tmp_path):
    module = _load_screenshot_module()
    module.write_manifest(tmp_path)

    content = (tmp_path / "README.md").read_text(encoding="utf-8")
    for filename, caption in module.SCREENSHOTS:
        assert filename in content
        assert caption in content


def test_generate_store_assets_creates_expected_sizes(tmp_path):
    module = _load_screenshot_module()
    generated = module.generate_store_assets(tmp_path)

    assert len(generated) == len(module.STORE_ASSETS)
    for filename, width, height in module.STORE_ASSETS:
        image = QImage(str(tmp_path / filename))
        assert not image.isNull()
        assert image.width() == width
        assert image.height() == height


def test_store_package_has_complete_non_placeholder_metadata() -> None:
    config = json.loads((ROOT / "store_package.json").read_text(encoding="utf-8"))

    assert config.get("name") == "ProSync" or config.get("app_name") == "ProSync"
    assert config["publisher"].startswith("CN=")
    assert config["identity_name"] == "Geiger.ProSync"
    assert config["version"] == "3.2.0.0"
    assert config["executable"] == "ProSync.exe"
    assert "runFullTrust" in config["capabilities"]
    assert config["category"] == "Utilities"
    assert config["privacy_url"].startswith("https://")
    assert config["support_url"].startswith("https://")

    values_str = " ".join(str(v) for v in config.values())
    assert "your" not in values_str.lower()
    assert "placeholder" not in values_str.lower()


def test_store_manifest_is_valid_xml_and_has_required_elements() -> None:
    manifest_path = ROOT / "store_package" / "ProSync" / "AppxManifest.xml"
    assert manifest_path.is_file(), "AppxManifest.xml must exist in store_package/ProSync/"

    tree = ET.parse(manifest_path)
    root = tree.getroot()

    assert "foundation/windows10" in root.tag

    identity = root.find("{http://schemas.microsoft.com/appx/manifest/foundation/windows10}Identity")
    assert identity is not None
    assert identity.get("Name") == "Geiger.ProSync"
    assert identity.get("Publisher") == "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
    assert identity.get("Version") == "3.2.0.0"

    manifest_text = manifest_path.read_text(encoding="utf-8")
    assert "runFullTrust" in manifest_text
    assert "ProSync.exe" in manifest_text


def test_store_listing_and_support_are_bilingual_and_privacy_aligned() -> None:
    listing = (ROOT / "STORE_LISTING.md").read_text(encoding="utf-8")
    support = (ROOT / "SUPPORT.md").read_text(encoding="utf-8")

    assert "## Deutsch" in listing
    assert "## English" in listing
    assert "Keine Pflicht-Cloud" in listing or "Lokal zuerst" in listing or "Local first" in listing
    assert "## Deutsch" in support
    assert "## English" in support
    assert "Security" in support or "Sicherheitslücken" in support


def test_store_readiness_reports_repository_staged() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_store_readiness.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "STORE READINESS: METADATA & REPOSITORY STAGED" in result.stdout
    assert "Partner Center reservation" in result.stdout


def test_store_listing_keywords_adhere_to_policy_10_1_3() -> None:
    listing = (ROOT / "STORE_LISTING.md").read_text(encoding="utf-8")

    de_match = re.search(r"### Schlüsselwörter\s*\n+([^\n#]+)", listing)
    assert de_match is not None, "German keywords section missing"
    de_keywords = [k.strip() for k in de_match.group(1).split(",") if k.strip()]
    assert 1 <= len(de_keywords) <= 7, f"German keywords must be 1-7 (found {len(de_keywords)})"

    en_match = re.search(r"### Keywords\s*\n+([^\n#]+)", listing)
    assert en_match is not None, "English keywords section missing"
    en_keywords = [k.strip() for k in en_match.group(1).split(",") if k.strip()]
    assert 1 <= len(en_keywords) <= 7, f"English keywords must be 1-7 (found {len(en_keywords)})"


def test_windows_store_prep_matches_metadata_and_policy() -> None:
    prep_path = ROOT / "WINDOWS_STORE_PREP.md"
    assert prep_path.is_file(), "WINDOWS_STORE_PREP.md must exist"
    prep_text = prep_path.read_text(encoding="utf-8")

    config = json.loads((ROOT / "store_package.json").read_text(encoding="utf-8"))
    assert config["identity_name"] in prep_text
    assert config["publisher"] in prep_text
    assert config["version"] in prep_text
    assert "Policy 10.1.3" in prep_text
    assert "WACK" in prep_text


def test_tile_icons_present_in_all_store_locations() -> None:
    required_icons = (
        "icon_44x44.png",
        "icon_50x50.png",
        "icon_150x150.png",
        "icon_310x150.png",
        "icon_310x310.png",
    )
    for loc in (
        ROOT / "assets" / "icons",
        ROOT / "store_assets",
        ROOT / "store_package" / "ProSync" / "icons",
    ):
        assert loc.is_dir(), f"Icon folder {loc} must exist"
        for icon_name in required_icons:
            icon_file = loc / icon_name
            assert icon_file.is_file(), f"Icon {icon_name} missing in {loc}"
            assert icon_file.stat().st_size > 0, f"Icon {icon_name} in {loc} is empty"


def test_german_umlaut_integrity_in_store_materials() -> None:
    listing = (ROOT / "STORE_LISTING.md").read_text(encoding="utf-8")
    prep = (ROOT / "WINDOWS_STORE_PREP.md").read_text(encoding="utf-8")
    pkg = (ROOT / "store_package.json").read_text(encoding="utf-8")

    # Ensure real German umlauts are used (ä, ö, ü, ß)
    assert any(c in listing for c in "äöüÄÖÜß")
    assert any(c in prep for c in "äöüÄÖÜß")
    assert any(c in pkg for c in "äöüÄÖÜß")


def main() -> int:
    from tempfile import TemporaryDirectory

    test_build_demo_config_contains_store_relevant_examples()
    with TemporaryDirectory(prefix="prosync-store-test-") as temp_dir:
        temp_path = Path(temp_dir)
        test_write_manifest_lists_expected_screenshots(temp_path / "manifest")
        test_generate_store_assets_creates_expected_sizes(temp_path / "assets")
    test_store_package_has_complete_non_placeholder_metadata()
    test_store_manifest_is_valid_xml_and_has_required_elements()
    test_store_listing_and_support_are_bilingual_and_privacy_aligned()
    test_store_readiness_reports_repository_staged()
    test_store_listing_keywords_adhere_to_policy_10_1_3()
    test_windows_store_prep_matches_metadata_and_policy()
    test_tile_icons_present_in_all_store_locations()
    test_german_umlaut_integrity_in_store_materials()
    print("Store-Material-Tests bestanden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
