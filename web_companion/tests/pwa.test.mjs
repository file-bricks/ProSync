import test, { describe } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");

test("manifest beschreibt den ProSync Companion", () => {
  const manifest = JSON.parse(
    fs.readFileSync(path.join(root, "manifest.webmanifest"), "utf8"),
  );
  assert.equal(manifest.name, "ProSync Companion");
  assert.equal(manifest.start_url, "./");
  assert.equal(manifest.display, "standalone");
  assert.ok(Array.isArray(manifest.icons));
  assert.ok(manifest.icons.some((icon) => icon.src === "./icon.svg"));
});

test("service worker cached die Shell-Dateien", () => {
  const sw = fs.readFileSync(path.join(root, "sw.js"), "utf8");
  assert.match(sw, /prosync-web-companion-v2/);
  assert.match(sw, /"\.\/index\.html"/);
  assert.match(sw, /"\.\/app\.js"/);
  assert.match(sw, /"\.\/library\.js"/);
});

test("index bindet Manifest und Modulskript ein", () => {
  const index = fs.readFileSync(path.join(root, "index.html"), "utf8");
  assert.match(index, /manifest\.webmanifest/);
  assert.match(index, /script type="module" src="\.\/app\.js"/);
  assert.match(index, /prosync-profile-v1\.json/);
});

test("index enthält apple-touch-icon für iOS-Homescreen", () => {
  const index = fs.readFileSync(path.join(root, "index.html"), "utf8");
  assert.match(index, /rel="apple-touch-icon"/, "apple-touch-icon fehlt — iOS Safari zeigt Screenshot statt Icon");
});

// --- iOS PWA-Härtung (P4b, 2026-06-16) ---
describe("iOS PWA-Härtung", () => {
  const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
  const css = fs.readFileSync(path.join(root, "app.css"), "utf8");
  const sw = fs.readFileSync(path.join(root, "sw.js"), "utf8");

  test("viewport enthält viewport-fit=cover (Notch/Dynamic Island)", () => {
    assert.match(html, /viewport-fit=cover/, "viewport-fit=cover fehlt im viewport-Meta-Tag");
  });

  test("apple-touch-icon zeigt auf apple-touch-icon-180.png (opak, kein SVG)", () => {
    assert.match(html, /apple-touch-icon-180\.png/, "apple-touch-icon-180.png fehlt als Linkziel");
  });

  test("apple-mobile-web-app-title ist vorhanden", () => {
    assert.match(html, /apple-mobile-web-app-title/, "apple-mobile-web-app-title Meta-Tag fehlt");
  });

  test("apple-mobile-web-app-status-bar-style ist vorhanden", () => {
    assert.match(html, /apple-mobile-web-app-status-bar-style/, "apple-mobile-web-app-status-bar-style Meta-Tag fehlt");
  });

  test("KEIN apple-mobile-web-app-capable (deprecated seit iOS 11.3)", () => {
    assert.doesNotMatch(html, /name="apple-mobile-web-app-capable"/, "apple-mobile-web-app-capable ist deprecated und darf nicht gesetzt sein");
  });

  test("apple-touch-icon-180.png existiert physisch im Stammverzeichnis", () => {
    assert.ok(fs.existsSync(path.join(root, "apple-touch-icon-180.png")), "apple-touch-icon-180.png fehlt");
  });

  test("app.css enthält safe-area-inset-top", () => {
    assert.match(css, /safe-area-inset-top/, "safe-area-inset-top fehlt in app.css");
  });

  test("app.css enthält safe-area-inset-bottom", () => {
    assert.match(css, /safe-area-inset-bottom/, "safe-area-inset-bottom fehlt in app.css");
  });

  test("sw.js enthält apple-touch-icon-180.png in ASSETS", () => {
    assert.match(sw, /apple-touch-icon-180\.png/, "apple-touch-icon-180.png fehlt im SW ASSETS");
  });
});

test("app.js schützt localStorage.getItem in loadStoredProfile mit try/catch", () => {
  const app = fs.readFileSync(path.join(root, "app.js"), "utf8");
  // loadStoredProfile must wrap getItem in a try/catch before accessing the result
  // Pattern: try { ... getItem ... } catch
  const loadFnMatch = app.match(/function loadStoredProfile\(\)\s*\{([\s\S]*?)^}/m);
  assert.ok(loadFnMatch, "loadStoredProfile nicht gefunden");
  const fnBody = loadFnMatch[1];
  const getItemPos = fnBody.indexOf("localStorage.getItem");
  const tryBeforeGetItem = fnBody.lastIndexOf("try {", getItemPos);
  assert.ok(tryBeforeGetItem !== -1 && tryBeforeGetItem < getItemPos, "localStorage.getItem in loadStoredProfile ist nicht in try/catch eingebettet");
});
