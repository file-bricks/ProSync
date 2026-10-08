# Beitragsrichtlinie / Contributing Guide

[English](#english) · [Deutsch](#deutsch)

---

<a id="deutsch"></a>
## Deutsch

Vielen Dank für Ihr Interesse, zu **ProSync** beizutragen! ProSync ist ein intelligentes, lokales Backup- und Datei-Synchronisationswerkzeug mit automatischem SQLite-WAL-Datenbankschutz, entwickelt unter dem Dach von **file-bricks** und **open-bricks**.

### 1. Grundsätze & Architektur-Invarianten

Jeder Beitrag muss die 10 Kern-Invarianten des Projekts wahren:

| Invariante | Bereich | Anforderung |
|---|---|---|
| `INV-LOCAL-01` | Local-First & Zero-Egress | 100% offline; keine Telemetrie, keine externen Cloud-Calls oder Phone-Home-Dienste. |
| `INV-RUNAS-02` | Unprivilegierter Modus | `RunAsInvoker` Non-Elevation; niemals Administratorrechte oder UAC-Elevation anfordern. |
| `INV-WAL-03` | SQLite WAL Crash Safety | Automatisierter Checkpoint `PRAGMA wal_checkpoint(TRUNCATE)`; Fail-Closed bei `SQLITE_BUSY`. |
| `INV-INTEG-04` | Atomare Dateioperationen | Bereitstellung über temporäre Dateien (`.tmp`) vor atomarem Ersetzen; keine korrupten Zieldateien. |
| `INV-SCHED-05` | DST-sichere Zeitplanung | IANA-Zeitzonen ohne Kaskadeneffekte über Sommer-/Winterzeitwechsel hinweg. |
| `INV-PWA-06` | Redigierter Begleiter-Export | `prosync-profile-v1.json` entfernt persönliche Pfade und Zugangsdaten vor dem Export. |
| `INV-PLAT-07` | Plattform-Parität | Standardisierte 8-Punkte Smoke-Suites für Linux und macOS. |
| `INV-STORE-08` | Windows Store / MSIX Staging | Gültiges AppxManifest (`Geiger.ProSync`), Policy 10.1.3 konforme Metadaten und Kachel-Assets. |
| `INV-DOCS-09` | Trilinguale 18-Punkte-Parität | Symmetrische 18 Abschnitte mit dualen Ankern (`sec-01`..`sec-18`) in DE, EN und ES. |
| `INV-SLA-10` | Open-Source-Governance & SLA | MIT-Lizenz, § 521 BGB Gefälligkeitsrecht, verbindliche 48h Security Response SLA. |

### 2. Plan D Local Development Workflow

- **Kanonischer Arbeitsort (Source of Truth):** `C:\_Local_DEV\repos\ProSync` (lokaler Git-Klon). Änderungen, Tests und Commits erfolgen ausschließlich hier, um Cloud-Sync-Konflikte und beschädigte Git-Locks zu verhindern.
- **OneDrive-Spiegel:** Sofern ein OneDrive-Ordner existiert, dient dieser ausschließlich als gitloser Multi-Device-Spiegel (ohne `.git`).

### 3. Version-Freeze-Disziplin (`T-20260920-167562623`)

Die Versionsnummer `3.2.0` in `pyproject.toml`, Quellcode und Manifesten ist **strikt eingefroren**. Es werden keine eigenmächtigen Versions-Bumps vorgenommen. Alle Neuerungen und Fehlerbehebungen werden unter `## [Unreleased]` in `CHANGELOG.md` dokumentiert.

### 4. Code- & Qualitätsrichtlinien

- **Python-Stil:** PEP 8, formatiert und geprüft mit `ruff`.
- **Dateikodierung:** UTF-8 ohne BOM für alle Dateien.
- **Keine Hardcoded-Pfade:** Niemals benutzerspezifische Pfade (wie `C:\Users\...`) im Quellcode hinterlegen.
- **Atomare Writer:** Für Konfigurationen und Reports stets `prosync_utils.atomic_write_json` oder `atomic_write_text` nutzen.
- **Lokale Verifikation:**
  ```bash
  python -m pytest -ra -v
  ruff check .
  python -m compileall -q .
  git diff --check
  ```

### 5. Rechtlicher Rahmen & Haftungsausschluss (§ 521 BGB)

Die Bereitstellung dieser Software erfolgt unentgeltlich im Sinne des deutschen Schenkungs- und Gefälligkeitsrechts nach **§ 521 BGB**. Die Haftung ist auf Vorsatz und grobe Fahrlässigkeit beschränkt.

### 6. Sicherheitsrichtlinie & 48h Response SLA

Sicherheitsrelevante Schwachstellen bitte vertraulich melden an:
- `security@file-bricks.org`
- `security@open-bricks.org`
- `support@lukasgeiger.com`
- `lukas@open-bricks.org`

Wir verpflichten uns zu einer ersten Reaktionszeit innerhalb von **48 Stunden** und einem Triage-Bericht innerhalb von 5 Tagen.

---

<a id="english"></a>
## English

Thank you for your interest in contributing to **ProSync**! ProSync is an intelligent, local backup and folder synchronization utility with automated SQLite WAL database protection, developed under the **file-bricks** and **open-bricks** collectives.

### 1. Foundational Principles & Architecture Invariants

All contributions must strictly respect the project's 10 core invariants:

| Invariant | Domain | Requirement |
|---|---|---|
| `INV-LOCAL-01` | Local-First & Zero Egress | 100% offline; zero telemetry, analytics, or unsolicited network calls. |
| `INV-RUNAS-02` | Unprivileged User Mode | `RunAsInvoker` non-elevation; never request administrative or UAC elevation. |
| `INV-WAL-03` | SQLite WAL Crash Safety | Automated pre-sync checkpoint `PRAGMA wal_checkpoint(TRUNCATE)`; fail-closed on `SQLITE_BUSY`. |
| `INV-INTEG-04` | Atomic File Operations | Temporary file staging (`.tmp`) prior to atomic replacement; no corrupted destinations. |
| `INV-SCHED-05` | DST-Safe Scheduling | IANA timezones without cascading catch-up runs across daylight saving transitions. |
| `INV-PWA-06` | Redacted Companion Export | `prosync-profile-v1.json` scrubs all personal paths, credentials, and tokens. |
| `INV-PLAT-07` | Cross-Platform Parity | Standardized 8-point platform smoke suites for Linux and macOS. |
| `INV-STORE-08` | Windows Store / MSIX Staging | Valid AppxManifest (`Geiger.ProSync`), Policy 10.1.3 compliant metadata and tile assets. |
| `INV-DOCS-09` | Trilingual 18-Point Parity | Symmetrical 18 sections with dual reciprocal anchors (`sec-01`..`sec-18`) in EN, DE, and ES. |
| `INV-SLA-10` | Open Source Governance & SLA | MIT License, § 521 BGB statutory notice, committed 48h security response SLA. |

### 2. Plan D Local Development Workflow

- **Canonical Workspace (Source of Truth):** `C:\_Local_DEV\repos\ProSync` (local git clone). All modifications, tests, and commits must take place here to avoid cloud-sync race conditions and broken git locks.
- **OneDrive Mirror:** If a OneDrive folder exists, it serves purely as a gitless multi-device mirror (without `.git`).

### 3. Version-Freeze Discipline (`T-20260920-167562623`)

Version `3.2.0` in `pyproject.toml`, source code, and application manifests is **strictly frozen**. No unauthorized version bumps are permitted. All enhancements and fixes are documented under `## [Unreleased]` in `CHANGELOG.md`.

### 4. Code & Quality Standards

- **Python Style:** PEP 8 compliance, verified with `ruff`.
- **File Encoding:** UTF-8 without BOM for all files.
- **No Hardcoded Paths:** Never commit user-specific absolute paths (e.g. `C:\Users\...`).
- **Atomic Writers:** Always utilize `prosync_utils.atomic_write_json` or `atomic_write_text` for persistent configs and logs.
- **Local Verification:**
  ```bash
  python -m pytest -ra -v
  ruff check .
  python -m compileall -q .
  git diff --check
  ```

### 5. Statutory Disclaimer (§ 521 BGB)

This software is provided free of charge under German statutory gift and courtesy law (**§ 521 BGB**). Liability is strictly limited to intentional misconduct and gross negligence.

### 6. Security Policy & 48h Response SLA

Please report security vulnerabilities confidentially to:
- `security@file-bricks.org`
- `security@open-bricks.org`
- `support@lukasgeiger.com`
- `lukas@open-bricks.org`

We commit to an initial response within **48 hours** and a triage report within 5 days.
