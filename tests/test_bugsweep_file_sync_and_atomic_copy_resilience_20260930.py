import os
import stat
import tempfile
import time
import threading
import importlib.util
from pathlib import Path
import pytest
from PySide6.QtCore import QCoreApplication

# Load ProSyncStart_V3.1.py dynamically
root_dir = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "prosync_v31",
    str(root_dir / "ProSyncStart_V3.1.py"),
)
prosync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prosync)


@pytest.fixture(autouse=True)
def ensure_qapp():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


def test_file_sync_emits_sync_report():
    """Bug: FileSyncWorker had no sync_report Signal and emitted no report."""
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "source.db")
        tgt = os.path.join(td, "target.db")
        with open(src, "w", encoding="utf-8") as f:
            f.write("SAMPLE-DATA-12345")

        cfg = {
            "name": "TestFileConn",
            "id": "conn-test-file",
            "source_file": src,
            "target_file": tgt,
            "mode": "one_way",
        }
        worker = prosync.FileSyncWorker(cfg)
        reports = []
        finished = []
        errors = []

        assert hasattr(worker, "sync_report"), "FileSyncWorker must define sync_report Signal"
        worker.sync_report.connect(reports.append)
        worker.finished.connect(lambda: finished.append(True))
        worker.error.connect(errors.append)

        worker.run()

        assert not errors, f"Unexpected errors: {errors}"
        assert finished == [True], "finished should be emitted"
        assert len(reports) == 1, "Exactly one sync_report should be emitted"
        rep = reports[0]
        assert rep["connection"] == "TestFileConn"
        assert rep["connection_id"] == "conn-test-file"
        assert rep["files_copied"] == 1
        assert rep["bytes_copied"] == os.path.getsize(tgt)
        assert rep["files_deleted"] == 0
        assert rep["files_skipped"] == 0


def test_file_sync_missing_target_fails_verification(monkeypatch):
    """Bug: If target_file does not exist, verification was skipped and success emitted."""
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "source.db")
        tgt = os.path.join(td, "target.db")
        with open(src, "w", encoding="utf-8") as f:
            f.write("SAMPLE-DATA")

        # Mock _atomic_copy2 to simulate a silent failure where target is missing
        monkeypatch.setattr(prosync, "_atomic_copy2", lambda s, d: None)

        cfg = {
            "name": "MissingTargetTest",
            "id": "conn-missing-tgt",
            "source_file": src,
            "target_file": tgt,
            "mode": "one_way",
        }
        worker = prosync.FileSyncWorker(cfg)
        finished = []
        errors = []
        worker.finished.connect(lambda: finished.append(True))
        worker.error.connect(errors.append)

        worker.run()

        assert not finished, "finished must NOT be emitted when target file does not exist"
        assert len(errors) == 1, "An error must be emitted when target file is missing"
        assert "nicht gefunden" in errors[0]


def test_file_sync_rejects_directory_source():
    """Bug: Supplying a directory as source_file crashed with unhandled exception."""
    with tempfile.TemporaryDirectory() as td:
        src_dir = os.path.join(td, "source_folder")
        os.makedirs(src_dir, exist_ok=True)
        tgt = os.path.join(td, "target.db")

        cfg = {
            "name": "DirSourceTest",
            "id": "conn-dir-src",
            "source_file": src_dir,
            "target_file": tgt,
            "mode": "one_way",
        }
        worker = prosync.FileSyncWorker(cfg)
        finished = []
        errors = []
        worker.finished.connect(lambda: finished.append(True))
        worker.error.connect(errors.append)

        worker.run()

        assert not finished
        assert len(errors) == 1
        assert "Verzeichnis" in errors[0]


def test_file_sync_rejects_identical_source_and_target():
    """Bug: Source and target could be the same file, causing useless copy/temp-replace."""
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "same.db")
        with open(src, "w", encoding="utf-8") as f:
            f.write("DATA")

        cfg = {
            "name": "SameFileTest",
            "id": "conn-same",
            "source_file": src,
            "target_file": src,
            "mode": "one_way",
        }
        worker = prosync.FileSyncWorker(cfg)
        finished = []
        errors = []
        worker.finished.connect(lambda: finished.append(True))
        worker.error.connect(errors.append)

        worker.run()

        assert not finished
        assert len(errors) == 1
        assert "identisch" in errors[0]


def test_file_sync_respects_pause(ensure_qapp):
    """Bug: FileSyncWorker ignored is_paused and ran through immediately."""
    app = ensure_qapp
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "source.db")
        tgt = os.path.join(td, "target.db")
        with open(src, "w", encoding="utf-8") as f:
            f.write("PAUSE-TEST-DATA")

        cfg = {
            "name": "PauseTest",
            "id": "conn-pause",
            "source_file": src,
            "target_file": tgt,
            "mode": "one_way",
        }
        worker = prosync.FileSyncWorker(cfg)
        worker.pause()
        assert worker.is_paused is True

        finished = []
        worker.finished.connect(lambda: finished.append(True))

        t = threading.Thread(target=worker.run)
        t.start()

        # Give it 0.2s: while paused, it should NOT complete
        time.sleep(0.2)
        app.processEvents()
        assert not finished, "Worker must pause and not finish while is_paused is True"

        # Now resume
        worker.resume()
        t.join(timeout=3.0)
        app.processEvents()

        assert finished == [True], "Worker should finish once resumed"
        assert os.path.exists(tgt)


def test_atomic_copy2_overwrites_readonly_destination():
    """Bug: os.replace fails with PermissionError [WinError 5] when dst has read-only attribute on Windows."""
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "src.db")
        dst = os.path.join(td, "dst.db")
        with open(src, "w", encoding="utf-8") as f:
            f.write("UPDATED_CONTENT_2026")
        with open(dst, "w", encoding="utf-8") as f:
            f.write("OLD_CONTENT")

        # Make destination read-only
        os.chmod(dst, stat.S_IREAD)

        # Must succeed without PermissionError
        prosync._atomic_copy2(src, dst)

        with open(dst, "r", encoding="utf-8") as f:
            assert f.read() == "UPDATED_CONTENT_2026"


def test_atomic_copy2_cleans_readonly_tmp_on_failure(monkeypatch):
    """Bug: If source is read-only, shutil.copy2 copies read-only to tmp, and os.remove(tmp) failed on error."""
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "src_ro.db")
        dst = os.path.join(td, "dst.db")
        tmp = f"{dst}.prosync_tmp"

        with open(src, "w", encoding="utf-8") as f:
            f.write("READONLY_SOURCE")
        os.chmod(src, stat.S_IREAD)

        # Force os.replace to raise an OSError to trigger cleanup in except block
        def broken_replace(s, d):
            raise OSError("Simulated replace failure")

        monkeypatch.setattr(os, "replace", broken_replace)

        with pytest.raises(OSError, match="Simulated replace failure"):
            prosync._atomic_copy2(src, dst)

        assert not os.path.exists(tmp), "Temporary file must be cleaned up even if marked read-only"


def test_folder_sync_worker_deletes_readonly_file_in_mirror_mode():
    """Bug: In mirror mode, DELETE_R failed with PermissionError if remote file was read-only."""
    with tempfile.TemporaryDirectory() as td:
        src_root = os.path.join(td, "source")
        tgt_root = os.path.join(td, "target")
        os.makedirs(src_root, exist_ok=True)
        os.makedirs(tgt_root, exist_ok=True)

        # Create obsolete file in target
        obsolete_file = os.path.join(tgt_root, "obsolete.txt")
        with open(obsolete_file, "w", encoding="utf-8") as f:
            f.write("OBSOLETE")
        os.chmod(obsolete_file, stat.S_IREAD)

        cfg = {
            "name": "MirrorTest",
            "id": "conn-mirror-ro",
            "source": src_root,
            "target": tgt_root,
            "mode": "mirror",
            "conflict_policy": "source",
        }
        worker = prosync.FolderSyncWorker(cfg)
        errors = []
        finished = []
        worker.error.connect(errors.append)
        worker.finished.connect(lambda: finished.append(True))

        worker.run()

        assert not errors, f"FolderSyncWorker failed: {errors}"
        assert finished == [True]
        assert not os.path.exists(obsolete_file), "Read-only obsolete file must be deleted"
