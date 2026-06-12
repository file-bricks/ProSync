import test from "node:test";
import assert from "node:assert/strict";

import {
  createDemoProfile,
  filterConnections,
  parseProfilePayload,
  parseProfileText,
  summarizeProfile,
} from "../library.js";

test("parseProfilePayload normalisiert Demo-Profil", () => {
  const profile = parseProfilePayload(createDemoProfile());
  assert.equal(profile.connections.length, 2);
  assert.equal(profile.reports.count, 4);
  assert.equal(profile.reports.items.length, 2);
  assert.equal(profile.connections[0].pathHints.sourceLabel, "Alpha");
});

test("parseProfileText lehnt falsches Schema ab", () => {
  assert.throws(
    () => parseProfileText(JSON.stringify({ schema: "unknown", connections: [] })),
    /Unbekanntes Profilformat/,
  );
});

test("filterConnections sucht in Name, Modus und Ausschlussmustern", () => {
  const profile = parseProfilePayload(createDemoProfile());
  const byMode = filterConnections(profile, { mode: "mirror" });
  assert.equal(byMode.length, 1);
  assert.equal(byMode[0].name, "Alpha Backup");

  const bySearch = filterConnections(profile, { search: "__pycache__" });
  assert.equal(bySearch.length, 1);
  assert.equal(bySearch[0].id, "folder-alpha");
});

test("summarizeProfile zählt Typen, Autosync und Reports", () => {
  const profile = parseProfilePayload(createDemoProfile());
  const summary = summarizeProfile(profile);
  assert.equal(summary.connectionCount, 2);
  assert.equal(summary.autosyncEnabledCount, 1);
  assert.equal(summary.checkpointCount, 1);
  assert.equal(summary.types.folder, 1);
  assert.equal(summary.types.file, 1);
  assert.equal(summary.reportCount, 4);
});
