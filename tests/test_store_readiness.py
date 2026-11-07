"""Vertragstests für Windows Store Metadaten, Assets und WACK-Readiness von ProSync."""

from __future__ import annotations

import json
import struct
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PUBLISHER = "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
EXPECTED_IDENTITY = "Geiger.ProSync"
EXPECTED_LANGUAGES = ["de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"]
BANNED_TRADEMARKS = {"windows", "microsoft", "google", "apple", "adobe", "pycharm", "vscode"}


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a valid PNG")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


class TestStoreReadiness(unittest.TestCase):

    def test_store_package_json_exists_and_is_valid(self):
        pkg_path = PROJECT_ROOT / "store_package.json"
        self.assertTrue(pkg_path.exists(), "store_package.json fehlt")
        data = json.loads(pkg_path.read_text(encoding="utf-8"))

        required_fields = [
            "app_name",
            "publisher",
            "publisher_display",
            "identity_name",
            "version",
            "description",
            "executable",
            "capabilities",
            "category",
            "age_rating",
            "privacy_url",
            "support_url",
            "license",
            "languages",
        ]
        for field in required_fields:
            self.assertIn(field, data, f"Pflichtfeld '{field}' fehlt in store_package.json")

        self.assertEqual(data["publisher"], EXPECTED_PUBLISHER)
        self.assertEqual(data["identity_name"], EXPECTED_IDENTITY)
        self.assertEqual(data["languages"], EXPECTED_LANGUAGES)

    def test_full_store_readiness_check_passes(self):
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "check_store_readiness.py")],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, f"check_store_readiness.py fehlgeschlagen:\n{result.stdout}\n{result.stderr}")
        self.assertIn("STORE READINESS: METADATA & REPOSITORY STAGED", result.stdout)

    def test_run_windows_wack_preflight_passes(self):
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "run_windows_wack.py"), "--json"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, f"run_windows_wack.py fehlgeschlagen:\n{result.stdout}\n{result.stderr}")
        summary = json.loads(result.stdout)
        self.assertEqual(summary["overall_result"], "PASS")
        self.assertEqual(summary["fail_count"], 0)
        self.assertGreaterEqual(summary["pass_count"], 10)
        self.assertTrue(Path(summary["report"]).is_file())

    def test_required_documents_exist(self):
        for doc in (
            "PRIVACY_POLICY.md",
            "SUPPORT.md",
            "STORE_LISTING.md",
            "WINDOWS_STORE_PREP.md",
            "PORTIERUNGSPLAN.md",
            "THIRD_PARTY_LICENSES.txt",
        ):
            p = PROJECT_ROOT / doc
            self.assertTrue(p.is_file(), f"Dokument {doc} fehlt")
            self.assertGreater(p.stat().st_size, 50, f"Dokument {doc} ist zu klein")

    def test_store_icons_match_specification(self):
        expected_sizes = {
            "icon_44x44.png": (44, 44),
            "icon_50x50.png": (50, 50),
            "icon_150x150.png": (150, 150),
            "icon_310x150.png": (310, 150),
            "icon_310x310.png": (310, 310),
            "StoreLogo.png": (50, 50),
        }
        icons_dir = PROJECT_ROOT / "store_package" / "ProSync" / "icons"
        for name, size in expected_sizes.items():
            f = icons_dir / name
            self.assertTrue(f.is_file(), f"Icon {name} fehlt in {icons_dir}")
            self.assertEqual(_png_size(f), size, f"Icon {name} hat falsche Dimension")

    def test_keywords_policy_10_1_3(self):
        data = json.loads((PROJECT_ROOT / "store_package.json").read_text(encoding="utf-8"))
        for code in ("de", "en", "es", "zh", "ja", "ru"):
            key = f"keywords_{code}"
            self.assertIn(key, data, f"Fehlender Key {key}")
            kws = data[key]
            self.assertEqual(len(kws), 7, f"Genau 7 Keywords erwartet für {key}")
            for kw in kws:
                self.assertLessEqual(len(kw), 30, f"Keyword '{kw}' in {key} zu lang (>30)")
                for banned in BANNED_TRADEMARKS:
                    self.assertNotIn(banned, kw.lower(), f"Unzulässige Marke '{banned}' in '{kw}'")

    def test_descriptions_length(self):
        data = json.loads((PROJECT_ROOT / "store_package.json").read_text(encoding="utf-8"))
        for code in ("de", "en", "es", "zh", "ja", "ru"):
            key = f"description_{code}"
            self.assertIn(key, data, f"Fehlende Beschreibung {key}")
            desc = data[key]
            self.assertLessEqual(len(desc), 100, f"Beschreibung {key} überschreitet 100 Zeichen ({len(desc)})")
            self.assertGreater(len(desc), 5, f"Beschreibung {key} ist zu kurz")

    def test_store_settings_parity(self):
        pkg = json.loads((PROJECT_ROOT / "store_package.json").read_text(encoding="utf-8"))
        settings = json.loads((PROJECT_ROOT / "releases" / "windowsstore" / "store_settings.json").read_text(encoding="utf-8"))

        self.assertEqual(pkg["identity_name"], settings["identity_name"])
        self.assertEqual(pkg["version"], settings["version"])
        self.assertEqual(pkg["languages"], settings["languages"])
        for code in ("de", "en", "es", "zh", "ja", "ru"):
            self.assertEqual(pkg[f"description_{code}"], settings[f"description_{code}"])
            self.assertEqual(pkg[f"keywords_{code}"], settings[f"keywords_{code}"])

    def test_appx_manifest_structure_and_resources(self):
        manifest_path = PROJECT_ROOT / "store_package" / "ProSync" / "AppxManifest.xml"
        self.assertTrue(manifest_path.is_file(), "AppxManifest.xml fehlt")
        tree = ET.parse(manifest_path)
        root = tree.getroot()

        # Identity
        identity = next((elem for elem in root.iter() if elem.tag.endswith("Identity")), None)
        self.assertIsNotNone(identity)
        self.assertEqual(identity.attrib.get("Name"), EXPECTED_IDENTITY)
        self.assertEqual(identity.attrib.get("Publisher"), EXPECTED_PUBLISHER)
        self.assertEqual(identity.attrib.get("Version"), "3.2.0.0")

        # Capabilities
        caps = [elem.attrib.get("Name") for elem in root.iter() if elem.tag.endswith("Capability")]
        self.assertIn("runFullTrust", caps)

        # Resources
        res_langs = [
            elem.attrib.get("Language", "").lower()
            for elem in root.iter()
            if elem.tag.endswith("Resource") and "Language" in elem.attrib
        ]
        expected_langs = ["de-de", "en-us", "es-es", "zh-cn", "ja-jp", "ru-ru"]
        for el in expected_langs:
            self.assertIn(el, res_langs, f"Sprachressource {el} fehlt im AppxManifest")


if __name__ == "__main__":
    unittest.main()
