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
