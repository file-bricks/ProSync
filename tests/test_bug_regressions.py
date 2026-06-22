"""Regressionstests — bugfix-library-transfer 2026-06-21."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
import manage_translations as mt


class TestD1NoQMenuBare(unittest.TestCase):
    """BUG-D1: QMenu() ohne Parent-Argument — GC-Risiko."""

    def _assert_no_bare_qmenu(self, filename):
        src = (ROOT / filename).read_text(encoding="utf-8")
        occurrences = []
        start = 0
        while True:
            idx = src.find("QMenu()", start)
            if idx == -1:
                break
            line_no = src[:idx].count("\n") + 1
            occurrences.append(line_no)
            start = idx + 1
        self.assertEqual(occurrences, [],
                         f"QMenu() ohne Parent in {filename}, Zeilen: {occurrences} — BUG-D1")

    def test_prosyncreader_no_bare_qmenu(self):
        self._assert_no_bare_qmenu("ProSyncReader.py")

    def test_v31_no_bare_qmenu(self):
        self._assert_no_bare_qmenu("ProSyncStart_V3.1.py")

    def test_v31_asusgei_no_bare_qmenu(self):
        self._assert_no_bare_qmenu("ProSyncStart_V3.1-ASUS-GEI.py")


class TestD3RunTestsTimeout(unittest.TestCase):
    """BUG-D3: subprocess.run ohne timeout= — hängt bei fehlschlagendem Testprozess."""

    def test_run_tests_subprocess_has_timeout(self):
        src = (ROOT / "run_tests.py").read_text(encoding="utf-8")
        idx = src.find("subprocess.run")
        self.assertGreater(idx, 0, "subprocess.run in run_tests.py nicht gefunden")
        snippet = src[idx:idx + 200]
        self.assertIn("timeout", snippet,
                      "subprocess.run in run_tests.py ohne timeout= — BUG-D3")


class TestU2ManageTranslations(unittest.TestCase):
    """BUG-U2: manage_translations lud korrupte JSON ohne Handler."""

    def test_corrupted_json_does_not_raise(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trans_file = os.path.join(tmpdir, "locales", "translations.json")
            os.makedirs(os.path.dirname(trans_file), exist_ok=True)
            with open(trans_file, "w", encoding="utf-8") as f:
                f.write("{corrupted json")
            try:
                mt.manage_translations(tmpdir)
            except json.JSONDecodeError:
                self.fail("JSONDecodeError nicht gefangen — BUG-U2 in manage_translations")

    def test_v31_import_profile_json_error_raises_valueerror(self):
        src = (ROOT / "ProSyncStart_V3.1.py").read_text(encoding="utf-8")
        idx = src.find("import_portable_profile")
        self.assertGreater(idx, 0, "import_portable_profile nicht gefunden")
        snippet = src[idx:idx + 400]
        self.assertIn("JSONDecodeError", snippet,
                      "json.load in import_portable_profile ohne JSONDecodeError-Handler — BUG-U2")

    def test_asusgei_import_profile_json_error_raises_valueerror(self):
        src = (ROOT / "ProSyncStart_V3.1-ASUS-GEI.py").read_text(encoding="utf-8")
        idx = src.find("import_portable_profile")
        self.assertGreater(idx, 0, "import_portable_profile nicht gefunden")
        snippet = src[idx:idx + 400]
        self.assertIn("JSONDecodeError", snippet,
                      "json.load in import_portable_profile ohne JSONDecodeError-Handler — BUG-U2")


if __name__ == "__main__":
    unittest.main()
