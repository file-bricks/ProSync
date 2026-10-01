"""Real filesystem and fault tests for the local copy publication contract."""
import ast
import ctypes
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import threading

import pytest


@pytest.fixture
def copier():
    # Execute the actual helper without starting Qt, scheduling, or user logging.
    source = Path(__file__).resolve().parents[1] / "ProSyncStart_V3.1.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    helper = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                  and n.name == "_atomic_copy2")
    namespace = dict(os=os, shutil=shutil, stat=stat, tempfile=tempfile,
                     log_warning=lambda message: None)
    exec(compile(ast.Module(body=[helper], type_ignores=[]), str(source), "exec"), namespace)
    return namespace["_atomic_copy2"]


@pytest.fixture
def files(tmp_path):
    src, dst = tmp_path / "source", tmp_path / "target"
    foreign = tmp_path / "target.prosync_tmp"
    src.write_bytes(b"new-data")
    dst.write_bytes(b"old-data")
    foreign.write_bytes(b"foreign-data")
    yield src, dst, foreign
    for file in tmp_path.iterdir():
        if file.is_file():
            file.chmod(stat.S_IWRITE | stat.S_IREAD)


def assert_preserved(files):
    src, dst, foreign = files
    assert src.read_bytes() == b"new-data"
    assert dst.read_bytes() == b"old-data"
    assert foreign.read_bytes() == b"foreign-data"
    assert set(dst.parent.iterdir()) == {src, dst, foreign}


def test_foreign_fixed_stage_untouched(copier, files):
    src, dst, foreign = files
    copier(src, dst)
    assert src.read_bytes() == dst.read_bytes() == b"new-data"
    assert foreign.read_bytes() == b"foreign-data"
    assert set(dst.parent.iterdir()) == set(files)


def test_source_is_old_fixed_stage(copier, files):
    _, dst, foreign = files
    copier(foreign, dst)
    assert foreign.read_bytes() == dst.read_bytes() == b"foreign-data"
    assert set(dst.parent.iterdir()) == set(files)


def test_fixed_stage_hardlink_to_original(copier, files):
    src, dst, foreign = files
    foreign.unlink()
    os.link(src, foreign)
    copier(src, dst)
    assert src.read_bytes() == foreign.read_bytes() == dst.read_bytes() == b"new-data"
    assert os.path.samefile(src, foreign)


@pytest.mark.parametrize("alias", ["direct", "relative", "hardlink"])
def test_source_alias_rejected_before_stage(copier, files, monkeypatch, alias):
    src, _, _ = files
    destination = src
    if alias == "hardlink":
        destination = src.parent / "alias"
        os.link(src, destination)
    elif alias == "relative":
        monkeypatch.chdir(src.parent)
        destination = Path("source")
    inode = src.stat().st_ino
    monkeypatch.setattr(tempfile, "mkstemp", lambda **kw: pytest.fail("No stage for source alias"))
    with pytest.raises(shutil.SameFileError):
        copier(src, destination)
    assert src.read_bytes() == b"new-data" and src.stat().st_ino == inode


@pytest.mark.parametrize("failure", ["partial", "metadata", "replace", "interrupt"])
def test_failures_preserve_all_originals(copier, files, monkeypatch, failure):
    error = KeyboardInterrupt("original") if failure == "interrupt" else OSError("original")
    def fail_copy(src, tmp):
        Path(tmp).write_bytes(b"partial")
        raise error
    def fail(*args, **kwargs):
        raise error
    if failure in ("partial", "interrupt"):
        monkeypatch.setattr(shutil, "copy2", fail_copy)
    elif failure == "metadata":
        # Windows CopyFile2 bypasses copystat; exercise the stdlib fallback
        # to inject a metadata failure after copying bytes.
        monkeypatch.setattr(shutil, "_winapi", None, raising=False)
        monkeypatch.setattr(shutil, "copystat", fail)
    else:
        monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(type(error)) as caught:
        copier(files[0], files[1])
    assert caught.value is error
    assert_preserved(files)


def test_missing_source_does_not_touch_foreign_stage(copier, files):
    with pytest.raises(FileNotFoundError):
        copier(files[0].parent / "missing", files[1])
    assert_preserved(files)


def test_reservation_failure_has_no_cleanup(copier, files, monkeypatch):
    def fail(**kw):
        raise PermissionError("reservation")
    monkeypatch.setattr(tempfile, "mkstemp", fail)
    monkeypatch.setattr(os, "remove", lambda p: pytest.fail("No owned stage"))
    with pytest.raises(PermissionError, match="reservation"):
        copier(files[0], files[1])
    assert_preserved(files)


def test_identity_permission_error_is_not_assumed_distinct(copier, files, monkeypatch):
    original_stat = os.stat
    def guarded(path, *args, **kwargs):
        if path == files[1]:
            raise PermissionError("identity")
        return original_stat(path, *args, **kwargs)
    monkeypatch.setattr(os, "stat", guarded)
    with pytest.raises(PermissionError, match="identity"):
        copier(files[0], files[1])
    monkeypatch.setattr(os, "stat", original_stat)
    assert_preserved(files)


def test_late_source_alias_rejected(copier, files, monkeypatch):
    src, dst, foreign = files
    original_copy = shutil.copy2
    def copy_then_alias(source, stage):
        original_copy(source, stage)
        dst.unlink()
        os.link(src, dst)
    monkeypatch.setattr(shutil, "copy2", copy_then_alias)
    with pytest.raises(shutil.SameFileError):
        copier(src, dst)
    assert os.path.samefile(src, dst)
    assert src.read_bytes() == b"new-data" and foreign.read_bytes() == b"foreign-data"
    assert set(src.parent.iterdir()) == set(files)


@pytest.mark.parametrize("readonly", [False, True])
def test_copy_metadata_and_empty_unicode_relative_target(copier, tmp_path, monkeypatch, readonly):
    src = tmp_path / "Quelle äöü"
    src.write_bytes(b"")
    os.utime(src, ns=(1_700_000_000_000_000_000, 1_700_000_001_234_000_000))
    if readonly:
        src.chmod(stat.S_IREAD)
    before = src.stat()
    monkeypatch.chdir(tmp_path)
    try:
        copier(src, "Ziel ü")
        dst = tmp_path / "Ziel ü"
        assert dst.read_bytes() == b""
        assert dst.stat().st_mtime_ns == before.st_mtime_ns
        assert dst.stat().st_mode == before.st_mode
        assert src.stat().st_mode == before.st_mode
        assert set(tmp_path.iterdir()) == {src, dst}
    finally:
        for file in tmp_path.iterdir():
            file.chmod(stat.S_IWRITE | stat.S_IREAD)


def test_readonly_source_replace_failure_cleans_only_owned_stage(copier, files, monkeypatch):
    src, dst, _ = files
    src.chmod(stat.S_IREAD)
    mode = src.stat().st_mode
    def fail(*args):
        raise PermissionError("replace")
    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(PermissionError, match="replace"):
        copier(src, dst)
    assert_preserved(files)
    assert src.stat().st_mode == mode


@pytest.mark.skipif(os.name != "nt", reason="Native Windows readonly publication")
@pytest.mark.parametrize("replace_fails", [False, True])
def test_readonly_target_success_or_rollback(copier, files, monkeypatch, replace_fails):
    src, dst, _ = files
    dst.chmod(stat.S_IREAD)
    before = dst.stat()
    if replace_fails:
        def fail(*args):
            raise PermissionError("replace")
        monkeypatch.setattr(os, "replace", fail)
        with pytest.raises(PermissionError, match="replace"):
            copier(src, dst)
        assert_preserved(files)
        assert dst.stat().st_mode == before.st_mode
        assert dst.stat().st_ino == before.st_ino
    else:
        copier(src, dst)
        assert dst.read_bytes() == b"new-data"
        assert src.read_bytes() == b"new-data"


@pytest.mark.skipif(os.name != "nt", reason="Native Windows readonly hardlink")
def test_readonly_target_hardlink_does_not_change_other_original(copier, files):
    src, dst, _ = files
    original = dst.parent / "third-original"
    os.link(dst, original)
    dst.chmod(stat.S_IREAD)
    mode = original.stat().st_mode
    with pytest.raises(PermissionError, match="Dateialias"):
        copier(src, dst)
    assert dst.read_bytes() == original.read_bytes() == b"old-data"
    assert original.stat().st_mode == mode
    assert set(dst.parent.iterdir()) == {*files, original}


def test_destination_directory_preserved(copier, files):
    src, dst, _ = files
    directory = dst.parent / "folder"
    directory.mkdir()
    with pytest.raises(OSError):
        copier(src, directory)
    assert (src.read_bytes(), dst.read_bytes(), files[2].read_bytes()) == (b"new-data", b"old-data", b"foreign-data")
    assert directory.is_dir()
    assert set(dst.parent.iterdir()) == {*files, directory}


def test_parallel_private_stages(copier, files, monkeypatch):
    src, dst, foreign = files
    second = dst.parent / "second"
    second.write_bytes(b"second-data")
    barrier = threading.Barrier(2)
    stages, successful, failures = [], [], []
    original_copy = shutil.copy2
    def blocked(source, stage):
        original_copy(source, stage)
        stages.append(Path(stage))
        barrier.wait(timeout=10)
    monkeypatch.setattr(shutil, "copy2", blocked)
    def run(source):
        try:
            copier(source, dst)
            successful.append(source.read_bytes())
        except BaseException as error:
            failures.append(error)
    threads = [threading.Thread(target=run, args=(source,)) for source in (src, second)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)
    assert all(not thread.is_alive() for thread in threads)
    assert len(stages) == 2 and stages[0] != stages[1]
    assert successful and dst.read_bytes() in successful
    assert all(os.name == "nt" and isinstance(e, OSError) and e.winerror in (5, 32) for e in failures)
    assert src.read_bytes() == b"new-data" and second.read_bytes() == b"second-data"
    assert foreign.read_bytes() == b"foreign-data"
    assert set(dst.parent.iterdir()) == {*files, second}


@pytest.mark.skipif(os.name != "nt", reason="Native Windows junction alias")
def test_parent_junction_source_alias(copier, files):
    src, _, _ = files
    alias = src.parent.parent / (src.parent.name + "-junction")
    result = subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(src.parent)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    try:
        with pytest.raises(shutil.SameFileError):
            copier(src, alias / src.name)
        assert_preserved(files)
    finally:
        os.rmdir(alias)


@pytest.mark.parametrize("alias_kind", ["fixed-stage", "source-alias", "readonly-target"])
def test_symlink_preserves_referenced_original(copier, files, alias_kind):
    src, dst, foreign = files
    link = foreign if alias_kind == "fixed-stage" else dst
    original = src if alias_kind != "readonly-target" else dst.parent / "third-original"
    if alias_kind == "readonly-target":
        if os.name != "nt":
            pytest.skip("Readonly target release is Windows-specific")
        original.write_bytes(b"third-data")
        original.chmod(stat.S_IREAD)
    mode = original.stat().st_mode
    link.unlink()
    try:
        link.symlink_to(original)
    except OSError as error:
        if os.name == "nt" and error.winerror == 1314:
            pytest.skip("Windows symlink privilege unavailable (1314)")
        raise
    if alias_kind == "fixed-stage":
        copier(src, dst)
        assert link.is_symlink() and dst.read_bytes() == b"new-data"
    elif alias_kind == "source-alias":
        with pytest.raises(shutil.SameFileError):
            copier(src, dst)
        assert link.is_symlink()
    else:
        with pytest.raises(PermissionError, match="Dateialias"):
            copier(src, dst)
        assert link.is_symlink() and original.read_bytes() == b"third-data"
    assert original.stat().st_mode == mode and src.read_bytes() == b"new-data"
    assert not list(dst.parent.glob(".prosync-*.tmp"))


def test_close_failure_keeps_original_error_and_closes_owned_handle(copier, files, monkeypatch):
    original_close = os.close
    calls = []
    error = OSError("close fault")
    def fail_once(fd):
        calls.append(fd)
        if len(calls) == 1:
            raise error
        original_close(fd)
    monkeypatch.setattr(os, "close", fail_once)
    with pytest.raises(OSError) as caught:
        copier(files[0], files[1])
    assert caught.value is error and len(calls) == 2 and calls[0] == calls[1]
    assert_preserved(files)


@pytest.mark.skipif(os.name != "nt", reason="Native Windows sharing denial")
def test_sharing_denial_retains_readonly_target(copier, files):
    src, dst, _ = files
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    create.restype = ctypes.c_void_p
    close = kernel.CloseHandle
    close.argtypes = [ctypes.c_void_p]
    close.restype = ctypes.c_int
    dst.chmod(stat.S_IREAD)
    mode = dst.stat().st_mode
    handle = create(str(dst), 0x80000000, 3, None, 3, 0x80, None)
    assert handle not in (None, ctypes.c_void_p(-1).value)
    try:
        with pytest.raises(OSError) as caught:
            copier(src, dst)
        assert caught.value.winerror in (5, 32)
        assert_preserved(files)
        assert dst.stat().st_mode == mode
    finally:
        assert close(handle)
