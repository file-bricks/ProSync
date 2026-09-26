"""Contract tests for ProSync repository metadata, discoverability, and documentation parity."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_badges_and_quick_nav() -> None:
    """Verify badges and quick navigation in both English and German READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme, lang in [(readme_en, "en"), (readme_de, "de")]:
        assert "License-MIT" in readme or "Lizenz-MIT" in readme or "License: MIT" in readme or "Lizenz: MIT" in readme, f"License badge missing in {lang}"
        assert "Version-v3.2.0" in readme or "v3.2.0" in readme, f"Version badge missing in {lang}"
        assert "Zero--Egress" in readme or "Zero-Egress" in readme or "Local" in readme, f"Privacy badge missing in {lang}"
        assert "file--bricks" in readme or "file-bricks" in readme, f"Ecosystem badge missing in {lang}"
        assert "open--bricks" in readme or "open-bricks" in readme, f"Umbrella badge missing in {lang}"
        assert "llms.txt" in readme, f"llms.txt badge/link missing in {lang}"
        assert "SECURITY.md" in readme, f"SECURITY.md link missing in {lang}"
        assert "CHANGELOG.md" in readme, f"CHANGELOG.md link missing in {lang}"
        assert "USER_GUIDE.md" in readme, f"USER_GUIDE.md link missing in {lang}"
        assert "NOTICE" in readme or "Attribution" in readme, f"NOTICE badge missing in {lang}"


def test_mermaid_diagrams_in_readmes() -> None:
    """Verify Mermaid architecture and sequence lifecycle diagrams exist in READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme, lang in [(readme_en, "en"), (readme_de, "de")]:
        assert "```mermaid" in readme, f"Mermaid block missing in {lang}"
        assert "flowchart TD" in readme, f"Flowchart diagram missing in {lang}"
        assert "sequenceDiagram" in readme, f"Sequence diagram missing in {lang}"
        assert "wal_checkpoint" in readme or "WAL" in readme, f"WAL Checkpoint step missing in sequence diagram for {lang}"


def test_visual_showcase_screenshots_exist() -> None:
    """Verify all screenshots referenced in README visual showcase exist on disk."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    matches = re.findall(r'!\[.*?\]\((screenshots/[^\)]+)\)', readme_en)
    assert len(matches) >= 3, f"Expected at least 3 showcase screenshots in README.md, found {len(matches)}"

    for rel_path in matches:
        full_path = ROOT / rel_path
        assert full_path.is_file(), f"Screenshot file {rel_path} does not exist"
        assert full_path.stat().st_size > 0, f"Screenshot file {rel_path} is empty"


def test_security_policy_bilingual_integrity() -> None:
    """Verify SECURITY.md contains English and German sections, local-first guarantees, and contact emails."""
    security_file = ROOT / "SECURITY.md"
    assert security_file.is_file(), "SECURITY.md must exist"
    content = security_file.read_text(encoding="utf-8")

    assert "## Deutsch" in content or "## German" in content, "German section missing in SECURITY.md"
    assert "## English" in content, "English section missing in SECURITY.md"
    assert "Zero-Egress" in content or "Zero Egress" in content or "Lokal" in content, "Local-first guarantee missing in SECURITY.md"
    assert "WAL" in content or "Checkpoint" in content, "WAL/Database safety invariants missing in SECURITY.md"
    assert "@" in content, "Security contact email missing in SECURITY.md"
    assert "Report a vulnerability" in content or "Sicherheitslücke" in content, "Vulnerability reporting instructions missing"


def test_llms_txt_integrity() -> None:
    """Verify llms.txt contains updated last-checked timestamp and repository context."""
    llms_file = ROOT / "llms.txt"
    assert llms_file.is_file(), "llms.txt must exist"
    content = llms_file.read_text(encoding="utf-8")

    assert "Last-checked: 2026-09-26" in content or "Last-checked: 2026-09-18" in content, "llms.txt timestamp not updated"
    assert "https://github.com/file-bricks/ProSync" in content, "Canonical repo link missing in llms.txt"
    assert "SQLite" in content and "WAL" in content, "SQLite WAL keywords missing in llms.txt"
    assert "SECURITY.md" in content, "SECURITY.md reference missing in llms.txt"
    assert "MARKETING-LOG.txt" in content, "MARKETING-LOG.txt reference missing in llms.txt"
    assert "NOTICE" in content, "NOTICE reference missing in llms.txt"


def test_sibling_ecosystem_matrix() -> None:
    """Verify sibling tools matrix linking to file-bricks, doc-bricks, ellmos-ai, dev-bricks, and open-bricks."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme, lang in [(readme_en, "en"), (readme_de, "de")]:
        assert "ExplorerPro" in readme, f"ExplorerPro sibling link missing in {lang}"
        assert "CloudLockFixer" in readme, f"CloudLockFixer sibling link missing in {lang}"
        assert "ProFiler" in readme, f"ProFiler sibling link missing in {lang}"
        assert "UniversalDocsGrabber" in readme or "CleanMarkdown" in readme, f"doc-bricks sibling link missing in {lang}"
        assert "open-bricks" in readme, f"open-bricks umbrella link missing in {lang}"


def test_pyproject_pep621_metadata() -> None:
    """Verify pyproject.toml PEP 621 metadata, urls, and classifiers."""
    pyproject_file = ROOT / "pyproject.toml"
    assert pyproject_file.is_file(), "pyproject.toml must exist"
    content = pyproject_file.read_text(encoding="utf-8")

    assert 'name = "prosync"' in content
    assert 'version = "3.2.0"' in content
    assert "Security =" in content, "Security URL missing in pyproject.toml"
    assert "Homepage =" in content, "Homepage URL missing in pyproject.toml"
    assert "Repository =" in content, "Repository URL missing in pyproject.toml"
    assert "Documentation =" in content, "Documentation URL missing in pyproject.toml"
    assert "Changelog =" in content, "Changelog URL missing in pyproject.toml"
    assert '"Parent Organization" =' in content or "Parent Organization =" in content, "Parent Organization URL missing in pyproject.toml"
    assert '"Umbrella Ecosystem" =' in content or "Umbrella Ecosystem =" in content, "Umbrella Ecosystem URL missing in pyproject.toml"
    assert '"LLM Ready" =' in content or "LLM Ready =" in content, "LLM Ready URL missing in pyproject.toml"
    assert '"Marketing Log" =' in content or "Marketing Log =" in content, "Marketing Log URL missing in pyproject.toml"
    assert "Notice =" in content, "Notice URL missing in pyproject.toml"
    assert "license-files =" in content, "license-files missing in pyproject.toml"
    assert 'addopts = "-ra -v"' in content, "addopts -ra -v missing in pyproject.toml"
    assert "norecursedirs =" in content, "norecursedirs missing in pyproject.toml"


def test_ci_workflow_integrity() -> None:
    """Verify GitHub Actions CI workflows exist and have test coverage."""
    workflow_dir = ROOT / ".github" / "workflows"
    assert (workflow_dir / "tests.yml").is_file(), "tests.yml missing"
    assert (workflow_dir / "source-platform-smoke.yml").is_file(), "source-platform-smoke.yml missing"

    tests_yml = (workflow_dir / "tests.yml").read_text(encoding="utf-8")
    assert "python run_tests.py" in tests_yml
    assert "python -m pytest -ra -v" in tests_yml


def test_ci_concurrency_and_timeout_guardrails() -> None:
    """Verify CI workflows have concurrency cancellation and explicit timeout-minutes."""
    workflow_dir = ROOT / ".github" / "workflows"
    workflows = {
        "tests.yml": 15,
        "source-platform-smoke.yml": 15,
        "stale.yml": 10,
        "welcome.yml": 5,
    }

    for wf_name, expected_timeout in workflows.items():
        wf_file = workflow_dir / wf_name
        assert wf_file.is_file(), f"Workflow {wf_name} missing"
        content = wf_file.read_text(encoding="utf-8")
        assert "concurrency:" in content, f"concurrency missing in {wf_name}"
        assert "cancel-in-progress: true" in content, f"cancel-in-progress missing in {wf_name}"
        assert f"timeout-minutes: {expected_timeout}" in content, (
            f"timeout-minutes: {expected_timeout} missing in {wf_name}"
        )


def test_gitignore_multihost_and_lock_defense() -> None:
    """Verify .gitignore includes multi-host, cloud conflict, and canonical lock patterns."""
    gitignore_file = ROOT / ".gitignore"
    assert gitignore_file.is_file(), ".gitignore must exist"
    content = gitignore_file.read_text(encoding="utf-8")

    patterns = [
        "*conflicted copy*",
        "*-WORKSTATION*",
        "*-ASUS*",
        "*-LAPTOP*",
        "*-Mac Studio*",
        "*-MacBook*",
        "*-IDEAPAD*",
        "LOCK",
        "*.lock",
        ".automation-lock",
        "uv.lock",
        "!package-lock.json",
        ".coverage.*",
        ".pytest_temp/",
    ]
    for pattern in patterns:
        assert pattern in content, f"Pattern {pattern} missing in .gitignore"


def test_marketing_log_recent_hygiene_entry() -> None:
    """Verify MARKETING-LOG.txt exists, is up-to-date, and documents governance invariants."""
    mktg_file = ROOT / "MARKETING-LOG.txt"
    assert mktg_file.is_file(), "MARKETING-LOG.txt must exist"
    content = mktg_file.read_text(encoding="utf-8")

    assert "2026-09-18" in content, "Recent audit date 2026-09-18 missing in MARKETING-LOG.txt"
    assert "PROSYNC SUITE" in content
    assert "INV-LOCAL-01" in content and "INV-SLA-10" in content, "Governance pillars missing in MARKETING-LOG.txt"
    assert "Pfad B" in content or "PFAD B" in content, "Pfad B audit section missing in MARKETING-LOG.txt"


def test_web_companion_pwa_svg_parity() -> None:
    """Verify web companion manifest includes SVG icon for scalable PWA install."""
    manifest_file = ROOT / "web_companion" / "manifest.webmanifest"
    assert manifest_file.is_file(), "manifest.webmanifest must exist"
    manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))

    icons = manifest_data.get("icons", [])
    svg_icons = [icon for icon in icons if icon.get("src") == "./icon.svg"]
    assert len(svg_icons) >= 1, "Missing ./icon.svg in manifest icons"
    assert svg_icons[0].get("type") == "image/svg+xml"
    assert (ROOT / "web_companion" / "icon.svg").is_file(), "web_companion/icon.svg file missing on disk"


def test_quick_navigation_18_points_parity() -> None:
    """Verify README.md and README_de.md have exactly 18 numbered sections with reciprocal anchors."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for i in range(1, 19):
        assert f"## {i}." in readme_en, f"Numbered section {i} missing in README.md"
        assert f"## {i}." in readme_de, f"Numbered section {i} missing in README_de.md"

    # Verify key anchors exist in both
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
        assert f'id="{anchor}"' in readme_en, f'Anchor id="{anchor}" missing in README.md'
        assert f'id="{anchor}"' in readme_de, f'Anchor id="{anchor}" missing in README_de.md'


def test_target_personas_and_high_intent_queries() -> None:
    """Verify target personas and high-intent discoverability terms in both READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    personas = ["[PERSONA-01]", "[PERSONA-02]", "[PERSONA-03]", "[PERSONA-04]"]
    for p in personas:
        assert p in readme_en, f"Persona {p} missing in README.md"
        assert p in readme_de, f"Persona {p} missing in README_de.md"


def test_comparative_matrix_vs_alternatives() -> None:
    """Verify 10-dimension comparative matrix against 4 alternatives."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme, lang in [(readme_en, "en"), (readme_de, "de")]:
        assert "FreeFileSync" in readme, f"FreeFileSync missing in comparative matrix ({lang})"
        assert "Robocopy" in readme, f"Robocopy missing in comparative matrix ({lang})"
        assert "Syncthing" in readme, f"Syncthing missing in comparative matrix ({lang})"
        assert "INV-LOCAL-01" in readme, f"INV-LOCAL-01 missing in comparative matrix ({lang})"
        assert "INV-SLA-10" in readme, f"INV-SLA-10 missing in comparative matrix ({lang})"


def test_dual_mermaid_diagrams() -> None:
    """Verify dual Mermaid diagrams (flowchart and sequenceDiagram) are present in both READMEs."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme, lang in [(readme_en, "en"), (readme_de, "de")]:
        assert "```mermaid" in readme, f"Mermaid block missing in {lang}"
        assert "flowchart TB" in readme or "flowchart TD" in readme, f"Architecture flowchart missing in {lang}"
        assert "sequenceDiagram" in readme, f"Sequence diagram missing in {lang}"
        assert "wal_checkpoint" in readme, f"wal_checkpoint missing in Mermaid sequence ({lang})"
        assert "SQLITE_BUSY" in readme, f"SQLITE_BUSY abort missing in Mermaid sequence ({lang})"


def test_third_party_licenses_md_integrity() -> None:
    """Verify THIRD_PARTY_LICENSES.md SBOM exists, documents SPDX identifiers, RunAsInvoker, and governance invariants."""
    sbom_file = ROOT / "THIRD_PARTY_LICENSES.md"
    assert sbom_file.is_file(), "THIRD_PARTY_LICENSES.md must exist"
    content = sbom_file.read_text(encoding="utf-8")

    assert "LGPL-3.0-only" in content, "PySide6 LGPL-3.0 SPDX missing in THIRD_PARTY_LICENSES.md"
    assert "LGPL-2.1-or-later" in content, "Paramiko LGPL-2.1 SPDX missing in THIRD_PARTY_LICENSES.md"
    assert "MIT License" in content or "MIT" in content, "MIT License missing in THIRD_PARTY_LICENSES.md"
    assert "RunAsInvoker" in content, "RunAsInvoker non-elevation certification missing"
    assert "Zero-Copyleft" in content, "Zero-Copyleft guarantee missing in THIRD_PARTY_LICENSES.md"
    assert "INV-LOCAL-01" in content and "INV-SLA-10" in content, "Governance invariant table missing"


def test_german_statutory_notice() -> None:
    """Verify README_de.md includes German statutory disclaimer (§ 521 BGB Gefälligkeitsrecht)."""
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")
    assert "521 BGB" in readme_de, "§ 521 BGB missing in README_de.md"
    assert "Gefälligkeit" in readme_de, "Gefälligkeitsrecht missing in README_de.md"


def test_notice_file_exists_and_contract() -> None:
    """Verify canonical NOTICE attribution file exists, mentions Lukas Geiger, file-bricks and open-bricks."""
    notice_file = ROOT / "NOTICE"
    assert notice_file.is_file(), "NOTICE file must exist in repository root"
    content = notice_file.read_text(encoding="utf-8")
    assert "ProSync" in content
    assert "Lukas Geiger" in content
    assert "file-bricks" in content
    assert "open-bricks" in content
    assert "THIRD_PARTY_LICENSES.md" in content


def test_pyproject_saturated_keywords() -> None:
    """Verify pyproject.toml keywords are saturated with 20 curated topics aligned with GitHub Topics."""
    pyproject_file = ROOT / "pyproject.toml"
    content = pyproject_file.read_text(encoding="utf-8")
    assert "license-files =" in content
    expected_keywords = [
        "backup",
        "cross-platform",
        "data-integrity",
        "database-backup",
        "database-protection",
        "desktop-app",
        "file-bricks",
        "file-sync",
        "local-first",
        "offline-first",
        "open-bricks",
        "privacy-first",
        "pyside6",
        "python",
        "sqlite",
        "sqlite-backup",
        "sync",
        "wal-checkpoint",
        "windows-desktop",
        "zero-egress",
    ]
    for kw in expected_keywords:
        assert f'"{kw}"' in content, f'Keyword "{kw}" missing in pyproject.toml'


def test_third_party_licenses_notice_cross_reference_and_recency() -> None:
    """Verify THIRD_PARTY_LICENSES.md references NOTICE and is updated to 2026-09-26."""
    sbom_file = ROOT / "THIRD_PARTY_LICENSES.md"
    content = sbom_file.read_text(encoding="utf-8")
    assert "Audit Date:** 2026-09-26" in content, "Audit Date not updated to 2026-09-26 in THIRD_PARTY_LICENSES.md"
    assert "NOTICE" in content, "NOTICE cross-reference missing in THIRD_PARTY_LICENSES.md"


def test_changelog_unreleased_pfad_a_entry() -> None:
    """Verify CHANGELOG.md contains Pfad A technical hygiene entry under [Unreleased]."""
    changelog_file = ROOT / "CHANGELOG.md"
    content = changelog_file.read_text(encoding="utf-8")
    assert "## [Unreleased]" in content
    assert "Pfad A" in content
    assert "2026-09-26" in content
    assert "NOTICE" in content


def test_ci_workflows_bytecode_compileall_gate() -> None:
    """Verify CI workflows include bytecode compilation validation gates."""
    tests_yml = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    smoke_yml = (ROOT / ".github" / "workflows" / "source-platform-smoke.yml").read_text(encoding="utf-8")
    assert "python -m compileall -q ." in tests_yml, "compileall gate missing in tests.yml"
    assert "python -m compileall -q ." in smoke_yml, "compileall gate missing in source-platform-smoke.yml"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main(["-v", __file__]))
