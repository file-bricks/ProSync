# Third-Party Licenses & Software Inventory

**Project:** `ProSync` (Intelligent Local Backup Synchronization & SQLite WAL Database Protection)<br>
**License:** [MIT License](LICENSE) · [Attribution Notice](NOTICE)<br>
**Audit Date:** 2026-09-26<br>
**Repository:** [file-bricks/ProSync](https://github.com/file-bricks/ProSync)<br>
**Organization:** [file-bricks](https://github.com/file-bricks)<br>
**Umbrella Collective:** [open-bricks](https://github.com/open-bricks)

---

## Runtime Architecture & Dependencies

`ProSync` is an intelligent desktop backup and folder synchronization application built with **Python 3** and **PySide6 (Qt 6)**, accompanied by an offline Web/PWA companion in `web_companion/`. It guarantees unprivileged local-first execution, crash-consistent SQLite WAL checkpoint safety, deterministic file synchronization, and zero external runtime telemetry or cloud dependencies.

### Runtime Dependencies

| Package / Library | Version Constraint | License | SPDX Identifier | Upstream URL | Purpose |
|---|---|---|---|---|---|
| **PySide6** | `>=6.5.0` | LGPL-3.0-only | `LGPL-3.0-only` | [PySide6 on PyPI](https://pypi.org/project/PySide6/) | Official Python Qt6 bindings for GUI, system tray, and cross-platform desktop integration. |
| **shiboken6** | `>=6.5.0` | LGPL-3.0-only | `LGPL-3.0-only` | [shiboken6 on PyPI](https://pypi.org/project/shiboken6/) | C++ binding generator and runtime support library for PySide6. |
| **tzdata** | `>=2025.2` | Apache-2.0 | `Apache-2.0` | [tzdata on PyPI](https://pypi.org/project/tzdata/) | IANA time zone database provider for reliable schedule operations across DST shifts. |
| **paramiko** | `>=3.4.0` | LGPL-2.1-or-later | `LGPL-2.1-or-later` | [paramiko on PyPI](https://pypi.org/project/paramiko/) | SSHv2 and SFTP transport client for remote synchronization targets (hardened against Terrapin GHSA-45x7-px36-x8w8). |
| **bcrypt** | `>=4.0.0` | Apache-2.0 | `Apache-2.0` | [bcrypt on PyPI](https://pypi.org/project/bcrypt/) | Modern password hashing library utilized by paramiko SSH authentication. |
| **cryptography** | `>=42.0.0` | Apache-2.0 OR BSD-3-Clause | `Apache-2.0 OR BSD-3-Clause` | [cryptography on PyPI](https://pypi.org/project/cryptography/) | Cryptographic primitives, ciphers, and key exchange algorithms powering paramiko. |
| **invoke** | `>=2.0.0` | BSD-2-Clause | `BSD-2-Clause` | [invoke on PyPI](https://pypi.org/project/invoke/) | Task execution and command processing utility supporting paramiko. |
| **PyNaCl** | `>=1.5.0` | Apache-2.0 | `Apache-2.0` | [PyNaCl on PyPI](https://pypi.org/project/PyNaCl/) | Python binding to libsodium cryptographic library used by paramiko. |
| **pypdf** | `>=4.0.0` | BSD-3-Clause | `BSD-3-Clause` | [pypdf on PyPI](https://pypi.org/project/pypdf/) | Pure-Python PDF extraction and preview inspection library used by ProSyncReader companion. |

Zero runtime npm packages, external tracking scripts, or cloud analytics brokers are embedded into the desktop application or the offline Web/PWA companion.

---

### Development, Tooling & Packaging Dependencies

The following tools are utilized strictly for local development, code quality enforcement, static analysis, packaging, and CI automation:

| Tool / Framework | Version Floor | License | SPDX Identifier | Project / Organization | Purpose |
|---|---|---|---|---|---|
| **pytest** | `>=9.1.1` | MIT | `MIT` | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) | Automated Python contract and unit testing framework (hardened against CVE-2025-7117). |
| **pluggy** | `>=1.0.0` | MIT | `MIT` | [pytest-dev/pluggy](https://github.com/pytest-dev/pluggy) | Plugin and hook management for pytest. |
| **iniconfig** | `>=2.0.0` | MIT | `MIT` | [pytest-dev/iniconfig](https://github.com/pytest-dev/iniconfig) | Brain-dead simple INI configuration parser for pytest. |
| **ruff** | `>=0.9.0` | MIT OR Apache-2.0 | `MIT OR Apache-2.0` | [astral-sh/ruff](https://github.com/astral-sh/ruff) | High-performance Python linter and code formatter. |
| **pip-licenses** | `>=4.0.0` | MIT | `MIT` | [raimon49/pip-licenses](https://github.com/raimon49/pip-licenses) | License inventory extraction and compliance verification tool. |
| **PyInstaller** | `>=6.10.0` | GPL-2.0-or-later WITH Bootloader-exception | `GPL-2.0-or-later WITH Bootloader-exception` | [pyinstaller/pyinstaller](https://github.com/pyinstaller/pyinstaller) | Multiplatform executable freezing engine with special exception permitting proprietary/permissive payloads. |
| **pyinstaller-hooks-contrib** | `>=2024.0` | Apache-2.0 | `Apache-2.0` | [pyinstaller/pyinstaller-hooks-contrib](https://github.com/pyinstaller/pyinstaller-hooks-contrib) | Community hooks repository for PyInstaller package bundling. |
| **altgraph** | `>=0.17.4` | MIT | `MIT` | [ronaldoussoren/altgraph](https://github.com/ronaldoussoren/altgraph) | Python graph (network) package used by PyInstaller. |
| **packaging** | `>=24.0` | Apache-2.0 OR BSD-2-Clause | `Apache-2.0 OR BSD-2-Clause` | [pypa/packaging](https://github.com/pypa/packaging) | Core utilities for Python packages and version parsing. |

---

## Licensing Architecture, Dynamic Linking & Unprivileged Execution

### Dynamic Linking & LGPL-3.0 / LGPL-2.1 Isolation
- **ProSync Core:** All application code, business logic, sync engine workers, scheduling routines, and the offline Web/PWA companion are licensed under the permissive [MIT License](LICENSE) with canonical attribution documented in [NOTICE](NOTICE).
- **PySide6 (LGPL-3.0-only):** The Qt 6 bindings and Qt runtime binaries are linked dynamically via official CPython wheels. In frozen binary distributions (PyInstaller), Qt libraries reside as separate shared objects / DLLs (`Qt6Core.dll`, `Qt6Gui.dll`, `Qt6Widgets.dll`), permitting end users to replace the Qt library binaries in compliance with LGPL-3.0 Section 4.
- **Paramiko (LGPL-2.1-or-later):** The SSH/SFTP networking library is dynamically imported as a standard Python module without static merging into ProSync source files.
- **Zero-Copyleft Contamination:** The application codebase contains no GPL or AGPL proprietary-restricting source code. The PyInstaller bootloader exception expressly permits combining with the application without viral licensing effects.

### Unprivileged User-Mode Operation (`RunAsInvoker`)
- All ProSync processes (`ProSyncStart_V3.1.py`, `ProSyncReader.py`, CLI invocation, batch queues, and background system tray workers) execute strictly in **unprivileged user mode** (`RunAsInvoker`).
- No administrative elevation, UAC elevation prompt, or root capabilities are ever required or requested.
- Configuration and logs reside safely within the user profile directory (`%LOCALAPPDATA%\ProSync` on Windows or `~/.config/ProSync` on POSIX systems).

---

## Governance & Runtime Invariants

`ProSync` adheres to ten foundational governance and runtime invariants:

| Invariant | Category | Description | Verification Method |
|---|---|---|---|
| `INV-LOCAL-01` | Local-First & Zero Egress | 100% offline-first execution; zero telemetry, analytics, or unsolicited network calls. | `tests/test_security_license_contract.py` |
| `INV-RUNAS-02` | Unprivileged User Mode (`RunAsInvoker`) | Strictly unprivileged execution; no UAC or root prompts required. | `SECURITY.md` & `pyproject.toml` |
| `INV-WAL-03` | SQLite WAL Crash Safety | Automated pre-sync checkpoint (`PRAGMA wal_checkpoint(TRUNCATE)`); aborts fail-closed on lock contention (`SQLITE_BUSY`). | `tests/test_sftp_target.py` & `ProSyncStart_V3.1.py` |
| `INV-INTEG-04` | Atomic File Copy & Crash Resilience | Staging to temporary files (`.tmp`) prior to atomic replacement; target files never corrupted by interruption. | `tests/test_bugsweep_resweep_20260622.py` |
| `INV-SCHED-05` | DST-Aware Canonical Scheduling | Deterministic daily scheduling using IANA timezones and exact wall-time calculations without catch-up cascades. | `tests/test_schedule_time.py` |
| `INV-PWA-06` | Redacted Offline Companion Export | Exported profile (`prosync-profile-v1.json`) strictly redacts personal paths, credentials, and tokens. | `tests/test_portable_profile.py` |
| `INV-PLAT-07` | Cross-Platform Parity | Standardized 8-point smoke test suites for Linux and macOS execution parity. | `tests/test_platform_smoke_contract.py` |
| `INV-STORE-08` | Windows Store / MSIX Staging | Valid AppxManifest (`Geiger.ProSync`), Policy 10.1.3 compliant metadata, and verified tile asset dimensions. | `tests/test_store_materials.py` |
| `INV-DOCS-09` | 1:1 Bilingual Documentation | Symmetrical 18-point documentation parity across English (`README.md`) and German (`README_de.md`) backed by `llms.txt`. | `tests/test_metadata.py` |
| `INV-SLA-10` | Open Source Governance & SLA | MIT License, public GitHub issues, and committed 48h initial response / 5d triage security SLA. | `SECURITY.md` & `tests/test_metadata.py` |

---

## License Texts & Attribution

### MIT License (`ProSync`, `pytest`, `ruff`, `pip-licenses`, `altgraph`)

```
MIT License

Copyright (c) 2026 Lukas Geiger / file-bricks

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### GNU Lesser General Public License v3.0 (`PySide6`, `shiboken6`)
*Refer to [GNU LGPL v3.0 Text](https://www.gnu.org/licenses/lgpl-3.0.en.html) for full legal terms.*

### GNU Lesser General Public License v2.1 (`paramiko`)
*Refer to [GNU LGPL v2.1 Text](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html) for full legal terms.*

### Apache License 2.0 (`tzdata`, `bcrypt`, `PyNaCl`, `pyinstaller-hooks-contrib`, `packaging`)
*Refer to [Apache-2.0 License Text](https://www.apache.org/licenses/LICENSE-2.0) for full legal terms.*

### BSD 3-Clause License (`pypdf`, `cryptography`)
*Refer to [BSD 3-Clause License Text](https://opensource.org/licenses/BSD-3-Clause) for full legal terms.*

### BSD 2-Clause License (`invoke`, `packaging`)
*Refer to [BSD 2-Clause License Text](https://opensource.org/licenses/BSD-2-Clause) for full legal terms.*
