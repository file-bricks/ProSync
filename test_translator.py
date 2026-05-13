"""
Regression test for TranslationSystem language detection.
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from translator import TranslationSystem


def test_translation_system_only_records_german_strings():
    """English strings must not be treated as German translations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        app_dir = Path(tmpdir)
        translator = TranslationSystem("de", app_dir=app_dir)
        translations_file = app_dir / "locales" / "translations.json"

        assert not translator._is_german("Open")
        assert not translator._is_german("Hello world")
        assert translator._is_german("Datei öffnen")
        assert translator._is_german("Datei oeffnen")

        assert translator.t("Open") == "Open"
        assert "Open" not in translator.translations
        assert not translations_file.exists()

        assert translator.t("Datei öffnen") == "Datei öffnen"
        assert "Datei öffnen" in translator.translations
        assert translations_file.exists()


def main() -> int:
    """Run the regression test as a standalone smoke test."""
    test_translation_system_only_records_german_strings()
    print("PASS: TranslationSystem erkennt nur deutsche Strings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
