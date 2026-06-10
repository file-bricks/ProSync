# ProSync

Intelligent backup synchronization with database safety.

> [Deutsche Dokumentation](README_de.md)

## Features

- **Folder Synchronization** (one-way / two-way)
- **File Synchronization** for individual files
- **Automatic Database Detection** and protection
- **WAL Checkpoint** for SQLite files before copying
- **System Tray Integration** for background operation
- **Scheduled Backups** with configurable intervals
- **Batch Sync** for multiple selected connections in one run
- **Database Indexing** for search and versioning (optional)
- **ProFiler Companion** -- optional start of ProFiler from the main window

## Screenshots

![Main Window](screenshots/main.png)

## Installation

```bash
pip install -r requirements.txt
```

### Required Packages

- PySide6
- (Optional) PyPDF2 for PDF preview in Reader
- (Optional) python-docx for Word preview in Reader

## Usage

### Via Python

```bash
python ProSyncStart_V3.1.py
```

### Via Batch File

```bash
START.bat
```

The application starts in the system tray. Right-click the icon for options.

## Windows Build

`build_exe.bat` provides a reproducible local Windows build. It creates
`dist/ProSync/ProSync.exe` and copies `ProSyncReader.exe` into the same output
folder so the search UI can still be launched separately in frozen mode.
Build artifacts in `build/`, `dist/`, and `releases/` are intentionally not versioned.

## Quality Checks

```bash
python -m compileall -q ProSyncStart_V3.1.py ProSyncReader.py prosync_utils.py logger.py run_tests.py _WARTUNG/generate_store_screenshots.py test_batch_sync_queue.py test_config_manager.py test_database_safety.py test_import_streams.py test_linux_platform_smoke.py test_portable_profile.py test_store_materials.py test_sync_worker.py
python run_tests.py
```

GitHub Actions runs the same smoke tests on Python 3.10, 3.11, and 3.12.

## Privacy and Local Files

`ProSync_config.json`, logs, build artifacts, and local host notes stay outside the repository. The tracked `ProSync_config.example.json` contains only an empty example structure and no personal source or target paths.

The GitHub repository only tracks source code, tests, sample configuration, and project documentation. Personal sync targets, databases, WAL files, temporary locks, and local build outputs are excluded through `.gitignore`.

Please report security vulnerabilities through GitHub's private vulnerability reporting flow in the **Security** tab instead of opening a public issue.

### Batch Execution

Select multiple tasks with `Ctrl` or `Shift` in the list and launch them together via
`▶ Batch starten` or the context menu. ProSync runs the selection sequentially,
ignores duplicate IDs, and stops the batch cleanly on errors or manual cancellation.

## Synchronization Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **mirror** | Target = exact copy of source | Full backup |
| **update** | Transfer only newer files | Incremental backup |
| **two_way** | Bidirectional synchronization | Sync between two workstations |
| **one_way** | Source → target only, no deletions | Safe archiving |
| **index_only** | Indexing only, no copying | File management without sync |

## Example Scenarios

### 1. Project Folder Backup

**Task:** Daily backup of a development project

**Configuration:**
- **Source:** `C:\Projekte\MeinProjekt`
- **Target:** `D:\Backups\MeinProjekt`
- **Mode:** `mirror`
- **Scheduled:** Daily at 6:00 PM
- **Indexing:** Enabled (for search)

**Result:** Complete backup with file versioning and search functionality

### 2. Synchronization Between Laptop and Desktop

**Task:** Synchronize files between two PCs

**Configuration:**
- **Source:** `C:\Dokumente`
- **Target:** `\\Desktop-PC\Dokumente`
- **Mode:** `two_way`
- **Scheduled:** Every 30 minutes
- **Conflict Resolution:** `newest` (newest file wins)

**Result:** Bidirectional sync, both PCs always have the latest files

### 3. Database Backup (SQLite with WAL Mode)

**Task:** Safe backup of a SQLite database

**Configuration:**
- **Type:** File connection (not folder!)
- **Source:** `C:\App\data.db`
- **Target:** `D:\Backups\data.db`
- **Mode:** `one_way`
- **WAL Checkpoint:** Enabled
- **Scheduled:** Every 4 hours

**Result:** Consistent DB backups without corruption

## Database Protection (V3.2)

ProSync automatically detects critical databases and applies safe settings:

### Supported Database Types

- **SQLite** (.sqlite, .sqlite3, .db, .db3)
- **MS Access** (.mdb, .accdb)

### Automatic Safety Measures

#### For Folder Connections:
- Critical DBs (in WAL mode) are **automatically excluded**
- WAL files (.db-wal, .db-shm, .db-journal) are **never copied**
- Recommendation: Create **file connections** for individual DBs

#### For File Connections:
- **WAL Checkpoint** is automatically enabled
- **One-way mode** is recommended
- Checkpoint before each copy operation

### What is WAL Checkpoint?

WAL (Write-Ahead Logging) stores SQLite changes in a separate `-wal` file.
A checkpoint merges these changes back into the main DB file.

**Without checkpoint:** Inconsistent backups possible!
**With checkpoint:** Intended to create a consistent DB copy, depending on SQLite checkpoint behavior.

## Configuration File

`ProSync_config.json` - Automatically created and managed locally. The file is ignored because it can contain personal source/target paths.
A safe example is tracked as `ProSync_config.example.json`.

### Example (Folder Connection):

```json
{
  "connections": [
    {
      "id": "conn-abc123",
      "name": "Projekt Backup",
      "type": "folder",
      "source": "C:\\Projekte\\MeinProjekt",
      "target": "D:\\Backups\\MeinProjekt",
      "mode": "mirror",
      "conflict_policy": "source",
      "indexing": true,
      "db_path": "C:\\Projekte\\MeinProjekt\\profiler_index.db",
      "exclude_patterns": ["*.tmp", "*.lock", "__pycache__"],
      "autosync": {
        "enabled": true,
        "interval_minutes": 60
      }
    }
  ]
}
```

### Example (File Connection):

```json
{
  "connections": [
    {
      "id": "conn-def456",
      "name": "Datenbank Backup",
      "type": "file",
      "source_file": "C:\\App\\data.db",
      "target_file": "D:\\Backups\\data.db",
      "mode": "one_way",
      "checkpoint_before_sync": true,
      "autosync": {
        "enabled": true,
        "interval_minutes": 240
      }
    }
  ]
}
```

## ProSyncReader

A separate tool for searching the sync databases.

```bash
python ProSyncReader.py
```

**Features:**
- Full-text search in synchronized files
- Tag-based search
- File preview (PDF, DOCX)
- Direct opening of files/folders

## ProFiler Companion

ProSync can launch ProFiler directly from the main window. The search checks
`app.profiler_path` in `ProSync_config.json` first, then local default paths,
and finally the shared `REL-PUB_ProFiler` software tree. Configured paths may
be absolute, relative to the ProSync folder, or use environment variables such
as `%USERPROFILE%\\...`.

## Tips & Best Practices

### Recommended:
- Use **file connections** for individual databases
- Enable **WAL Checkpoint** for SQLite DBs
- Test new connections with a **manual sync** first
- Use **exclude_patterns** for temporary files

### Avoid:
- Use **two_way** for critical databases
- Synchronize **running** applications
- Copy **.db-wal** files manually
- Use **mirror** if you don't want deletions

## Troubleshooting

### "Checkpoint failed"
Database is currently open/locked. Close the application or increase the timeout.

### "Sync hangs"
Large files or slow network connection. Use `update` instead of `mirror` for faster syncs.

### "File was excluded"
Check `exclude_patterns` in the config. Critical DBs are automatically excluded (for folder connections).

## System Tray Commands

- **Left-click:** Open main window
- **Right-click → Run:** Start connection manually
- **Right-click → Auto-run:** Enable scheduled sync
- **Right-click → Exit:** Quit ProSync

## License

MIT - See [LICENSE](LICENSE)

This project uses PySide6 (LGPL).
