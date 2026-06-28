import test from "node:test";
import assert from "node:assert/strict";

import {
  createDemoProfile,
  filterConnections,
  parseProfilePayload,
  parseProfileText,
  sortConnections,
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

test("sortConnections sortiert nach Name A–Z (Standard)", () => {
  const profile = parseProfilePayload(createDemoProfile());
  // Demo-Profil: "Alpha Backup" (folder) und "SQLite Ledger" (file)
  const sorted = sortConnections(profile.connections, "name-asc");
  assert.equal(sorted[0].name, "Alpha Backup");
  assert.equal(sorted[1].name, "SQLite Ledger");
  // Originalliste bleibt unverändert (immutable)
  assert.equal(profile.connections[0].name, "Alpha Backup");
});

test("sortConnections sortiert nach Name Z–A", () => {
  const profile = parseProfilePayload(createDemoProfile());
  const sorted = sortConnections(profile.connections, "name-desc");
  assert.equal(sorted[0].name, "SQLite Ledger");
  assert.equal(sorted[1].name, "Alpha Backup");
});

test("sortConnections stellt Autosync-aktive Verbindungen voran", () => {
  const profile = parseProfilePayload(createDemoProfile());
  // "Alpha Backup" hat autosync enabled=true, "SQLite Ledger" hat enabled=false
  const sorted = sortConnections(profile.connections, "autosync-first");
  assert.equal(sorted[0].autosyncEnabled, true, "Erste Verbindung soll Autosync aktiv haben");
  assert.equal(sorted[0].name, "Alpha Backup");
  assert.equal(sorted[1].autosyncEnabled, false);
});

test("sortConnections sortiert nach Typ (lexikalisch, dann Name)", () => {
  const profile = parseProfilePayload(createDemoProfile());
  // 'file' < 'folder' lexikalisch
  const sorted = sortConnections(profile.connections, "type");
  assert.equal(sorted[0].type, "file");
  assert.equal(sorted[1].type, "folder");
});

test("sortConnections gibt leeres Array zurück bei leeren Verbindungen", () => {
  const result = sortConnections([], "name-asc");
  assert.deepEqual(result, []);
});

test("sortConnections fällt bei unbekanntem sortBy auf name-asc zurück", () => {
  const profile = parseProfilePayload(createDemoProfile());
  const sorted = sortConnections(profile.connections, "unknown");
  assert.equal(sorted[0].name, "Alpha Backup");
  assert.equal(sorted[1].name, "SQLite Ledger");
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
