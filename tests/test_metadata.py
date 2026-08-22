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

    assert "Last-checked: 2026-08-22" in content, "llms.txt timestamp not updated to 2026-08-22"
    assert "https://github.com/file-bricks/ProSync" in content, "Canonical repo link missing in llms.txt"
    assert "SQLite" in content and "WAL" in content, "SQLite WAL keywords missing in llms.txt"
    assert "SECURITY.md" in content, "SECURITY.md reference missing in llms.txt"


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


def test_ci_workflow_integrity() -> None:
    """Verify GitHub Actions CI workflows exist and have test coverage."""
    workflow_dir = ROOT / ".github" / "workflows"
    assert (workflow_dir / "tests.yml").is_file(), "tests.yml missing"
    assert (workflow_dir / "source-platform-smoke.yml").is_file(), "source-platform-smoke.yml missing"

    tests_yml = (workflow_dir / "tests.yml").read_text(encoding="utf-8")
    assert "python run_tests.py" in tests_yml
    assert "python -m pytest -q" in tests_yml


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main(["-v", __file__]))
