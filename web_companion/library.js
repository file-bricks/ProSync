const PROFILE_SCHEMA = "prosync-profile-v1";

export function createDemoProfile() {
  return {
    schema: PROFILE_SCHEMA,
    exported_at: "2026-06-08T09:45:00Z",
    exported_from: {
      app: "ProSync",
      version: "3.2",
    },
    app: {
      notifications_enabled: true,
    },
    connections: [
      {
        id: "folder-alpha",
        name: "Alpha Backup",
        type: "folder",
        mode: "mirror",
        exclude_patterns: ["*.tmp", "__pycache__", "*.lock"],
        autosync: {
          enabled: true,
          interval_minutes: 30,
        },
        path_hints: {
          source_label: "Alpha",
          target_label: "Alpha-Backup",
          db_label: "index.db",
        },
        conflict_policy: "source",
        indexing: true,
        safety_summary: {
          kind: "folder",
          databases_found: 3,
          critical_databases: 1,
          excluded_databases: 1,
          total_db_size_mb: 41.2,
        },
      },
      {
        id: "file-ledger",
        name: "SQLite Ledger",
        type: "file",
        mode: "one_way",
        exclude_patterns: [],
        autosync: {
          enabled: false,
          interval_minutes: 240,
        },
        path_hints: {
          source_label: "ledger.sqlite",
          target_label: "ledger-backup.sqlite",
        },
        checkpoint_before_sync: true,
        safety_summary: {
          kind: "file",
          databases_found: 1,
          critical_databases: 1,
          excluded_databases: 0,
          total_db_size_mb: 5.4,
        },
      },
    ],
    reports: {
      count: 4,
      latest: {
        connection: "Alpha Backup",
        connection_id: "folder-alpha",
        mode: "mirror",
        started_at: "2026-06-08T08:20:00Z",
        duration_seconds: 18.4,
        files_copied: 32,
        files_deleted: 2,
        files_skipped: 11,
        bytes_copied: 3812044,
        total_actions: 45,
      },
      items: [
        {
          connection: "Alpha Backup",
          connection_id: "folder-alpha",
          mode: "mirror",
          started_at: "2026-06-08T08:20:00Z",
          duration_seconds: 18.4,
          files_copied: 32,
          files_deleted: 2,
          files_skipped: 11,
          bytes_copied: 3812044,
          total_actions: 45,
        },
        {
          connection: "SQLite Ledger",
          connection_id: "file-ledger",
          mode: "one_way",
          started_at: "2026-06-07T21:05:00Z",
          duration_seconds: 3.1,
          files_copied: 1,
          files_deleted: 0,
          files_skipped: 0,
          bytes_copied: 5481201,
          total_actions: 1,
        },
      ],
    },
  };
}

function normalizeString(value, fallback = "") {
  if (value == null) {
    return fallback;
  }
  return String(value).trim() || fallback;
}

function normalizeNumber(value, fallback = 0) {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function normalizeBoolean(value) {
  return value === true;
}

function normalizePathHints(pathHints) {
  const hints = pathHints && typeof pathHints === "object" ? pathHints : {};
  return {
    sourceLabel: normalizeString(hints.source_label, "Quelle unbekannt"),
    targetLabel: normalizeString(hints.target_label, "Ziel unbekannt"),
    dbLabel: normalizeString(hints.db_label, ""),
  };
}

function normalizeSafetySummary(summary) {
  if (!summary || typeof summary !== "object") {
    return null;
  }
  return {
    kind: normalizeString(summary.kind, "unbekannt"),
    databasesFound: normalizeNumber(summary.databases_found, 0),
    criticalDatabases: normalizeNumber(summary.critical_databases, 0),
    excludedDatabases: normalizeNumber(summary.excluded_databases, 0),
    totalDbSizeMb: normalizeNumber(summary.total_db_size_mb, 0),
  };
}

function normalizeConnection(connection, index) {
  if (!connection || typeof connection !== "object" || Array.isArray(connection)) {
    return null;
  }

  const id = normalizeString(connection.id, `connection-${index + 1}`);
  const name = normalizeString(connection.name, id);
  const type = normalizeString(connection.type, "unknown");
  const mode = normalizeString(connection.mode, "unknown");
  const excludePatterns = Array.isArray(connection.exclude_patterns)
    ? connection.exclude_patterns.map((pattern) => normalizeString(pattern)).filter(Boolean)
    : [];
  const autosync = connection.autosync && typeof connection.autosync === "object" ? connection.autosync : {};
  const pathHints = normalizePathHints(connection.path_hints);
  const requiresMapping = normalizeBoolean(connection.requires_mapping);

  return {
    id,
    name,
    type,
    mode,
    excludePatterns,
    autosyncEnabled: normalizeBoolean(autosync.enabled),
    autosyncIntervalMinutes: normalizeNumber(autosync.interval_minutes, 15),
    pathHints,
    conflictPolicy: normalizeString(connection.conflict_policy, ""),
    indexing: normalizeBoolean(connection.indexing),
    checkpointBeforeSync: normalizeBoolean(connection.checkpoint_before_sync),
    requiresMapping,
    safetySummary: normalizeSafetySummary(connection.safety_summary),
  };
}

function normalizeReport(report) {
  if (!report || typeof report !== "object" || Array.isArray(report)) {
    return null;
  }
  return {
    connection: normalizeString(report.connection, "Unbekannte Verbindung"),
    connectionId: normalizeString(report.connection_id, ""),
    mode: normalizeString(report.mode, "unknown"),
    startedAt: normalizeString(report.started_at, ""),
    durationSeconds: normalizeNumber(report.duration_seconds, 0),
    filesCopied: normalizeNumber(report.files_copied, 0),
    filesDeleted: normalizeNumber(report.files_deleted, 0),
    filesSkipped: normalizeNumber(report.files_skipped, 0),
    bytesCopied: normalizeNumber(report.bytes_copied, 0),
    totalActions: normalizeNumber(report.total_actions, 0),
  };
}

export function parseProfilePayload(payload) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("Das Profil ist kein JSON-Objekt.");
  }
  if (payload.schema !== PROFILE_SCHEMA) {
    throw new Error("Unbekanntes Profilformat.");
  }

  const connections = Array.isArray(payload.connections)
    ? payload.connections.map((connection, index) => normalizeConnection(connection, index)).filter(Boolean)
    : [];

  const reports = payload.reports && typeof payload.reports === "object" ? payload.reports : {};
  const reportItems = Array.isArray(reports.items)
    ? reports.items.map((report) => normalizeReport(report)).filter(Boolean)
    : [];
  const latest = normalizeReport(reports.latest);
  if (latest && reportItems.every((report) => report.startedAt !== latest.startedAt || report.connectionId !== latest.connectionId)) {
    reportItems.unshift(latest);
  }

  return {
    schema: PROFILE_SCHEMA,
    exportedAt: normalizeString(payload.exported_at, ""),
    exportedFromApp: normalizeString(payload.exported_from?.app, "ProSync"),
    exportedFromVersion: normalizeString(payload.exported_from?.version, "unbekannt"),
    notificationsEnabled: normalizeBoolean(payload.app?.notifications_enabled),
    connections,
    reports: {
      count: normalizeNumber(reports.count, reportItems.length),
      latest,
      items: reportItems,
    },
  };
}

export function summarizeProfile(profile) {
  const types = {};
  const modes = {};
  let autosyncEnabledCount = 0;
  let checkpointCount = 0;
  let indexedCount = 0;
  let mappingCount = 0;

  for (const connection of profile.connections) {
    types[connection.type] = (types[connection.type] ?? 0) + 1;
    modes[connection.mode] = (modes[connection.mode] ?? 0) + 1;
    if (connection.autosyncEnabled) {
      autosyncEnabledCount += 1;
    }
    if (connection.checkpointBeforeSync) {
      checkpointCount += 1;
    }
    if (connection.indexing) {
      indexedCount += 1;
    }
    if (connection.requiresMapping) {
      mappingCount += 1;
    }
  }

  return {
    connectionCount: profile.connections.length,
    autosyncEnabledCount,
    checkpointCount,
    indexedCount,
    mappingCount,
    types,
    modes,
    reportCount: profile.reports.count,
  };
}

// sortBy: 'name-asc' | 'name-desc' | 'autosync-first' | 'type'
export function sortConnections(connections, sortBy = "name-asc") {
  const sorted = [...connections];
  switch (sortBy) {
    case "name-desc":
      sorted.sort((a, b) => b.name.localeCompare(a.name, "de"));
      break;
    case "autosync-first":
      sorted.sort((a, b) => {
        if (a.autosyncEnabled !== b.autosyncEnabled) {
          return a.autosyncEnabled ? -1 : 1;
        }
        return a.name.localeCompare(b.name, "de");
      });
      break;
    case "type":
      sorted.sort(
        (a, b) =>
          a.type.localeCompare(b.type, "de") ||
          a.name.localeCompare(b.name, "de"),
      );
      break;
    default: // 'name-asc'
      sorted.sort((a, b) => a.name.localeCompare(b.name, "de"));
  }
  return sorted;
}

export function filterConnections(profile, filters = {}) {
  const search = normalizeString(filters.search).toLowerCase();
  const type = normalizeString(filters.type, "all");
  const mode = normalizeString(filters.mode, "all");
  const autosync = normalizeString(filters.autosync, "all");

  return profile.connections.filter((connection) => {
    if (type !== "all" && connection.type !== type) {
      return false;
    }
    if (mode !== "all" && connection.mode !== mode) {
      return false;
    }
    if (autosync === "enabled" && !connection.autosyncEnabled) {
      return false;
    }
    if (autosync === "disabled" && connection.autosyncEnabled) {
      return false;
    }
    if (!search) {
      return true;
    }

    return [
      connection.id,
      connection.name,
      connection.type,
      connection.mode,
      connection.pathHints.sourceLabel,
      connection.pathHints.targetLabel,
      connection.pathHints.dbLabel,
      connection.excludePatterns.join(" "),
      connection.conflictPolicy,
    ].some((part) => part.toLowerCase().includes(search));
  });
}

export function parseProfileText(text) {
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch (_error) {
    throw new Error("Die Eingabe enthält kein gültiges JSON.");
  }
  return parseProfilePayload(parsed);
}

export async function readProfileFile(file) {
  const text = await file.text();
  return parseProfileText(text);
}
