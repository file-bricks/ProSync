"""Regression tests for the daily local-time scheduling contract."""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from schedule_time import next_daily_run, parse_daily_time, resolve_iana_timezone


BERLIN = ZoneInfo("Europe/Berlin")


def test_next_daily_run_uses_tomorrow_when_today_has_passed():
    now = datetime(2026, 1, 15, 19, 0, tzinfo=BERLIN)

    result = next_daily_run(now, time(18, 0), BERLIN)

    assert result == datetime(2026, 1, 16, 18, 0, tzinfo=BERLIN)


def test_next_daily_run_handles_midnight():
    now = datetime(2026, 1, 15, 23, 59, 59, tzinfo=BERLIN)

    result = next_daily_run(now, time(0, 0), BERLIN)

    assert result == datetime(2026, 1, 16, 0, 0, tzinfo=BERLIN)


def test_next_daily_run_is_strictly_later_when_wall_time_is_equal():
    now = datetime(2026, 1, 15, 18, 0, tzinfo=BERLIN)

    result = next_daily_run(now, time(18, 0), BERLIN)

    assert result == datetime(2026, 1, 16, 18, 0, tzinfo=BERLIN)


def test_next_daily_run_shifts_nonexistent_wall_time_by_dst_gap():
    now = datetime(2026, 3, 29, 0, 30, tzinfo=BERLIN)

    result = next_daily_run(now, time(2, 30), BERLIN)

    assert result == datetime(2026, 3, 29, 3, 30, tzinfo=BERLIN)
    assert result.utcoffset() == timedelta(hours=2)


def test_next_daily_run_uses_first_occurrence_in_repeated_hour():
    now = datetime(2026, 10, 25, 1, 30, tzinfo=BERLIN)

    result = next_daily_run(now, time(2, 30), BERLIN)

    assert result == datetime(2026, 10, 25, 2, 30, tzinfo=BERLIN, fold=0)
    assert result.fold == 0
    assert result.utcoffset() == timedelta(hours=2)


def test_next_daily_run_does_not_run_twice_in_repeated_hour():
    now = datetime(2026, 10, 25, 2, 15, tzinfo=BERLIN, fold=1)

    result = next_daily_run(now, time(2, 30), BERLIN)

    assert result == datetime(2026, 10, 26, 2, 30, tzinfo=BERLIN)
    assert result.utcoffset() == timedelta(hours=1)


def test_next_daily_run_requires_aware_now():
    with pytest.raises(ValueError, match="timezone-aware"):
        next_daily_run(datetime(2026, 1, 15, 12, 0), time(18, 0), BERLIN)


def test_next_daily_run_requires_naive_wall_time():
    with pytest.raises(ValueError, match="without tzinfo"):
        next_daily_run(
            datetime(2026, 1, 15, 12, 0, tzinfo=BERLIN),
            time(18, 0, tzinfo=BERLIN),
            BERLIN,
        )


def test_next_daily_run_rejects_fixed_offset_timezone():
    with pytest.raises(TypeError, match="IANA ZoneInfo"):
        next_daily_run(
            datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc),
            time(18, 0),
            timezone.utc,
        )


def test_parse_daily_time_requires_canonical_24_hour_format():
    assert parse_daily_time("06:05") == time(6, 5)

    with pytest.raises(ValueError, match="HH:MM"):
        parse_daily_time("6:05")


def test_resolve_iana_timezone_rejects_unknown_values():
    assert resolve_iana_timezone("Europe/Berlin").key == "Europe/Berlin"

    with pytest.raises(ValueError, match="unknown IANA timezone"):
        resolve_iana_timezone("Mars/Olympus")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
