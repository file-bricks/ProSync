"""Hermetische Vertragstests für Staging-Isolierung, Scan-Abwehr und SFTP-Härtung.

Prüft:
1. SyncWalker schließt ProSync-eigene Staging- und Backup-Dateien standardmäßig aus.
2. SFTP _scan_remote_tree schließt temporäre Upload- und Backup-Stages aus.
3. SFTP _make_remote_tmp_path erzeugt kollisionsfreie, eindeutige Staging-Pfade.
4. FolderSyncWorker überträgt oder löscht niemals Stage-Dateien bei überlappenden Scans.
"""

from __future__ import annotations

import importlib.util
import os
import stat
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtCore import QCoreApplication


def _load_prosync():
    repo_root = Path(__file__).resolve().parent.parent
    main_file = repo_root / "ProSyncStart_V3.1.py"
    spec = importlib.util.spec_from_file_location("prosync_main", str(main_file))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeAttr:
    def __init__(self, filename: str, mode: int, size: int, mtime: float):
        self.filename = filename
        self.st_mode = mode
        self.st_size = size
        self.st_mtime = mtime


class FakeSftp:
    def __init__(self):
        self.dirs = {"/"}
        self.files: dict[str, dict[str, Any]] = {}
        self.closed = False

    @staticmethod
    def _norm(path: str) -> str:
        path = str(path).replace("\\", "/")
        if not path.startswith("/"):
            path = "/" + path
        while "//" in path:
            path = path.replace("//", "/")
        return path.rstrip("/") or "/"

    def mkdir(self, path: str) -> None:
        self.dirs.add(self._norm(path))

    def stat(self, path: str):
        path = self._norm(path)
        if path in self.dirs:
            return FakeAttr(Path(path).name, stat.S_IFDIR, 0, 0)
        if path in self.files:
            item = self.files[path]
            return FakeAttr(Path(path).name, stat.S_IFREG, len(item["content"]), item["mtime"])
        raise FileNotFoundError(path)

    def listdir_attr(self, path: str):
        path = self._norm(path)
        children = []
        for directory in sorted(self.dirs):
            if directory == path:
                continue
            if self._parent(directory) == path:
                children.append(FakeAttr(directory.rsplit("/", 1)[-1], stat.S_IFDIR, 0, 0))
        for file_path, item in sorted(self.files.items()):
            if self._parent(file_path) == path:
                children.append(
                    FakeAttr(
                        file_path.rsplit("/", 1)[-1],
                        stat.S_IFREG,
                        len(item["content"]),
                        item["mtime"],
                    )
                )
        return children

    def _parent(self, path: str) -> str:
        path = self._norm(path)
        parent = path.rsplit("/", 1)[0]
        return parent or "/"


def test_sync_walker_excludes_internal_staging_patterns_by_default(tmp_path: Path):
    prosync = _load_prosync()
    walker = prosync.SyncWalker()

    (tmp_path / "valid.txt").write_text("payload", encoding="utf-8")
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "valid2.txt").write_text("payload2", encoding="utf-8")

    # In-flight stages
    (tmp_path / ".prosync-copy123.tmp").write_text("stage1", encoding="utf-8")
    (sub / ".prosync-nested456.tmp").write_text("stage2", encoding="utf-8")
    (tmp_path / "doc.pdf.prosync_tmp_abcdef").write_text("stage3", encoding="utf-8")
    (tmp_path / "archive.zip.prosync_backup_fedcba").write_text("stage4", encoding="utf-8")
    (sub / "notes.txt.prosync_tmp").write_text("stage5", encoding="utf-8")

    tree = walker.scan(str(tmp_path))
    normalized_keys = {k.replace("\\", "/") for k in tree.keys()}

    assert normalized_keys == {"valid.txt", "subdir/valid2.txt"}
    for excluded in [
        ".prosync-copy123.tmp",
        "subdir/.prosync-nested456.tmp",
        "doc.pdf.prosync_tmp_abcdef",
        "archive.zip.prosync_backup_fedcba",
        "subdir/notes.txt.prosync_tmp",
    ]:
        assert excluded not in normalized_keys


def test_sync_walker_should_exclude_behavior():
    prosync = _load_prosync()
    walker = prosync.SyncWalker()

    assert walker._should_exclude(".prosync-stage123.tmp", []) is True
    assert walker._should_exclude("doc.pdf.prosync_tmp_abcd", []) is True
    assert walker._should_exclude("archive.zip.prosync_backup_xyz", []) is True
    assert walker._should_exclude("file.txt.prosync_tmp", []) is True
    assert walker._should_exclude("normal_file.txt", []) is False
    assert walker._should_exclude(".prosync-stage123.tmp", [], include_internal=False) is False


def test_sftp_scan_remote_tree_excludes_stage_and_backup_files():
    prosync = _load_prosync()
    fake_sftp = FakeSftp()
    fake_sftp.mkdir("/remote")
    fake_sftp.files["/remote/regular.txt"] = {"content": b"live", "mtime": 100.0}
    fake_sftp.files["/remote/regular.txt.prosync_tmp_123"] = {"content": b"tmp", "mtime": 101.0}
    fake_sftp.files["/remote/regular.txt.prosync_backup_456"] = {"content": b"bak", "mtime": 99.0}
    fake_sftp.files["/remote/.prosync-789.tmp"] = {"content": b"stage", "mtime": 102.0}

    worker = prosync.SftpTargetSyncWorker(
        {"id": "test", "name": "SFTP", "source": ".", "target": "/remote"}
    )
    tree = worker._scan_remote_tree(fake_sftp, "/remote")

    assert set(tree.keys()) == {"regular.txt"}
    assert tree["regular.txt"]["mtime"] == 100.0


def test_sftp_make_remote_tmp_path_generates_unique_paths():
    prosync = _load_prosync()
    worker = prosync.SftpTargetSyncWorker(
        {"id": "test", "name": "SFTP", "source": ".", "target": "/remote"}
    )
    target = "/remote/important.dat"
    paths = [worker._make_remote_tmp_path(target) for _ in range(20)]

    assert len(set(paths)) == 20
    for p in paths:
        assert p.startswith("/remote/important.dat.prosync_tmp_")
        assert len(p) > len("/remote/important.dat.prosync_tmp_")


def test_folder_sync_worker_stage_files_not_synced_or_deleted(tmp_path: Path):
    QCoreApplication.instance() or QCoreApplication([])
    prosync = _load_prosync()

    src = tmp_path / "src"
    tgt = tmp_path / "tgt"
    src.mkdir()
    tgt.mkdir()

    (src / "real_source.txt").write_text("source_content", encoding="utf-8")
    (tgt / "real_target.txt").write_text("target_content", encoding="utf-8")

    # Stages in src and tgt
    (src / ".prosync-src-stage.tmp").write_text("src_stage", encoding="utf-8")
    (src / "doc.prosync_tmp_111").write_text("src_tmp", encoding="utf-8")
    (tgt / ".prosync-tgt-stage.tmp").write_text("tgt_stage", encoding="utf-8")
    (tgt / "backup.prosync_backup_222").write_text("tgt_backup", encoding="utf-8")

    cfg = {
        "id": "c1",
        "name": "TestSync",
        "source": str(src),
        "target": str(tgt),
        "mode": "two_way",
        "conflict_policy": "source",
    }

    worker = prosync.FolderSyncWorker(cfg)
    reports = []
    worker.sync_report.connect(reports.append)
    worker.run()

    # Verify real files synced
    assert (tgt / "real_source.txt").exists()
    assert (src / "real_target.txt").exists()

    # Verify stages in src were NOT replicated to tgt
    assert not (tgt / ".prosync-src-stage.tmp").exists()
    assert not (tgt / "doc.prosync_tmp_111").exists()

    # Verify stages in tgt were NOT replicated to src
    assert not (src / ".prosync-tgt-stage.tmp").exists()
    assert not (src / "backup.prosync_backup_222").exists()

    # Verify stages were not destroyed/deleted
    assert (src / ".prosync-src-stage.tmp").exists()
    assert (tgt / ".prosync-tgt-stage.tmp").exists()
