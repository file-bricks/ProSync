import test, { describe } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { TRANSLATIONS, SUPPORTED_LANGUAGES, getTranslation } from "../app.js";

const root = path.resolve(import.meta.dirname, "..");

describe("Web-Companion Tier-2 I18N Parity (Policy P-006)", () => {
  test("SUPPORTED_LANGUAGES enthält alle 6 Tier-2 Sprachen", () => {
    assert.deepEqual(SUPPORTED_LANGUAGES, ["de", "en", "es", "zh", "ja", "ru"]);
  });

  test("TRANSLATIONS enthält alle 6 Zielsprachen", () => {
    for (const lang of SUPPORTED_LANGUAGES) {
      assert.ok(TRANSLATIONS[lang], `Sprachkatalog für '${lang}' fehlt`);
    }
  });

  test("100% Schlüsselparität über alle 6 Sprachen", () => {
    const baseKeys = Object.keys(TRANSLATIONS.de).sort();
    assert.ok(baseKeys.length >= 70, `Zu wenige Basisschlüssel: ${baseKeys.length}`);

    for (const lang of ["en", "es", "zh", "ja", "ru"]) {
      const langKeys = Object.keys(TRANSLATIONS[lang]).sort();
      assert.deepEqual(
        langKeys,
        baseKeys,
        `Schlüssel-Diskrepanz zwischen 'de' und '${lang}'`,
      );
    }
  });

  test("Keine leeren Strings oder Platzhalter in den Übersetzungen", () => {
    for (const lang of SUPPORTED_LANGUAGES) {
      for (const [key, val] of Object.entries(TRANSLATIONS[lang])) {
        assert.ok(typeof val === "string" && val.trim().length > 0, `Leerer Wert in '${lang}' für '${key}'`);
        assert.ok(!val.includes("PLACEHOLDER"), `Platzhalter gefunden in '${lang}' für '${key}'`);
      }
    }
  });

  test("getTranslation liefert korrekte Sprache und Fallback", () => {
    assert.equal(getTranslation("btn_import", "de"), "Profil importieren");
    assert.equal(getTranslation("btn_import", "en"), "Import profile");
    assert.equal(getTranslation("btn_import", "es"), "Importar perfil");
    assert.equal(getTranslation("btn_import", "zh"), "导入配置文件");
    assert.equal(getTranslation("btn_import", "ja"), "プロファイルをインポート");
    assert.equal(getTranslation("btn_import", "ru"), "Импортировать профиль");

    // Fallback auf DE bei unbekanntem Key in Zielsprache oder Key selbst
    assert.equal(getTranslation("unknown_key_xyz", "es"), "unknown_key_xyz");
  });

  test("index.html bindet #lang-select mit allen 6 Sprachen ein", () => {
    const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
    assert.match(html, /id="lang-select"/, "#lang-select Dropdown fehlt in index.html");
    for (const lang of SUPPORTED_LANGUAGES) {
      assert.match(html, new RegExp(`value="${lang}"`), `Option value='${lang}' fehlt in #lang-select`);
    }
    assert.match(html, /data-i18n="app_title"/);
    assert.match(html, /data-i18n="btn_import"/);
  });
});
