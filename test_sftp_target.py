"""Regression tests for SFTP target connections."""

from __future__ import annotations

import importlib.util
import json
import os
import stat
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication


def load_prosync_module():
    module_path = Path(__file__).with_name("ProSyncStart_V3.1.py")
    spec = importlib.util.spec_from_file_location("prosync_sftp", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeAttr:
    def __init__(self, filename: str, mode: int, size: int = 0, mtime: float = 0):
        self.filename = filename
        self.st_mode = mode
        self.st_size = size
        self.st_mtime = mtime


class FakeSftp:
    def __init__(self):
        self.dirs = {"/"}
        self.files: dict[str, dict] = {}
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
        prefix = "" if path == "/" else path
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

    def put(self, local_path: str, remote_path: str) -> None:
        remote_path = self._norm(remote_path)
        parent = self._parent(remote_path)
        if parent not in self.dirs:
            raise FileNotFoundError(parent)
        self.files[remote_path] = {
            "content": Path(local_path).read_bytes(),
            "mtime": os.path.getmtime(local_path),
        }

    def rename(self, old: str, new: str) -> None:
        old = self._norm(old)
        new = self._norm(new)
        self.files[new] = self.files.pop(old)

    def utime(self, path: str, times) -> None:
        path = self._norm(path)
        self.files[path]["mtime"] = times[1]

    def remove(self, path: str) -> None:
        path = self._norm(path)
        del self.files[path]

    def close(self) -> None:
        self.closed = True


class FakeSsh:
    def __init__(self):
        self.closed = False

    def close(self) -> None:
        self.closed = True


def _base_config(tmp_path: Path) -> dict:
    return {
        "id": "sftp-1",
        "name": "Mac Mirror",
        "type": "sftp",
        "source": str(tmp_path / "src"),
        "target": "/backup/prosync",
        "remote_host": "macstudio.tailnet",
        "remote_port": 22,
        "remote_username": "lukas",
        "mode": "mirror",
        "exclude_patterns": ["*.tmp"],
        "autosync": {"enabled": False, "interval_minutes": 30},
    }


def test_sftp_worker_uploads_and_deletes_mirror_stale_files(tmp_path: Path) -> None:
    QCoreApplication.instance() or QCoreApplication([])
    prosync = load_prosync_module()
    src = tmp_path / "src"
    (src / "nested").mkdir(parents=True)
    (src / "keep.txt").write_text("same", encoding="utf-8")
    (src / "changed.txt").write_text("new content", encoding="utf-8")
    (src / "nested" / "fresh.txt").write_text("fresh", encoding="utf-8")
    (src / "skip.tmp").write_text("skip", encoding="utf-8")

    fake_sftp = FakeSftp()
    fake_ssh = FakeSsh()
    fake_sftp.mkdir("/backup")
    fake_sftp.mkdir("/backup/prosync")
    fake_sftp.files["/backup/prosync/keep.txt"] = {
        "content": b"same",
        "mtime": os.path.getmtime(src / "keep.txt"),
    }
    fake_sftp.files["/backup/prosync/changed.txt"] = {"content": b"old", "mtime": 1}
    fake_sftp.files["/backup/prosync/stale.txt"] = {"content": b"delete me", "mtime": 1}

    reports = []
    errors = []
    worker = prosync.SftpTargetSyncWorker(
        _base_config(tmp_path),
        transport_factory=lambda _cfg: (fake_ssh, fake_sftp),
    )
    worker.sync_report.connect(reports.append)
    worker.error.connect(errors.append)
    worker.run()

    assert errors == []
    assert reports[-1]["target_type"] == "sftp"
    assert reports[-1]["files_copied"] == 2
    assert reports[-1]["files_deleted"] == 1
    assert fake_sftp.files["/backup/prosync/changed.txt"]["content"] == b"new content"
    assert fake_sftp.files["/backup/prosync/nested/fresh.txt"]["content"] == b"fresh"
    assert "/backup/prosync/stale.txt" not in fake_sftp.files
    assert "/backup/prosync/skip.tmp" not in fake_sftp.files
    assert fake_sftp.closed is True
    assert fake_ssh.closed is True


def test_sftp_config_rejects_database_checkpoint_mode(tmp_path: Path) -> None:
    prosync = load_prosync_module()
    src = tmp_path / "src"
    src.mkdir()
    cfg = _base_config(tmp_path)
    cfg["checkpoint_before_sync"] = True

    try:
        prosync.validate_sftp_connection(cfg)
    except ValueError as exc:
        assert "nicht datenbanksicher" in str(exc)
    else:
        raise AssertionError("SFTP checkpoint configuration should be rejected")


def test_sftp_portable_profile_redacts_remote_endpoint(tmp_path: Path) -> None:
    prosync = load_prosync_module()
    cfg_path = tmp_path / "ProSync_config.json"
    export_path = tmp_path / "portable.json"
    config = prosync.ConfigManager(str(cfg_path))
    config.data = {
        "app": {},
        "connections": [_base_config(tmp_path)],
    }

    payload = config.export_portable_profile(str(export_path))
    exported_text = export_path.read_text(encoding="utf-8")

    assert payload["connections"][0]["type"] == "sftp"
    assert "macstudio.tailnet" not in exported_text
    assert "/backup/prosync" not in exported_text
    assert "remote_warning" in payload["connections"][0]

    imported = prosync.ConfigManager(str(tmp_path / "Imported.json"))
    imported.import_portable_profile(str(export_path))
    imported_conn = imported.list_connections()[0]

    assert imported_conn["type"] == "sftp"
    assert imported_conn["remote_host"] == ""
    assert imported_conn["target"] == ""
    assert imported_conn["_portable_import"]["requires_mapping"] is True


def main() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        test_sftp_worker_uploads_and_deletes_mirror_stale_files(base / "worker")
        test_sftp_config_rejects_database_checkpoint_mode(base / "validate")
        test_sftp_portable_profile_redacts_remote_endpoint(base / "portable")
    print("SFTP target tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
