import {
  createDemoProfile,
  filterConnections,
  parseProfilePayload,
  parseProfileText,
  readProfileFile,
  sortConnections,
  summarizeProfile,
} from "./library.js";

const STORAGE_KEY = "prosync-web-companion-profile-v1";

const state = {
  profile: null,
  sourceLabel: "Kein Profil geladen",
};

const elements = {
  importInput: document.querySelector("#import-input"),
  importButton: document.querySelector("#import-button"),
  pasteButton: document.querySelector("#paste-button"),
  demoButton: document.querySelector("#demo-button"),
  resetButton: document.querySelector("#reset-button"),
  jsonInput: document.querySelector("#json-input"),
  searchInput: document.querySelector("#search-input"),
  typeFilter: document.querySelector("#type-filter"),
  modeFilter: document.querySelector("#mode-filter"),
  autosyncFilter: document.querySelector("#autosync-filter"),
  sortSelect: document.querySelector("#sort-select"),
  status: document.querySelector("#load-status"),
  installHint: document.querySelector("#install-hint"),
  offlineHint: document.querySelector("#offline-hint"),
  summary: document.querySelector("#summary-cards"),
  typeList: document.querySelector("#type-list"),
  modeList: document.querySelector("#mode-list"),
  connectionCount: document.querySelector("#connection-count"),
  connectionList: document.querySelector("#connection-list"),
  emptyState: document.querySelector("#empty-state"),
  reportList: document.querySelector("#report-list"),
  reportEmpty: document.querySelector("#report-empty"),
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatDate(isoString) {
  if (!isoString) {
    return "unbekannt";
  }
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) {
    return isoString;
  }
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatBytes(bytes) {
  const value = Number(bytes);
  if (!Number.isFinite(value) || value <= 0) {
    return "0 B";
  }
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = value;
  let index = 0;
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024;
    index += 1;
  }
  return `${size.toFixed(size >= 10 || index === 0 ? 0 : 1)} ${units[index]}`;
}

function setStatus(message, kind = "info") {
  elements.status.textContent = message;
  elements.status.dataset.kind = kind;
}

function detectInstallHint() {
  const agent = navigator.userAgent.toLowerCase();
  if (agent.includes("iphone") || agent.includes("ipad")) {
    return "iPhone/iPad: In Safari über Teilen -> Zum Home-Bildschirm als lokale Referenz anheften.";
  }
  if (agent.includes("android")) {
    return "Android: Im Browser-Menü App installieren oder Zum Startbildschirm hinzufügen nutzen.";
  }
  return "Desktop: Im Browser als App installieren oder einfach als Offline-Referenz geöffnet lassen.";
}

function updateOfflineHint() {
  elements.offlineHint.textContent = navigator.onLine
    ? "Online oder lokaler Host erkannt. Nach dem ersten Laden bleibt der letzte Profilstand offline verfügbar."
    : "Offline-Modus aktiv. Der Companion arbeitet mit dem letzten lokal gespeicherten Profilstand.";
}

function saveProfile(profile) {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        sourceLabel: state.sourceLabel,
        profile,
        savedAt: new Date().toISOString(),
      }),
    );
  } catch (_error) {
    setStatus("Profil konnte nicht lokal gespeichert werden.", "warning");
  }
}

function loadStoredProfile() {
  let raw;
  try {
    raw = localStorage.getItem(STORAGE_KEY);
  } catch (_error) {
    return null;
  }
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw);
    return {
      sourceLabel: parsed.sourceLabel ?? "Zuletzt geladenes Profil",
      profile: coerceStoredProfile(parsed.profile),
    };
  } catch (_error) {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (_removeError) {
      // Ignore removal errors (e.g. Safari Private Mode)
    }
    return null;
  }
}

function coerceStoredProfile(profile) {
  if (!profile || typeof profile !== "object") {
    throw new Error("Kein gespeichertes Profil gefunden.");
  }
  if ("exportedAt" in profile && Array.isArray(profile.connections) && profile.reports) {
    return profile;
  }
  return parseProfilePayload(profile);
}

function renderSummary(profile) {
  const summary = summarizeProfile(profile);
  const latest = profile.reports.latest;
  const cards = [
    { label: "Quelle", value: state.sourceLabel },
    { label: "Exportiert", value: formatDate(profile.exportedAt) },
    { label: "App-Version", value: profile.exportedFromVersion },
    { label: "Verbindungen", value: String(summary.connectionCount) },
    { label: "Autosync aktiv", value: String(summary.autosyncEnabledCount) },
    { label: "Reports im Export", value: String(summary.reportCount) },
    { label: "Letzter Lauf", value: latest ? formatDate(latest.startedAt) : "Keiner" },
    { label: "Desktop-Hinweis", value: profile.notificationsEnabled ? "Benachrichtigungen an" : "Benachrichtigungen aus" },
  ];

  elements.summary.innerHTML = cards
    .map(
      (card) => `
        <article class="summary-card">
          <span class="summary-label">${escapeHtml(card.label)}</span>
          <strong class="summary-value">${escapeHtml(card.value)}</strong>
        </article>
      `,
    )
    .join("");
}

function renderMetaLists(profile) {
  const summary = summarizeProfile(profile);
  const typeEntries = Object.entries(summary.types).sort((left, right) => right[1] - left[1]);
  const modeEntries = Object.entries(summary.modes).sort((left, right) => right[1] - left[1]);

  elements.typeFilter.innerHTML = ['<option value="all">Alle Typen</option>']
    .concat(typeEntries.map(([type]) => `<option value="${escapeHtml(type)}">${escapeHtml(type)}</option>`))
    .join("");

  elements.modeFilter.innerHTML = ['<option value="all">Alle Modi</option>']
    .concat(modeEntries.map(([mode]) => `<option value="${escapeHtml(mode)}">${escapeHtml(mode)}</option>`))
    .join("");

  elements.typeList.innerHTML = typeEntries
    .map(
      ([type, count]) => `
        <li class="meta-item">
          <span>${escapeHtml(type)}</span>
          <span class="pill">${count}</span>
        </li>
      `,
    )
    .join("");

  elements.modeList.innerHTML = modeEntries
    .map(
      ([mode, count]) => `
        <li class="meta-item">
          <span>${escapeHtml(mode)}</span>
          <span class="pill">${count}</span>
        </li>
      `,
    )
    .join("");
}

function renderConnections(profile) {
  const filtered = filterConnections(profile, {
    search: elements.searchInput.value,
    type: elements.typeFilter.value,
    mode: elements.modeFilter.value,
    autosync: elements.autosyncFilter.value,
  });
  const visibleConnections = sortConnections(filtered, elements.sortSelect.value);

  elements.connectionCount.textContent = `${visibleConnections.length} sichtbar`;
  elements.connectionList.innerHTML = visibleConnections
    .map((connection) => {
      const autosyncText = connection.autosyncEnabled
        ? `Aktiv · alle ${connection.autosyncIntervalMinutes} Min`
        : "Inaktiv";
      const safety = connection.safetySummary;
      const safetyFacts = safety
        ? `
          <div class="facts-grid">
            <div class="fact-box">
              <span class="label">Datenbanken</span>
              <strong>${safety.databasesFound}</strong>
            </div>
            <div class="fact-box">
              <span class="label">Kritisch</span>
              <strong>${safety.criticalDatabases}</strong>
            </div>
            <div class="fact-box">
              <span class="label">Ausgeschlossen</span>
              <strong>${safety.excludedDatabases}</strong>
            </div>
            <div class="fact-box">
              <span class="label">DB-Größe</span>
              <strong>${escapeHtml(`${safety.totalDbSizeMb} MB`)}</strong>
            </div>
          </div>
        `
        : "";

      const chips = [];
      chips.push(`<span class="pill">${escapeHtml(connection.type)}</span>`);
      chips.push(`<span class="pill">${escapeHtml(connection.mode)}</span>`);
      if (connection.autosyncEnabled) {
        chips.push('<span class="pill pill--accent">Autosync aktiv</span>');
      }
      if (connection.checkpointBeforeSync) {
        chips.push('<span class="pill">Checkpoint vor Sync</span>');
      }
      if (connection.indexing) {
        chips.push('<span class="pill">Indexierung</span>');
      }
      if (connection.requiresMapping) {
        chips.push('<span class="pill">Neu zuordnen</span>');
      }

      const excludePatterns = connection.excludePatterns.length
        ? connection.excludePatterns.map((pattern) => `<span class="pill">${escapeHtml(pattern)}</span>`).join("")
        : '<span class="subtle">Keine Ausschlussmuster im Export.</span>';

      return `
        <article class="connection-card">
          <div class="connection-card__header">
            <div>
              <h3>${escapeHtml(connection.name)}</h3>
              <p class="subtle">${escapeHtml(connection.id)} · ${escapeHtml(autosyncText)}</p>
            </div>
            <div class="chip-list">${chips.join("")}</div>
          </div>
          <div class="path-grid">
            <div class="path-box">
              <span class="label">Quelle</span>
              <strong class="code-line">${escapeHtml(connection.pathHints.sourceLabel)}</strong>
            </div>
            <div class="path-box">
              <span class="label">Ziel</span>
              <strong class="code-line">${escapeHtml(connection.pathHints.targetLabel)}</strong>
            </div>
            <div class="path-box">
              <span class="label">Index / DB</span>
              <strong class="code-line">${escapeHtml(connection.pathHints.dbLabel || "Nicht enthalten")}</strong>
            </div>
            <div class="path-box">
              <span class="label">Konfliktregel</span>
              <strong>${escapeHtml(connection.conflictPolicy || "Nicht gesetzt")}</strong>
            </div>
          </div>
          <div class="path-box">
            <span class="label">Ausschlussmuster</span>
            <div class="chip-list">${excludePatterns}</div>
          </div>
          ${safetyFacts}
        </article>
      `;
    })
    .join("");

  const hasConnections = visibleConnections.length > 0;
  elements.emptyState.hidden = hasConnections;
  elements.connectionList.hidden = !hasConnections;
}

function renderReports(profile) {
  const reports = profile.reports.items;
  elements.reportList.innerHTML = reports
    .map(
      (report) => `
        <article class="report-card">
          <div class="report-card__header">
            <div>
              <h3>${escapeHtml(report.connection)}</h3>
              <p class="subtle">${escapeHtml(report.connectionId || "ohne ID")} · ${escapeHtml(report.mode)}</p>
            </div>
            <span class="pill">${escapeHtml(formatDate(report.startedAt))}</span>
          </div>
          <div class="report-stats">
            <div class="fact-box">
              <span class="label">Dauer</span>
              <strong>${escapeHtml(`${report.durationSeconds} s`)}</strong>
            </div>
            <div class="fact-box">
              <span class="label">Kopiert</span>
              <strong>${report.filesCopied}</strong>
            </div>
            <div class="fact-box">
              <span class="label">Gelöscht</span>
              <strong>${report.filesDeleted}</strong>
            </div>
            <div class="fact-box">
              <span class="label">Übersprungen</span>
              <strong>${report.filesSkipped}</strong>
            </div>
            <div class="fact-box">
              <span class="label">Aktionen</span>
              <strong>${report.totalActions}</strong>
            </div>
            <div class="fact-box">
              <span class="label">Datenmenge</span>
              <strong>${escapeHtml(formatBytes(report.bytesCopied))}</strong>
            </div>
          </div>
        </article>
      `,
    )
    .join("");

  const hasReports = reports.length > 0;
  elements.reportEmpty.hidden = hasReports;
  elements.reportList.hidden = !hasReports;
}

function renderProfile(profile) {
  state.profile = profile;
  renderSummary(profile);
  renderMetaLists(profile);
  renderConnections(profile);
  renderReports(profile);
}

function loadDemoProfile() {
  const profile = parseProfilePayload(createDemoProfile());
  state.sourceLabel = "Demo-Profil";
  saveProfile(profile);
  renderProfile(profile);
  setStatus("Demo-Profil geladen.", "success");
}

async function handleFileImport() {
  const [file] = elements.importInput.files ?? [];
  if (!file) {
    return;
  }
  try {
    const profile = await readProfileFile(file);
    state.sourceLabel = file.name;
    saveProfile(profile);
    renderProfile(profile);
    setStatus(`Profil geladen: ${file.name}`, "success");
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    elements.importInput.value = "";
  }
}

function handlePasteImport() {
  const text = elements.jsonInput.value.trim();
  if (!text) {
    setStatus("Bitte zuerst JSON in das Textfeld einfügen.", "warning");
    return;
  }
  try {
    const profile = parseProfileText(text);
    state.sourceLabel = "JSON-Paste";
    saveProfile(profile);
    renderProfile(profile);
    setStatus("Profil aus Text geladen.", "success");
  } catch (error) {
    setStatus(error.message, "error");
  }
}

function clearStoredProfile() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (_removeError) {
    // Ignore removal errors (e.g. Safari Private Mode, policy-blocked storage)
  }
  state.profile = null;
  state.sourceLabel = "Kein Profil geladen";
  elements.jsonInput.value = "";
  elements.summary.innerHTML = "";
  elements.typeList.innerHTML = "";
  elements.modeList.innerHTML = "";
  elements.connectionList.innerHTML = "";
  elements.reportList.innerHTML = "";
  elements.connectionList.hidden = true;
  elements.reportList.hidden = true;
  elements.emptyState.hidden = false;
  elements.reportEmpty.hidden = false;
  elements.connectionCount.textContent = "0 sichtbar";
  elements.typeFilter.innerHTML = '<option value="all">Alle Typen</option>';
  elements.modeFilter.innerHTML = '<option value="all">Alle Modi</option>';
  elements.sortSelect.value = "name-asc";
  setStatus("Lokaler Profilstand entfernt.", "info");
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    return;
  }
  navigator.serviceWorker.register("./sw.js").catch(() => {
    setStatus("Service Worker konnte lokal nicht registriert werden.", "warning");
  });
}

function bindEvents() {
  elements.importButton.addEventListener("click", () => elements.importInput.click());
  elements.importInput.addEventListener("change", handleFileImport);
  elements.pasteButton.addEventListener("click", handlePasteImport);
  elements.demoButton.addEventListener("click", loadDemoProfile);
  elements.resetButton.addEventListener("click", clearStoredProfile);
  elements.searchInput.addEventListener("input", () => {
    if (state.profile) {
      renderConnections(state.profile);
    }
  });
  elements.typeFilter.addEventListener("change", () => {
    if (state.profile) {
      renderConnections(state.profile);
    }
  });
  elements.modeFilter.addEventListener("change", () => {
    if (state.profile) {
      renderConnections(state.profile);
    }
  });
  elements.autosyncFilter.addEventListener("change", () => {
    if (state.profile) {
      renderConnections(state.profile);
    }
  });
  elements.sortSelect.addEventListener("change", () => {
    if (state.profile) {
      renderConnections(state.profile);
    }
  });
  window.addEventListener("online", updateOfflineHint);
  window.addEventListener("offline", updateOfflineHint);
}

function boot() {
  elements.installHint.textContent = detectInstallHint();
  updateOfflineHint();
  bindEvents();
  registerServiceWorker();

  const params = new URLSearchParams(window.location.search);
  if (params.get("demo") === "1") {
    loadDemoProfile();
    return;
  }

  const stored = loadStoredProfile();
  if (stored) {
    state.sourceLabel = stored.sourceLabel;
    renderProfile(stored.profile);
    setStatus("Letztes Profil aus dem Browser-Speicher wiederhergestellt.", "info");
    return;
  }

  setStatus("Noch kein Profil geladen. Importiere eine `prosync-profile-v1.json` oder starte mit Demo.", "info");
}

boot();
