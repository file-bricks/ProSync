"""
manage_translations.py - Multi-Language Translation Manager & CI Gate
======================================================================
Policy P-006: Tier-2 Multi-Language Standard (DE, EN, ES, ZH, JA, RU)

Verwendung:
    python manage_translations.py [--check] [--dir PROJEKTVERZEICHNIS]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

SUPPORTED_LANGUAGES = ("de", "en", "es", "zh", "ja", "ru")
TRANSLATION_FILE = "locales/translations.json"

STRING_PATTERNS = [
    re.compile(r'text\s*=\s*"([^"]+)"'),
    re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'addAction\s*\([^,]*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setToolTip\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setPlaceholderText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
]

GERMAN_HINTS = [
    "datei", "filter", "fehler", "laden", "speichern",
    "ansicht", "optionen", "zurueck", "anzeigen", "export",
    "import", "einstellungen", "abbrechen", "hilfe", "bearbeiten",
    "oeffnen", "schliessen", "start", "aktualisieren",
    "pruefen", "sicherheit", "datenbank", "aufgabe", "ordner", "ueber",
]


def is_german(text: str) -> bool:
    if any(ch in text for ch in "äöüÄÖÜß"):
        return True
    text_lower = text.lower()
    return any(w in text_lower for w in GERMAN_HINTS)


def find_german_strings(source_dir: str) -> set:
    german_strings = set()
    skip_dirs = {"build", "dist", "venv", ".venv", "__pycache__", "releases", "scratch"}

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py") and not file.startswith("test_") and file != "run_tests.py":
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    continue
                for pattern in STRING_PATTERNS:
                    for match in pattern.findall(content):
                        if is_german(match):
                            german_strings.add(match.strip())
    return german_strings


def check_translations(source_dir: str = ".") -> int:
    """CI Check: Überprüft Vollständigkeit aller 6 Zielsprachen in translations.json."""
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)
    if not os.path.exists(trans_file):
        print(f"[FAIL] Übersetzungsdatei {trans_file} existiert nicht!")
        return 1

    try:
        with open(trans_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except Exception as e:
        print(f"[FAIL] Fehler beim Parsen von {trans_file}: {e}")
        return 1

    total_keys = 0
    missing_by_lang = {lang: [] for lang in SUPPORTED_LANGUAGES}

    for key, val in translations.items():
        if key.startswith("_"):
            continue
        total_keys += 1
        if not isinstance(val, dict):
            for lang in SUPPORTED_LANGUAGES:
                missing_by_lang[lang].append(key)
            continue
        for lang in SUPPORTED_LANGUAGES:
            target_val = val.get(lang)
            if not target_val or not str(target_val).strip():
                missing_by_lang[lang].append(key)

    has_error = False
    for lang, missing in missing_by_lang.items():
        if missing:
            has_error = True
            print(f"[!] {len(missing)}/{total_keys} fehlende Übersetzungen für Sprache '{lang}':")
            for k in missing[:5]:
                print(f"    - {k}")
            if len(missing) > 5:
                print(f"    ... und {len(missing) - 5} weitere")

    if has_error:
        print("\n[FAIL] Übersetzungsprüfung fehlgeschlagen. Nicht alle Schlüssel vollständig übersetzt.")
        return 1

    print(f"[OK] 100% Übersetzungsparität: Alle {total_keys} Schlüssel in allen 6 Sprachen vorhanden ({', '.join(SUPPORTED_LANGUAGES)}).")
    return 0


def manage_translations(source_dir: str = ".") -> None:
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)

    if os.path.exists(trans_file):
        try:
            with open(trans_file, "r", encoding="utf-8") as f:
                translations = json.load(f)
        except (json.JSONDecodeError, OSError):
            translations = {}
    else:
        translations = {}

    found = find_german_strings(source_dir)

    added = []
    for s in sorted(found):
        if s not in translations:
            translations[s] = {lang: (s if lang == "de" else "") for lang in SUPPORTED_LANGUAGES}
            added.append(s)

    os.makedirs(os.path.dirname(trans_file), exist_ok=True)
    tmp_file = trans_file + ".tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(translations, f, indent=2, ensure_ascii=False)
    os.replace(tmp_file, trans_file)

    if added:
        print(f"[+] {len(added)} neue Einträge hinzugefügt:")
        for s in added[:10]:
            print(f"    - {s}")
        if len(added) > 10:
            print(f"    ... und {len(added) - 10} weitere")
    else:
        print("[i] Keine neuen deutschen Strings gefunden.")

    total_keys = len([k for k in translations if not k.startswith("_")])
    print(f"\n[i] Gesamt: {total_keys} Übersetzungsschlüssel in {trans_file}")


def main() -> int:
    parser = argparse.ArgumentParser(description="ProSync Translation Manager (Policy P-006 Tier-2)")
    parser.add_argument("--check", action="store_true", help="Validiert 100% Sprachabdeckung aller 6 Zielsprachen")
    parser.add_argument("--dir", default=".", help="Wurzelverzeichnis des Projekts")
    args, _ = parser.parse_known_args()

    if args.check:
        return check_translations(args.dir)
    manage_translations(args.dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
