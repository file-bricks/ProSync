# CROSSCHECK — Externe Dependencies

> Vorlage: `_TEMPLATES/CROSSCHECK_TEMPLATE.md` | Konvention: GUIDE.md §Toolchain-Standards
> Pfad: `_sources/CROSSCHECK.md` im jeweiligen Projektordner
> Stand: 2026-06-07

## Verwendete Pakete mit Major-Version-Pinning

| Paket | Gepinnte Version | Aktuelle Version | Letzte Prüfung |
|---|---|---|---|
| PySide6 | `>=6.5.0` | 6.10.1 | 2026-06-07 |
| PyInstaller (Build-Tool) | — | 6.14.2 | 2026-06-07 |

Aktuelle Version prüfen: `python -m uv pip list --outdated` oder `pip list --outdated`

---

## P0 — Sicherheit / CVEs (blockiert Release)

| # | Paket | Problem | Status | Behoben in |
|---|---|---|---|---|
| — | — | — | — | — |

Quellen: [PyPI Safety DB](https://pypi.org/), [CVE MITRE](https://cve.mitre.org/), `safety check`

---

## P1 — Breaking Changes bei Major-Update (dokumentieren vor Update)

| # | Paket | Von | Nach | Breaking Change | Aufwand |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

---

## P2 — Deprecation-Warnings

| # | Paket | Warnung | Deadline | Maßnahme |
|---|---|---|---|---|
| — | — | — | — | — |

---

## P3 — Nice-to-have Features / Performance

| # | Paket | Neue Funktion | Nützlich für | Priorität |
|---|---|---|---|---|
| — | — | — | — | niedrig |

---

## Workflow

1. **Vor jedem Release:** Alle P0-Einträge abarbeiten; P1 dokumentiert und im CHANGELOG vermerkt.
2. **Quartalsmäßig:** `uv pip list --outdated` laufen lassen, Tabelle aktualisieren.
3. **Neue Deps:** Direkt beim Hinzufügen einen P2/P3-Eintrag anlegen, falls relevante Breaking-Change-Noten im Changelog.
