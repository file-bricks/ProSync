"""Regression tests for the persisted daily scheduler mode."""

from __future__ import annotations

import importlib.util
import os
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PySide6.QtCore import QCoreApplication


BERLIN = ZoneInfo("Europe/Berlin")


def _load_prosync_module():
    module_path = Path(__file__).with_name("ProSyncStart_V3.1.py")
    spec = importlib.util.spec_from_file_location("prosync_daily", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Config:
    def __init__(self, connections):
        self.connections = connections

    def list_connections(self):
        return self.connections


def test_daily_scheduler_arms_one_shot_timer_and_rearms_after_trigger():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    QCoreApplication.instance() or QCoreApplication([])
    prosync = _load_prosync_module()
    conn = {
        "id": "daily-1",
        "name": "Täglicher Test",
        "autosync": {
            "enabled": True,
            "mode": "daily",
            "daily_time": "13:00",
            "timezone": "Europe/Berlin",
        },
    }
    moments = iter(
        [
            datetime(2026, 1, 15, 12, 0, tzinfo=BERLIN),
            datetime(2026, 1, 15, 13, 1, tzinfo=BERLIN),
        ]
    )
    scheduler = prosync.ConnectionScheduler(_Config([conn]), now_provider=lambda _tz: next(moments))
    triggered = []
    scheduler.trigger_sync.connect(lambda value: triggered.append(value["id"]))

    scheduler.update_all()
    timer = scheduler.timers["daily-1"]
    assert timer.isSingleShot()
    assert timer.interval() == 60 * 60 * 1000

    scheduler._on_daily_timer("daily-1")

    assert triggered == ["daily-1"]
    assert scheduler.timers["daily-1"].isSingleShot()
    assert scheduler.timers["daily-1"].interval() == (23 * 60 + 59) * 60 * 1000


def test_daily_schedule_schema_persists_in_local_configuration():
    prosync = _load_prosync_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "ProSync_config.json"
        config = prosync.ConfigManager(str(config_path))
        config.add_or_update_connection(
            {
                "id": "daily-persisted",
                "name": "Tägliche Sicherung",
                "autosync": {
                    "enabled": True,
                    "mode": "daily",
                    "daily_time": "06:05",
                    "timezone": "Europe/Berlin",
                },
            }
        )

        reloaded = prosync.ConfigManager(str(config_path))

    assert reloaded.list_connections()[0]["autosync"] == {
        "enabled": True,
        "mode": "daily",
        "daily_time": "06:05",
        "timezone": "Europe/Berlin",
    }
