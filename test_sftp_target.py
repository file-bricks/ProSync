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
    src.mkdir(parents=True)
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


class _FakeHostKeys:
    def __init__(self):
        self.entries: dict[str, tuple] = {}

    def lookup(self, name):
        return self.entries.get(name)

    def add(self, hostname, keytype, key):
        self.entries[hostname] = (keytype, key)


class _FakeServerKey:
    @staticmethod
    def get_name():
        return "ssh-ed25519"


def _install_fake_paramiko_client(monkeypatch, preseed_host_keys=None):
    """Replace paramiko.SSHClient/Transport with recording fakes; real Policy classes stay."""
    import paramiko

    clients: list = []
    transports: list = []
    preseed = dict(preseed_host_keys or {})

    class FakeSSHClient:
        def __init__(self):
            self.policy = None
            self.loaded_host_key_files: list[str] = []
            self.saved_host_key_files: list[str] = []
            self.connect_kwargs: dict | None = None
            self._host_keys = _FakeHostKeys()
            self._host_keys.entries.update(preseed)
            clients.append(self)

        def load_system_host_keys(self):
            pass

        def load_host_keys(self, filename):
            self.loaded_host_key_files.append(filename)

        def save_host_keys(self, filename):
            self.saved_host_key_files.append(filename)

        def get_host_keys(self):
            return self._host_keys

        def set_missing_host_key_policy(self, policy):
            self.policy = policy

        def connect(self, **kwargs):
            self.connect_kwargs = kwargs

        def open_sftp(self):
            return "FAKE_SFTP_HANDLE"

    class FakeTransport:
        def __init__(self, sock):
            self.sock = sock
            self.start_timeout = None
            self.closed = False
            transports.append(self)

        def start_client(self, timeout=None):
            self.start_timeout = timeout

        def get_remote_server_key(self):
            return _FakeServerKey()

        def close(self):
            self.closed = True

    monkeypatch.setattr(paramiko, "SSHClient", FakeSSHClient)
    monkeypatch.setattr(paramiko, "Transport", FakeTransport)
    return clients, transports


def test_create_sftp_transport_pins_unknown_host_key_via_tofu(tmp_path: Path, monkeypatch) -> None:
    """First-ever connect with allow_unknown_host_key must fetch+pin the key, never bypass validation."""
    import paramiko

    monkeypatch.setenv("APPDATA", str(tmp_path))
    (tmp_path / "src").mkdir(parents=True)
    prosync = load_prosync_module()
    clients, transports = _install_fake_paramiko_client(monkeypatch)

    cfg = _base_config(tmp_path)
    cfg["allow_unknown_host_key"] = True

    client, sftp = prosync.create_sftp_transport(cfg)

    assert sftp == "FAKE_SFTP_HANDLE"
    assert isinstance(client.policy, paramiko.RejectPolicy)
    assert len(transports) == 1, "unknown host must trigger exactly one TOFU probe"
    assert transports[0].closed is True
    assert client._host_keys.entries, "server key must be pinned after first contact"
    assert client.saved_host_key_files, "pinned key must be persisted to known_hosts"
    assert client.connect_kwargs["hostname"] == cfg["remote_host"]
    assert (tmp_path / "ProSync" / "known_hosts").parent.exists()


def test_create_sftp_transport_never_bypasses_validation_when_disabled(tmp_path: Path, monkeypatch) -> None:
    """With the opt-in off, no TOFU probe may run and RejectPolicy stays in force (fail closed)."""
    import paramiko

    monkeypatch.setenv("APPDATA", str(tmp_path))
    (tmp_path / "src").mkdir(parents=True)
    prosync = load_prosync_module()
    clients, transports = _install_fake_paramiko_client(monkeypatch)

    cfg = _base_config(tmp_path)
    cfg["allow_unknown_host_key"] = False

    client, _sftp = prosync.create_sftp_transport(cfg)

    assert isinstance(client.policy, paramiko.RejectPolicy)
    assert transports == [], "no TOFU probe without explicit opt-in"
    assert not client._host_keys.entries


def test_create_sftp_transport_skips_probe_for_already_pinned_host(tmp_path: Path, monkeypatch) -> None:
    """A host that is already known must not trigger a new TOFU probe (no silent re-trust on key change)."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    (tmp_path / "src").mkdir(parents=True)
    prosync = load_prosync_module()

    cfg = _base_config(tmp_path)
    cfg["allow_unknown_host_key"] = True
    host_key_name = prosync._ssh_host_key_name(cfg["remote_host"], cfg["remote_port"])
    assert host_key_name == cfg["remote_host"]  # default port 22 -> no bracket/port suffix

    pinned_key = ("ssh-ed25519", "already-known-key")
    clients, transports = _install_fake_paramiko_client(
        monkeypatch, preseed_host_keys={host_key_name: pinned_key}
    )

    client, _sftp = prosync.create_sftp_transport(cfg)

    assert transports == [], "already-known host must not trigger a new TOFU probe"
    assert client._host_keys.entries[host_key_name] == pinned_key


class _SimpleMonkeyPatch:
    """Minimal stand-in for pytest's `monkeypatch` fixture, for the standalone `main()` runner.

    No undo on teardown -- fine here since `main()` runs each test in a fresh subprocess-like
    one-shot invocation and exits right after.
    """

    @staticmethod
    def setattr(obj, name, value):
        setattr(obj, name, value)

    @staticmethod
    def setenv(name, value):
        os.environ[name] = value


def main() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        test_sftp_worker_uploads_and_deletes_mirror_stale_files(base / "worker")
        test_sftp_config_rejects_database_checkpoint_mode(base / "validate")
        test_sftp_portable_profile_redacts_remote_endpoint(base / "portable")
        test_create_sftp_transport_pins_unknown_host_key_via_tofu(base / "tofu1", _SimpleMonkeyPatch())
        test_create_sftp_transport_never_bypasses_validation_when_disabled(base / "tofu2", _SimpleMonkeyPatch())
        test_create_sftp_transport_skips_probe_for_already_pinned_host(base / "tofu3", _SimpleMonkeyPatch())
    print("SFTP target tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
