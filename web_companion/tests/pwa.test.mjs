import test from "node:test";
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
  assert.match(sw, /prosync-web-companion-v1/);
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
