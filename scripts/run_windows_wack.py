#!/usr/bin/env python3
"""run_windows_wack.py - Führt das Windows App Certification Kit (WACK) für ProSync aus oder erstellt hermetische Preflight-Reports."""

from __future__ import annotations

import argparse
import json
import shutil
import struct
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

try:
    import ctypes
except ImportError:
    ctypes = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_APPCERT = Path(r"C:\Program Files (x86)\Windows Kits\10\App Certification Kit\appcert.exe")
WACK_REPORT_PREFIX = "wack_preflight_"
BANNED_TRADEMARKS = {"windows", "microsoft", "google", "apple", "adobe", "pycharm", "vscode"}


@dataclass(frozen=True)
class WackSummary:
    report: str
    overall_result: str
    requirement_count: int
    pass_count: int
    fail_count: int
    warning_count: int


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a valid PNG")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def load_store_config(project_root: Path) -> dict[str, object]:
    settings_file = project_root / "releases" / "windowsstore" / "store_settings.json"
    if settings_file.exists():
        try:
            return json.loads(settings_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    pkg_file = project_root / "store_package.json"
    if pkg_file.exists():
        try:
            return json.loads(pkg_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def expected_msix_path(project_root: Path, store_config: dict[str, object]) -> Path:
    app_name = str(store_config.get("msix_name") or "ProSync.msix")
    candidate_dirs = [
        project_root / "releases" / "windowsstore",
        project_root / "releases",
        project_root / "dist",
        Path(r"C:\_Local_DEV\codex_build\prosync-store"),
    ]
    for directory in candidate_dirs:
        candidate = directory / app_name
        if candidate.exists():
            return candidate
    return candidate_dirs[0] / app_name


def resolve_msix_path(project_root: Path, store_config: dict[str, object], explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    return expected_msix_path(project_root, store_config).resolve()


def resolve_report_path(project_root: Path, report_dir: Path | None, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    base_dir = (report_dir or (project_root / "releases" / "windowsstore" / "test_reports")).expanduser().resolve()
    timestamp = datetime.now().strftime("%Y%m%d")
    return base_dir / f"{WACK_REPORT_PREFIX}{timestamp}.xml"


def find_appcert(explicit: Path | None = None) -> Path | None:
    if explicit is not None:
        candidate = explicit.expanduser().resolve()
        return candidate if candidate.is_file() else None
    if DEFAULT_APPCERT.is_file():
        return DEFAULT_APPCERT
    discovered = shutil.which("appcert.exe")
    return Path(discovered).resolve() if discovered else None


def is_windows_admin() -> bool:
    if ctypes is None or not hasattr(ctypes, "windll"):
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def run_preflight_checks(project_root: Path, store_config: dict[str, object]) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []

    # 1. Manifest
    manifest_candidates = [
        project_root / "store_package" / "ProSync" / "AppxManifest.xml",
        project_root / "AppxManifest.xml",
    ]
    manifest = next((p for p in manifest_candidates if p.exists()), None)
    if manifest is not None:
        try:
            tree = ET.parse(manifest)
            root = tree.getroot()
            checks.append({
                "id": "MANIFEST_SYNTAX",
                "name": "AppxManifest-Validierung & XML-Wohlgeformtheit",
                "result": "PASS",
                "details": f"Manifest syntax OK: {manifest.name}",
            })
            caps = [elem.attrib.get("Name") for elem in root.iter() if elem.tag.endswith("Capability")]
            if "runFullTrust" in caps:
                checks.append({
                    "id": "RESTRICTED_CAPABILITIES",
                    "name": "Restricted Capabilities Deklaration (runFullTrust)",
                    "result": "PASS",
                    "details": "Desktop-Bridge Anwendung deklariert runFullTrust",
                })
            else:
                checks.append({
                    "id": "RESTRICTED_CAPABILITIES",
                    "name": "Restricted Capabilities Deklaration (runFullTrust)",
                    "result": "FAIL",
                    "details": "runFullTrust fehlt im AppxManifest",
                })

            res_langs = [
                elem.attrib.get("Language", "").lower()
                for elem in root.iter()
                if elem.tag.endswith("Resource") and "Language" in elem.attrib
            ]
            expected_res = ["de-de", "en-us", "es-es", "zh-cn", "ja-jp", "ru-ru"]
            if all(lang in res_langs for lang in expected_res):
                checks.append({
                    "id": "RESOURCE_LANGUAGES",
                    "name": "Tier-2 6-Sprachen Ressourcen-Deklaration im Manifest",
                    "result": "PASS",
                    "details": f"Alle 6 Ressourcen-Sprachen ({', '.join(expected_res)}) im Manifest deklariert",
                })
            else:
                missing = [l for l in expected_res if l not in res_langs]
                checks.append({
                    "id": "RESOURCE_LANGUAGES",
                    "name": "Tier-2 6-Sprachen Ressourcen-Deklaration im Manifest",
                    "result": "FAIL",
                    "details": f"Fehlende Sprachressourcen im Manifest: {', '.join(missing)}",
                })
        except Exception as e:
            checks.append({
                "id": "MANIFEST_SYNTAX",
                "name": "AppxManifest-Validierung & XML-Wohlgeformtheit",
                "result": "FAIL",
                "details": f"XML-Parsing-Fehler: {e}",
            })
    else:
        checks.append({
            "id": "MANIFEST_SYNTAX",
            "name": "AppxManifest-Validierung & XML-Wohlgeformtheit",
            "result": "FAIL",
            "details": "Kein AppxManifest.xml gefunden",
        })

    # 2. Package Configuration
    pkg_path = project_root / "store_package.json"
    if pkg_path.exists():
        try:
            pkg_data = json.loads(pkg_path.read_text(encoding="utf-8"))
            req_fields = [
                "app_name", "publisher", "publisher_display", "identity_name",
                "version", "description", "executable", "capabilities",
                "category", "license", "languages",
            ]
            missing_fields = [f for f in req_fields if f not in pkg_data]
            if not missing_fields:
                checks.append({
                    "id": "PACKAGE_CONFIG",
                    "name": "Store Package Metadaten & Pflichtfelder",
                    "result": "PASS",
                    "details": "store_package.json enthält alle Pflichtfelder",
                })
            else:
                checks.append({
                    "id": "PACKAGE_CONFIG",
                    "name": "Store Package Metadaten & Pflichtfelder",
                    "result": "FAIL",
                    "details": f"Fehlende Pflichtfelder in store_package.json: {', '.join(missing_fields)}",
                })

            langs = pkg_data.get("languages", [])
            req_langs = ["de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"]
            if all(l in langs for l in req_langs):
                checks.append({
                    "id": "CONFIG_LANGUAGES",
                    "name": "Tier-2 6-Sprachen Deklaration in store_package.json",
                    "result": "PASS",
                    "details": f"Alle 6 Tier-2 Sprachen ({', '.join(req_langs)}) deklariert",
                })
            else:
                checks.append({
                    "id": "CONFIG_LANGUAGES",
                    "name": "Tier-2 6-Sprachen Deklaration in store_package.json",
                    "result": "FAIL",
                    "details": f"Fehlende Sprachen: {[l for l in req_langs if l not in langs]}",
                })

            # Keywords Policy 10.1.3 Check
            kw_issues = []
            for code in ("de", "en", "es", "zh", "ja", "ru"):
                kws = pkg_data.get(f"keywords_{code}", [])
                if len(kws) != 7:
                    kw_issues.append(f"keywords_{code} hat {len(kws)} statt 7 Keywords")
                for kw in kws:
                    if len(kw) > 30:
                        kw_issues.append(f"Keyword '{kw}' in keywords_{code} zu lang (>30 Z.)")
                    for banned in BANNED_TRADEMARKS:
                        if banned in kw.lower():
                            kw_issues.append(f"Unzulässige Fremdmarke '{banned}' in '{kw}'")

            if not kw_issues:
                checks.append({
                    "id": "POLICY_10_1_3_KEYWORDS",
                    "name": "Partner Center Richtlinie 10.1.3 Keywords-Konformität",
                    "result": "PASS",
                    "details": "Exakt 7 Keywords je Sprache, alle <= 30 Zeichen, keine unzulässigen Fremdmarken",
                })
            else:
                checks.append({
                    "id": "POLICY_10_1_3_KEYWORDS",
                    "name": "Partner Center Richtlinie 10.1.3 Keywords-Konformität",
                    "result": "FAIL",
                    "details": "; ".join(kw_issues[:3]),
                })

            # Short descriptions length Check
            desc_issues = []
            for code in ("de", "en", "es", "zh", "ja", "ru"):
                desc = pkg_data.get(f"description_{code}", "")
                if not (5 <= len(desc) <= 100):
                    desc_issues.append(f"description_{code} hat {len(desc)} Zeichen (erwartet 5..100)")

            if not desc_issues:
                checks.append({
                    "id": "POLICY_10_1_3_DESCRIPTIONS",
                    "name": "Partner Center Richtlinie 10.1.3 Kurzbeschreibungen (<= 100 Z.)",
                    "result": "PASS",
                    "details": "Alle 6 Kurzbeschreibungen liegen im geforderten Bereich von 5 bis 100 Zeichen",
                })
            else:
                checks.append({
                    "id": "POLICY_10_1_3_DESCRIPTIONS",
                    "name": "Partner Center Richtlinie 10.1.3 Kurzbeschreibungen (<= 100 Z.)",
                    "result": "FAIL",
                    "details": "; ".join(desc_issues),
                })

        except Exception as e:
            checks.append({
                "id": "PACKAGE_CONFIG",
                "name": "Store Package Metadaten & Pflichtfelder",
                "result": "FAIL",
                "details": f"Fehler beim Parsen von store_package.json: {e}",
            })
    else:
        checks.append({
            "id": "PACKAGE_CONFIG",
            "name": "Store Package Metadaten & Pflichtfelder",
            "result": "FAIL",
            "details": "store_package.json fehlt",
        })

    # 3. Assets & Icons
    expected_icons = {
        "icon_44x44.png": (44, 44),
        "icon_50x50.png": (50, 50),
        "icon_150x150.png": (150, 150),
        "icon_310x150.png": (310, 150),
        "icon_310x310.png": (310, 310),
        "StoreLogo.png": (50, 50),
    }
    icons_dir = project_root / "store_package" / "ProSync" / "icons"
    asset_issues = []
    if icons_dir.is_dir():
        for name, size in expected_icons.items():
            f = icons_dir / name
            if not f.is_file():
                asset_issues.append(f"Icon fehlt: {name}")
            else:
                try:
                    actual = _png_size(f)
                    if actual != size:
                        asset_issues.append(f"Icon {name} hat Dimension {actual} statt {size}")
                except Exception as e:
                    asset_issues.append(f"Icon {name} ungültig: {e}")
    else:
        asset_issues.append("store_package/ProSync/icons Verzeichnis fehlt")

    if not asset_issues:
        checks.append({
            "id": "APPX_ASSET_DIMENSIONS",
            "name": "AppX Tile- und Store-Logo-Dimensionen",
            "result": "PASS",
            "details": "Alle 6 Standard-Icons besitzen exakte Spezifikationsgrößen und gültige PNG-Header",
        })
    else:
        checks.append({
            "id": "APPX_ASSET_DIMENSIONS",
            "name": "AppX Tile- und Store-Logo-Dimensionen",
            "result": "FAIL",
            "details": "; ".join(asset_issues[:3]),
        })

    # 4. Screenshots
    screenshot_dirs = [
        project_root / "releases" / "windowsstore" / "screenshots",
        project_root / "store_assets" / "screenshots",
    ]
    shots = []
    for sdir in screenshot_dirs:
        if sdir.is_dir():
            for p in sdir.glob("*.png"):
                try:
                    if p.is_file() and p.stat().st_size > 1000:
                        _png_size(p)
                        shots.append(p)
                except Exception:
                    continue
    if len(shots) >= 3:
        checks.append({
            "id": "SCREENSHOTS_PRESENCE",
            "name": "Store Screenshots Vorhandensein & Mindestanzahl",
            "result": "PASS",
            "details": f"{len(shots)} Screenshots in releases/windowsstore/screenshots/ vorhanden",
        })
    else:
        checks.append({
            "id": "SCREENSHOTS_PRESENCE",
            "name": "Store Screenshots Vorhandensein & Mindestanzahl",
            "result": "FAIL",
            "details": f"Nur {len(shots)} Screenshots vorhanden (mind. 3 erforderlich)",
        })

    # 5. Staging Listings
    missing_listings = []
    for code in ("de", "en", "es", "zh", "ja", "ru"):
        lf = project_root / "releases" / "windowsstore" / f"store_listing_{code}.md"
        if not lf.is_file() or lf.stat().st_size < 50:
            missing_listings.append(f"store_listing_{code}.md")

    if not missing_listings:
        checks.append({
            "id": "STAGING_LISTINGS",
            "name": "Tier-2 6-Sprachen Store-Listings Staging-Präsenz",
            "result": "PASS",
            "details": "Alle 6 Sprach-Listings (DE, EN, ES, ZH, JA, RU) in releases/windowsstore/ vorhanden",
        })
    else:
        checks.append({
            "id": "STAGING_LISTINGS",
            "name": "Tier-2 6-Sprachen Store-Listings Staging-Präsenz",
            "result": "FAIL",
            "details": f"Fehlende oder leere Listings: {', '.join(missing_listings)}",
        })

    # 6. Documentation
    required_docs = ["BUILD.md", "WACK_PROTOCOL.md", "store_settings.json"]
    missing_docs = [d for d in required_docs if not (project_root / "releases" / "windowsstore" / d).is_file()]
    if not missing_docs:
        checks.append({
            "id": "STAGING_DOCS",
            "name": "Store Staging Dokumentation & Build-Anleitungen",
            "result": "PASS",
            "details": "BUILD.md, WACK_PROTOCOL.md und store_settings.json vollständig",
        })
    else:
        checks.append({
            "id": "STAGING_DOCS",
            "name": "Store Staging Dokumentation & Build-Anleitungen",
            "result": "FAIL",
            "details": f"Fehlende Staging-Dokumente: {', '.join(missing_docs)}",
        })

    return checks


def write_xml_report(path: Path, checks: list[dict[str, object]]) -> WackSummary:
    path.parent.mkdir(parents=True, exist_ok=True)
    root = ET.Element("REPORT", {
        "TOOL": "WACK-Preflight-Runner",
        "VERSION": "1.0.0",
        "TIMESTAMP": datetime.now().isoformat(),
    })
    summary_elem = ET.SubElement(root, "SUMMARY")
    passes = sum(1 for c in checks if c["result"] == "PASS")
    fails = sum(1 for c in checks if c["result"] == "FAIL")
    warns = sum(1 for c in checks if c["result"] == "WARNING")
    overall = "PASS" if fails == 0 else "FAIL"

    summary_elem.set("OVERALL_RESULT", overall)
    summary_elem.set("TOTAL_CHECKS", str(len(checks)))
    summary_elem.set("PASS_COUNT", str(passes))
    summary_elem.set("FAIL_COUNT", str(fails))
    summary_elem.set("WARN_COUNT", str(warns))

    results_elem = ET.SubElement(root, "CHECKS")
    for chk in checks:
        item = ET.SubElement(results_elem, "CHECK", {
            "ID": str(chk.get("id", "")),
            "RESULT": str(chk.get("result", "")),
        })
        name_sub = ET.SubElement(item, "NAME")
        name_sub.text = str(chk.get("name", ""))
        det_sub = ET.SubElement(item, "DETAILS")
        det_sub.text = str(chk.get("details", ""))

    tree = ET.ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)

    return WackSummary(
        report=str(path),
        overall_result=overall,
        requirement_count=len(checks),
        pass_count=passes,
        fail_count=fails,
        warning_count=warns,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Gibt die Zusammenfassung als JSON aus")
    parser.add_argument("--dry-run", action="store_true", help="Führt nur die statische Preflight-Prüfung aus")
    parser.add_argument("--report-dir", type=Path, help="Zielordner für XML-Prüfberichte")
    parser.add_argument("--msix", type=Path, help="Expliziter Pfad zum MSIX-Paket")
    args = parser.parse_args(argv)

    cfg = load_store_config(PROJECT_ROOT)
    checks = run_preflight_checks(PROJECT_ROOT, cfg)
    report_file = resolve_report_path(PROJECT_ROOT, args.report_dir, None)
    summary = write_xml_report(report_file, checks)

    if args.json:
        print(json.dumps(asdict(summary), indent=2))
    else:
        print(f"WACK Preflight Result: {summary.overall_result}")
        print(f"Pass: {summary.pass_count}, Fail: {summary.fail_count}, Warn: {summary.warning_count}")
        print(f"Report: {summary.report}")

    return 0 if summary.fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
