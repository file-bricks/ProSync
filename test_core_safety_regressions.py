"""Regression tests for fail-closed sync and configuration safety."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication


def load_prosync_module():
    module_path = Path(__file__).with_name("ProSyncStart_V3.1.py")
    spec = importlib.util.spec_from_file_location("prosync_core_safety", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_folder_config(source: Path, target: Path, mode: str = "mirror") -> dict:
    return {
        "id": "safety-test",
        "name": "Safety Test",
        "source": str(source),
        "target": str(target),
        "mode": mode,
    }


def capture_worker(worker):
    errors = []
    finished = []
    reports = []
    worker.error.connect(errors.append)
    worker.finished.connect(lambda: finished.append(True))
    if hasattr(worker, "sync_report"):
        worker.sync_report.connect(reports.append)
    worker.run()
    return errors, finished, reports


def test_folder_mirror_missing_source_preserves_target(tmp_path):
    QCoreApplication.instance() or QCoreApplication([])
    prosync = load_prosync_module()
    source = tmp_path / "missing-source"
    target = tmp_path / "target"
    target.mkdir()
    protected = target / "keep.txt"
    protected.write_text("keep", encoding="utf-8")

    errors, finished, reports = capture_worker(
        prosync.FolderSyncWorker(make_folder_config(source, target))
    )

    assert errors and "Quellordner nicht gefunden" in errors[0]
    assert finished == []
    assert reports == []
    assert protected.read_text(encoding="utf-8") == "keep"


def test_folder_mirror_unreadable_source_preserves_target(tmp_path, monkeypatch):
    QCoreApplication.instance() or QCoreApplication([])
    prosync = load_prosync_module()
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    protected = target / "keep.txt"
    protected.write_text("keep", encoding="utf-8")
    real_walk = prosync.os.walk

    def failing_walk(root, *args, **kwargs):
        if str(root) == str(source):
            kwargs["onerror"](PermissionError("access denied"))
            return iter(())
        return real_walk(root, *args, **kwargs)

    monkeypatch.setattr(prosync.os, "walk", failing_walk)
    errors, finished, reports = capture_worker(
        prosync.FolderSyncWorker(make_folder_config(source, target))
    )

    assert errors and "Ordner kann nicht gelesen werden" in errors[0]
    assert finished == []
    assert reports == []
    assert protected.exists()


@pytest.mark.parametrize("nested_side", ["source", "target", "same"])
def test_folder_sync_rejects_overlapping_roots(tmp_path, nested_side):
    QCoreApplication.instance() or QCoreApplication([])
    prosync = load_prosync_module()
    outer = tmp_path / "outer"
    inner = outer / "inner"
    inner.mkdir(parents=True)
    protected = inner / "keep.txt"
    protected.write_text("keep", encoding="utf-8")

    if nested_side == "source":
        source, target = outer, inner
    elif nested_side == "target":
        source, target = inner, outer
    else:
        source = target = outer

    errors, finished, reports = capture_worker(
        prosync.FolderSyncWorker(make_folder_config(source, target))
    )

    assert errors and "dürfen nicht ineinander liegen" in errors[0]
    assert finished == []
    assert reports == []
    assert protected.read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize("failed_action", ["copy", "delete"])
def test_folder_action_error_never_reports_success(tmp_path, monkeypatch, failed_action):
    QCoreApplication.instance() or QCoreApplication([])
    prosync = load_prosync_module()
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    if failed_action == "copy":
        (source / "copy.txt").write_text("new", encoding="utf-8")

        def fail_copy(_source, _target):
            raise OSError("copy denied")

        monkeypatch.setattr(prosync, "_atomic_copy2", fail_copy)
    else:
        stale = target / "stale.txt"
        stale.write_text("old", encoding="utf-8")
        real_remove = prosync.os.remove

        def fail_delete(path):
            if str(path) == str(stale):
                raise PermissionError("delete denied")
            return real_remove(path)

        monkeypatch.setattr(prosync.os, "remove", fail_delete)

    errors, finished, reports = capture_worker(
        prosync.FolderSyncWorker(make_folder_config(source, target))
    )

    assert errors and "fehlgeschlagen" in errors[0]
    assert finished == []
    assert reports == []


def test_folder_one_way_updates_without_deleting_target_only_files(tmp_path):
    QCoreApplication.instance() or QCoreApplication([])
    prosync = load_prosync_module()
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "changed.txt").write_text("new content", encoding="utf-8")
    (source / "fresh.txt").write_text("fresh", encoding="utf-8")
    (target / "changed.txt").write_text("old", encoding="utf-8")
    stale = target / "target-only.txt"
    stale.write_text("preserve", encoding="utf-8")

    errors, finished, reports = capture_worker(
        prosync.FolderSyncWorker(make_folder_config(source, target, mode="one_way"))
    )

    assert errors == []
    assert finished == [True]
    assert reports and reports[0]["files_copied"] == 2
    assert (target / "changed.txt").read_text(encoding="utf-8") == "new content"
    assert (target / "fresh.txt").read_text(encoding="utf-8") == "fresh"
    assert stale.read_text(encoding="utf-8") == "preserve"


def test_failed_wal_checkpoint_blocks_database_copy(tmp_path, monkeypatch):
    QCoreApplication.instance() or QCoreApplication([])
    prosync = load_prosync_module()
    source = tmp_path / "source.db"
    target = tmp_path / "target.db"
    source.write_bytes(b"database")
    copy_calls = []
    monkeypatch.setattr(
        prosync.DatabaseSafetyManager,
        "checkpoint_sqlite_database",
        classmethod(lambda cls, path: False),
    )
    monkeypatch.setattr(
        prosync,
        "_atomic_copy2",
        lambda source_path, target_path: copy_calls.append((source_path, target_path)),
    )
    worker = prosync.FileSyncWorker(
        {
            "id": "db-safety",
            "name": "Database Safety",
            "source_file": str(source),
            "target_file": str(target),
            "checkpoint_before_sync": True,
        }
    )

    errors, finished, _reports = capture_worker(worker)

    assert errors and "Datenbankkopie abgebrochen" in errors[0]
    assert finished == []
    assert copy_calls == []
    assert not target.exists()


class StrictRenameSftp:
    """SFTP fake whose standard rename refuses an existing destination."""

    def __init__(self, initial=None):
        self.files = dict(initial or {})
        self.rename_calls = []
        self.removed = []

    def stat(self, path):
        if path not in self.files:
            raise FileNotFoundError(path)
        return object()

    def put(self, local_path, remote_path):
        self.files[remote_path] = Path(local_path).read_bytes()

    def rename(self, old, new):
        self.rename_calls.append((old, new))
        if new in self.files:
            raise OSError("destination exists")
        self.files[new] = self.files.pop(old)

    def remove(self, path):
        self.removed.append(path)
        del self.files[path]

    def utime(self, path, times):
        assert path in self.files


class PosixRenameSftp(StrictRenameSftp):
    def __init__(self, initial=None, fail=False):
        super().__init__(initial)
        self.fail = fail
        self.posix_calls = []

    def posix_rename(self, old, new):
        self.posix_calls.append((old, new))
        if self.fail:
            raise OSError("posix rename failed")
        self.files[new] = self.files.pop(old)


def make_sftp_worker(prosync):
    return prosync.SftpTargetSyncWorker(
        {"id": "sftp", "name": "SFTP", "source": ".", "target": "/"}
    )


def test_sftp_overwrite_prefers_posix_rename(tmp_path):
    prosync = load_prosync_module()
    local = tmp_path / "upload.txt"
    local.write_bytes(b"new")
    sftp = PosixRenameSftp({"/file.txt": b"old"})

    make_sftp_worker(prosync)._upload_file(sftp, str(local), "/file.txt")

    assert sftp.files["/file.txt"] == b"new"
    assert sftp.posix_calls == [("/file.txt.prosync_tmp", "/file.txt")]
    assert sftp.rename_calls == []


def test_sftp_overwrite_fallback_moves_old_target_out_of_the_way(tmp_path):
    prosync = load_prosync_module()
    local = tmp_path / "upload.txt"
    local.write_bytes(b"new")
    sftp = StrictRenameSftp({"/file.txt": b"old"})

    make_sftp_worker(prosync)._upload_file(sftp, str(local), "/file.txt")

    assert sftp.files == {"/file.txt": b"new"}
    assert all(old != "/file.txt.prosync_tmp" or new == "/file.txt" for old, new in sftp.rename_calls)


def test_sftp_failed_atomic_replace_cleans_temp_file(tmp_path):
    prosync = load_prosync_module()
    local = tmp_path / "upload.txt"
    local.write_bytes(b"new")
    sftp = PosixRenameSftp({"/file.txt": b"old"}, fail=True)

    with pytest.raises(OSError, match="posix rename failed"):
        make_sftp_worker(prosync)._upload_file(sftp, str(local), "/file.txt")

    assert sftp.files == {"/file.txt": b"old"}
    assert "/file.txt.prosync_tmp" in sftp.removed


@pytest.mark.parametrize("invalid_content", ["{broken json", "[]"])
def test_invalid_config_is_preserved_backed_up_and_blocks_load(tmp_path, invalid_content):
    prosync = load_prosync_module()
    config_path = tmp_path / "ProSync_config.json"
    config_path.write_text(invalid_content, encoding="utf-8")

    with pytest.raises(prosync.ConfigLoadError):
        prosync.ConfigManager(str(config_path))

    assert config_path.read_text(encoding="utf-8") == invalid_content
    backups = list(tmp_path.glob("ProSync_config.json.invalid*.bak"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == invalid_content


def test_scheduler_clamps_huge_interval_to_qtimer_safe_maximum():
    QCoreApplication.instance() or QCoreApplication([])
    prosync = load_prosync_module()

    class Config:
        @staticmethod
        def list_connections():
            return [
                {
                    "id": "huge-interval",
                    "autosync": {"enabled": True, "interval_minutes": 10**20},
                }
            ]

    scheduler = prosync.ConnectionScheduler(Config())
    scheduler.update_all()

    expected = prosync.MAX_AUTOSYNC_INTERVAL_MINUTES * 60 * 1000
    assert scheduler.timers["huge-interval"].interval() == expected
    assert expected <= prosync.MAX_QT_TIMER_INTERVAL_MS
    scheduler.stop_all()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
