"""Pure time calculations for future ProSync calendar schedules.

The current application scheduler remains interval based. This module defines
the local-time and daylight-saving contract before calendar schedules are
wired into configuration, GUI, or ``QTimer`` instances.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def parse_daily_time(value: str) -> time:
    """Parse a user-facing daily wall-clock value in ``HH:MM`` format."""

    if not isinstance(value, str):
        raise ValueError("daily time must use the HH:MM format")
    try:
        parsed = datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        raise ValueError("daily time must use the HH:MM format") from exc
    if value != parsed.strftime("%H:%M"):
        raise ValueError("daily time must use the HH:MM format")
    return parsed


def resolve_iana_timezone(value: str) -> ZoneInfo:
    """Return an IANA timezone or raise a clear configuration error."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError("timezone must be a non-empty IANA timezone name")
    try:
        return ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"unknown IANA timezone: {value}") from exc


def next_daily_run(now: datetime, run_at: time, tz: ZoneInfo) -> datetime:
    """Return the next daily occurrence of ``run_at`` in ``tz``.

    The returned instant is strictly later than ``now``. Ambiguous wall times
    use their first occurrence (``fold=0``), so a daily job cannot run twice on
    the same local calendar date. Nonexistent wall times are shifted forward by
    the daylight-saving gap while preserving minutes and seconds.

    Args:
        now: Current timezone-aware instant.
        run_at: Local wall-clock time without timezone information.
        tz: IANA timezone carrying the daylight-saving transition rules.

    Raises:
        TypeError: If ``tz`` is not a :class:`zoneinfo.ZoneInfo`.
        ValueError: If ``now`` is naive or ``run_at`` has timezone information.
    """

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    if run_at.tzinfo is not None:
        raise ValueError("run_at must be a local wall time without tzinfo")
    if not isinstance(tz, ZoneInfo):
        raise TypeError("tz must be an IANA ZoneInfo timezone")

    now_utc = now.astimezone(timezone.utc)
    local_date = now.astimezone(tz).date()

    for days_ahead in range(3):
        wall_time = datetime.combine(local_date + timedelta(days=days_ahead), run_at)
        candidate = wall_time.replace(tzinfo=tz, fold=0)

        # A UTC roundtrip normalizes imaginary local times. For example,
        # Europe/Berlin 02:30 becomes 03:30 on the spring-forward date.
        normalized = candidate.astimezone(timezone.utc).astimezone(tz)
        if normalized.replace(tzinfo=None) != wall_time:
            candidate = normalized

        if candidate.astimezone(timezone.utc) > now_utc:
            return candidate

    raise RuntimeError("could not determine the next daily run")


__all__ = ["next_daily_run", "parse_daily_time", "resolve_iana_timezone"]
