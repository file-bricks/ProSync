# Offene Befunde — ProSync

**Erfasst am:** 2026-08-10
**Rolle:** MAINTAINER (TaskMaster Loop)

### Befund 1: Fremdänderung am Web-Companion-Manifest

- **Fundort:** `web_companion/manifest.webmanifest`
- **Beleg:** Die Arbeitskopie enthält ausschließlich diese bestehende Änderung:
  `M web_companion/manifest.webmanifest`. Gegenüber `HEAD` wurden die Icon-Pfade
  auf kleingeschriebene Dateinamen geändert und `./icon.svg` aus dem `icons`-Array
  entfernt.
- **Auswirkung:** `npm test` meldet 25/29 bestanden und 4 Fehler in den
  Manifest-/Bugsweep-13-Regressionen: fehlendes `./icon.svg` sowie fehlende
  `Icon-192.png`-/`Icon-512.png`-Einträge mit `purpose: "any"`.
- **Maßnahme:** Die Änderung ist nicht Teil dieses MAINTAINER-Slices und wurde
  nicht verändert, nicht gestaged und nicht committet. Die Reparatur bleibt beim
  Eigentümer der Fremdänderung.

### Befund 2: Frischer Qualitäts-Readback

- `python -X utf8 -m pytest -q`: 77/77 Tests bestanden; eine bekannte
  `PyPDF2`-Deprecation-Warnung bleibt.
- `python -B run_tests.py`: alle eingebundenen Smoke- und Store-Material-Checks
  bestanden, einschließlich Source-Platform-Smoke.
- `python -m compileall -q ...`: bestanden.
- `node --check app.js`, `library.js`, `sw.js`: bestanden.
- `npm test`: wegen Befund 1 nicht vollständig grün (25/29 bestanden).

### Abschluss des MAINTAINER-Slices

Es wurde keine Produktdatei verändert. Der dokumentarische Readback ist der
einzige eigene Änderungsumfang; die Manifest-Fremdänderung bleibt erhalten.
Vor dem Slice stand `master` auf `c0c5580` und war laut lokalem Readback vier
Commits hinter `origin/master`; ein Push ist nicht Bestandteil der Rolle.

### Befund 3: Standalone-SFTP-Abbruch mit PySide6 6.12.0 (2026-10-12)

- **Fundort:** Linux/Python-3.10-A/B-Diagnose im [Smoke-Run 38200480460](https://github.com/file-bricks/ProSync/actions/runs/38200480460/job/114652552520).
- **Beleg:** Bei identischen Nicht-Qt-Abhängigkeiten endete der Standalone-SFTP-Test
  mit PySide6/Shiboken6 6.11.2 mit Exit 0; die isolierte SFTP-Pytest-Suite bestand 9/9.
  Mit 6.12.0 bestand Pytest weiter 9/9, doch der Standalone-Prozess gab seine
  Erfolgsmeldung aus und brach anschließend mit Exit -6 und
  `munmap_chunk(): invalid pointer` ab.
- **Einordnung:** Der A/B-Lauf verbindet den Abbruch mit dem gemessenen 6.12.0-
  Distributionssatz auf diesem SFTP-Pfad. Die Ursache der Speicherbeschädigung bleibt
  unbekannt.
- **Maßnahme:** Temporäre Grenze `PySide6>=6.5.0,<6.12` in `requirements.txt`,
  `pyproject.toml` und den CI-Installationspfaden; Paketversion 3.2.0 bleibt
  eingefroren. Die Diagnose-Sonderläufe werden aus dem finalen Workflow entfernt,
  während alle regulären Smoke- und Volltestläufe erhalten bleiben.
- **Wiederöffnung:** Grenze erst neu bewerten, wenn ein neuerer Qt-Stand den
  unveränderten Standalone-SFTP-Test, den vollständigen Smoke-Runner und die
  vorhandenen vollständigen CI-Matrizen erfolgreich absolviert.
