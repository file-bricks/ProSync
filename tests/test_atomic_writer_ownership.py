"""Tests for atomic and collision-resistant configuration and profile writers."""
from __future__ import annotations

import json
import os
import stat
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from prosync_utils import atomic_write_json, atomic_write_text


def test_atomic_write_text_success(tmp_path: Path) -> None:
    target = tmp_path / "test_file.txt"
    content = "Grüße aus Köln: Äpfel, Öle, Übermut & Spaß!"
    atomic_write_text(str(target), content, encoding="utf-8")

    assert target.is_file()
    assert target.read_text(encoding="utf-8") == content


def test_atomic_write_text_creates_parent_directories(tmp_path: Path) -> None:
    nested_target = tmp_path / "deep" / "nested" / "dir" / "out.txt"
    content = "Autonome Ordnererstellung funktioniert."
    atomic_write_text(str(nested_target), content, encoding="utf-8")

    assert nested_target.is_file()
    assert nested_target.read_text(encoding="utf-8") == content


def test_atomic_write_text_cleans_up_on_failure(tmp_path: Path) -> None:
    target = tmp_path / "fail_clean.txt"

    with mock.patch("os.fsync", side_effect=OSError("Disk sync error")):
        with pytest.raises(OSError, match="Disk sync error"):
            atomic_write_text(str(target), "data")

    assert not target.exists()
    # Ensure no leftover temp files exist in directory
    assert list(tmp_path.iterdir()) == []


def test_atomic_write_text_preserves_target_on_failure(tmp_path: Path) -> None:
    target = tmp_path / "existing.txt"
    target.write_text("original content", encoding="utf-8")

    with mock.patch("os.fsync", side_effect=OSError("Disk sync error")):
        with pytest.raises(OSError, match="Disk sync error"):
            atomic_write_text(str(target), "corrupted replacement")

    assert target.read_text(encoding="utf-8") == "original content"
    assert list(tmp_path.iterdir()) == [target]


def test_atomic_write_json_success(tmp_path: Path) -> None:
    target = tmp_path / "config.json"
    data = {
        "connections": [{"name": "Übertrag_Backup", "active": True, "count": 42}],
        "settings": {"language": "de", "autosync": False},
    }
    atomic_write_json(str(target), data, indent=2, ensure_ascii=False)

    assert target.is_file()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded == data


def test_atomic_write_json_exclusive_stage_preserves_foreign_tmp(tmp_path: Path) -> None:
    target = tmp_path / "config.json"
    foreign_tmp = tmp_path / "config.json.tmp"
    foreign_tmp.write_text("fremde tempdaten eines anderen prozesses", encoding="utf-8")

    data = {"key": "sicherer_eintrag"}
    atomic_write_json(str(target), data)

    assert target.is_file()
    assert json.loads(target.read_text(encoding="utf-8")) == data
    # The foreign .tmp file must not have been touched, overwritten or removed!
    assert foreign_tmp.exists()
    assert foreign_tmp.read_text(encoding="utf-8") == "fremde tempdaten eines anderen prozesses"


def test_atomic_write_json_unserializable_cleans_up_and_leaves_target(tmp_path: Path) -> None:
    target = tmp_path / "valid.json"
    target.write_text('{"original": true}', encoding="utf-8")

    with pytest.raises(TypeError):
        atomic_write_json(str(target), {"unserializable": object()})

    assert target.read_text(encoding="utf-8") == '{"original": true}'
    assert list(tmp_path.iterdir()) == [target]


def test_config_manager_save_and_export_portable_profile_preserves_foreign_tmp(tmp_path: Path) -> None:
    import importlib.util

    root = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location("prosync_main", root / "ProSyncStart_V3.1.py")
    prosync = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prosync)

    cfg_file = tmp_path / "ProSync_config.json"
    foreign_cfg_tmp = tmp_path / "ProSync_config.json.tmp"
    foreign_cfg_tmp.write_text("fremdes config tmp", encoding="utf-8")

    cfg = prosync.ConfigManager(str(cfg_file))
    cfg.add_or_update_connection({"id": "conn-1", "name": "Ordner-Spiegelung"})
    cfg.save()

    assert cfg_file.is_file()
    assert foreign_cfg_tmp.read_text(encoding="utf-8") == "fremdes config tmp"

    # Test portable export
    export_file = tmp_path / "portable_profile.json"
    foreign_export_tmp = tmp_path / "portable_profile.json.tmp"
    foreign_export_tmp.write_text("fremdes export tmp", encoding="utf-8")

    cfg.export_portable_profile(str(export_file))
    assert export_file.is_file()
    assert foreign_export_tmp.read_text(encoding="utf-8") == "fremdes export tmp"


def test_prosync_reader_db_manager_save_preserves_foreign_tmp(tmp_path: Path) -> None:
    import importlib.util

    root = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location("prosync_reader", root / "ProSyncReader.py")
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)

    cfg_path = tmp_path / "search_config.json"
    foreign_tmp = tmp_path / "search_config.json.tmp"
    foreign_tmp.write_text("fremdes reader tmp", encoding="utf-8")

    with mock.patch.object(reader, "CONFIG_PATH", str(cfg_path)):
        db_mgr = reader.DBManager()
        db_mgr.add_db(str(tmp_path / "test.db"))

    assert cfg_path.is_file()
    assert foreign_tmp.read_text(encoding="utf-8") == "fremdes reader tmp"


def test_translation_system_save_preserves_foreign_tmp(tmp_path: Path) -> None:
    from translator import TranslationSystem

    trans_file = tmp_path / "locales" / "translations.json"
    foreign_tmp = tmp_path / "locales" / "translations.json.tmp"
    trans_file.parent.mkdir(parents=True, exist_ok=True)
    foreign_tmp.write_text("fremdes translation tmp", encoding="utf-8")

    ts = TranslationSystem(default_lang="de", app_dir=tmp_path)
    ts.translations["neuer_key"] = {"de": "Wert", "en": "Value"}
    ts._save_translations()

    assert trans_file.is_file()
    assert foreign_tmp.read_text(encoding="utf-8") == "fremdes translation tmp"
