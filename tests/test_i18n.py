"""Contract tests for ProSync Multi-Language Internationalization (Policy P-006 Tier-2)."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import translator
from translator import (
    TranslationSystem,
    get_translator,
    t,
    set_language,
    get_language,
    get_supported_languages,
    get_language_names,
    get_language_display_names,
)


def test_supported_languages_list():
    """Verify Policy P-006 Tier-2 supported languages: DE, EN, ES, ZH, JA, RU."""
    langs = get_supported_languages()
    assert langs == ["de", "en", "es", "zh", "ja", "ru"]
    assert TranslationSystem.FALLBACK_LANGUAGES == ("en", "de")


def test_language_names_and_display_mappings():
    """Verify all 6 languages have native and display mappings."""
    names = get_language_names()
    display_names = get_language_display_names()

    for code in ("de", "en", "es", "zh", "ja", "ru"):
        assert code in names
        assert code in display_names
        assert len(names[code]) > 0
        assert f"({code})" in display_names[code]


def test_translations_catalog_exists_and_valid():
    """Verify locales/translations.json exists and contains metadata."""
    trans_file = ROOT / "locales" / "translations.json"
    assert trans_file.is_file(), "locales/translations.json must exist"

    with open(trans_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "_meta" in data
    assert "languages" in data["_meta"]
    assert data["_meta"]["languages"] == ["de", "en", "es", "zh", "ja", "ru"]


def test_translations_100_percent_parity():
    """Verify 100% parity across all 6 languages with 0 missing translations."""
    trans_file = ROOT / "locales" / "translations.json"
    with open(trans_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    keys = [k for k in data if not k.startswith("_")]
    assert len(keys) >= 50, f"Expected at least 50 translation keys, got {len(keys)}"

    for lang in ("de", "en", "es", "zh", "ja", "ru"):
        for k in keys:
            entry = data[k]
            assert isinstance(entry, dict), f"Entry '{k}' must be a dictionary"
            assert lang in entry, f"Language '{lang}' missing in key '{k}'"
            val = entry[lang]
            assert isinstance(val, str) and val.strip(), f"Translation for '{k}' in '{lang}' cannot be empty"


def test_fallback_chain_hierarchy():
    """Verify deterministic 4-stage fallback: target -> en -> de -> key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        locales_dir = tmp_path / "locales"
        locales_dir.mkdir()
        catalog = {
            "full": {"de": "Voll-DE", "en": "Full-EN", "es": "Lleno-ES", "zh": "全-ZH", "ja": "完全-JA", "ru": "Полный-RU"},
            "missing_es": {"de": "Ersatz-DE", "en": "Fallback-EN", "es": "", "zh": "ZH", "ja": "JA", "ru": "RU"},
            "only_de": {"de": "Nur-DE", "en": "", "es": "", "zh": "", "ja": "", "ru": ""},
            "empty_all": {"de": "", "en": "", "es": "", "zh": "", "ja": "", "ru": ""},
        }
        with open(locales_dir / "translations.json", "w", encoding="utf-8") as f:
            json.dump(catalog, f)

        ts = TranslationSystem(default_lang="es", app_dir=tmp_path)

        # 1. Target language hit
        assert ts.t("full") == "Lleno-ES"

        # 2. Fallback to English
        assert ts.t("missing_es") == "Fallback-EN"

        # 3. Fallback to German
        assert ts.t("only_de") == "Nur-DE"

        # 4. Fallback to key
        assert ts.t("empty_all") == "empty_all"
        assert ts.t("unknown_key_xyz") == "unknown_key_xyz"


def test_singleton_and_convenience_api():
    """Verify singleton get_translator(), t(), and set_language()."""
    ts = get_translator()
    assert ts is not None

    set_language("de")
    assert get_language() == "de"
    assert t("Bereit") == "Bereit"

    set_language("en")
    assert get_language() == "en"
    assert t("Bereit") == "Ready"

    set_language("es")
    assert get_language() == "es"
    assert t("Bereit") == "Listo"

    set_language("zh")
    assert get_language() == "zh"
    assert t("Bereit") == "就绪"

    set_language("ja")
    assert get_language() == "ja"
    assert t("Bereit") == "準備完了"

    set_language("ru")
    assert get_language() == "ru"
    assert t("Bereit") == "Готово"

    # Reset back to German
    set_language("de")
    assert get_language() == "de"


def test_manage_translations_check_cli():
    """Verify manage_translations.py --check exits 0 on full catalog parity."""
    res = subprocess.run(
        [sys.executable, str(ROOT / "manage_translations.py"), "--check", "--dir", str(ROOT)],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"manage_translations.py --check failed: {res.stderr}\n{res.stdout}"
    assert "100%" in res.stdout


def test_readme_es_18_points_and_anchors_parity():
    """Verify README.es.md exists and has 18 numbered sections matching EN and DE."""
    readme_es = (ROOT / "README.es.md").read_text(encoding="utf-8")

    for i in range(1, 19):
        assert f"## {i}." in readme_es, f"Numbered section {i} missing in README.es.md"

    key_anchors = [
        "1-features", "features",
        "2-architecture", "architecture",
        "3-target-personas--discoverability", "target-personas",
        "4-comparative-matrix-vs-alternatives", "comparative-matrix",
        "5-dual-mermaid-diagrams", "dual-mermaid-diagrams",
        "6-governance--runtime-invariants", "governance--runtime-invariants",
        "7-synchronization-modes", "synchronization-modes",
        "8-sqlite-wal-database-protection", "database-protection-v32",
        "9-visual-showcase--feature-gallery", "visual-showcase",
        "10-installation--dependencies", "installation",
        "11-cli--headless-automation", "headless-cli",
        "12-scheduled-backups--iana-timezones", "scheduled-backups",
        "13-portable-webpwa-companion", "webpwa-companion",
        "14-prosyncreader--profiler-search", "prosyncreader--profiler-companion",
        "15-windows-store--msix-staging", "windows-build",
        "16-testing--quality-checks", "quality-checks",
        "17-third-party-licenses--transparency", "license",
        "18-security-policy--sibling-ecosystem", "sibling-tools",
    ]
    for anchor in key_anchors:
        assert f'id="{anchor}"' in readme_es, f'Anchor id="{anchor}" missing in README.es.md'


def test_readme_es_personas_matrix_and_mermaid():
    """Verify personas, comparative matrix, and dual Mermaid diagrams in README.es.md."""
    readme_es = (ROOT / "README.es.md").read_text(encoding="utf-8")

    for p in ["[PERSONA-01]", "[PERSONA-02]", "[PERSONA-03]", "[PERSONA-04]"]:
        assert p in readme_es, f"Persona {p} missing in README.es.md"

    for term in ["FreeFileSync", "Robocopy", "Syncthing", "INV-LOCAL-01", "INV-SLA-10"]:
        assert term in readme_es, f"Term {term} missing in README.es.md"

    assert "```mermaid" in readme_es
    assert "flowchart TD" in readme_es or "flowchart TB" in readme_es
    assert "sequenceDiagram" in readme_es
    assert "wal_checkpoint" in readme_es
    assert "SQLITE_BUSY" in readme_es


def test_trilingual_readme_cross_links():
    """Verify README.md, README_de.md, and README.es.md link to each other."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")
    readme_es = (ROOT / "README.es.md").read_text(encoding="utf-8")

    for text, name in [(readme_en, "README.md"), (readme_de, "README_de.md"), (readme_es, "README.es.md")]:
        assert "[English](README.md)" in text, f"English link missing in {name}"
        assert "[Deutsch](README_de.md)" in text, f"Deutsch link missing in {name}"
        assert "[Español](README.es.md)" in text, f"Español link missing in {name}"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main(["-v", __file__]))


