"""Pure time calculations for ProSync calendar schedules.

This module defines the local-time, weekday-filtered, and daylight-saving contract
for calendar schedules wired into configuration, GUI, or ``QTimer`` instances.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

WEEKDAY_ALIASES: dict[str, int] = {
    # German & English full/common
    "mo": 0,
    "mon": 0,
    "monday": 0,
    "montag": 0,
    "di": 1,
    "tue": 1,
    "tuesday": 1,
    "dienstag": 1,
    "mi": 2,
    "wed": 2,
    "wednesday": 2,
    "mittwoch": 2,
    "do": 3,
    "thu": 3,
    "thursday": 3,
    "donnerstag": 3,
    "fr": 4,
    "fri": 4,
    "friday": 4,
    "freitag": 4,
    "sa": 5,
    "sat": 5,
    "saturday": 5,
    "samstag": 5,
    "so": 6,
    "sun": 6,
    "sunday": 6,
    "sonntag": 6,
    # English short 2-letter codes
    "tu": 1,
    "we": 2,
    "th": 3,
    "su": 6,
    # Spanish (Tier-2 supported locale)
    "lu": 0,
    "lunes": 0,
    "ma": 1,
    "martes": 1,
    "miercoles": 2,
    "miércoles": 2,
    "ju": 3,
    "jueves": 3,
    "vi": 4,
    "viernes": 4,
    "sabado": 5,
    "sábado": 5,
    "domingo": 6,
}

WEEKDAY_GROUPS: dict[str, set[int]] = {
    "all": {0, 1, 2, 3, 4, 5, 6},
    "daily": {0, 1, 2, 3, 4, 5, 6},
    "taeglich": {0, 1, 2, 3, 4, 5, 6},
    "täglich": {0, 1, 2, 3, 4, 5, 6},
    "todos": {0, 1, 2, 3, 4, 5, 6},
    "diario": {0, 1, 2, 3, 4, 5, 6},
    "*": {0, 1, 2, 3, 4, 5, 6},
    "workdays": {0, 1, 2, 3, 4},
    "werktage": {0, 1, 2, 3, 4},
    "laborables": {0, 1, 2, 3, 4},
    "dias laborables": {0, 1, 2, 3, 4},
    "días laborables": {0, 1, 2, 3, 4},
    "mon-fri": {0, 1, 2, 3, 4},
    "mo-fr": {0, 1, 2, 3, 4},
    "lu-vi": {0, 1, 2, 3, 4},
    "weekend": {5, 6},
    "wochenende": {5, 6},
    "fin de semana": {5, 6},
    "sat-sun": {5, 6},
    "sa-so": {5, 6},
    "sa-do": {5, 6},
}


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


def parse_weekdays(
    value: str | list[int | str] | set[int | str] | tuple[int | str, ...] | None,
) -> set[int] | None:
    """Parse and validate weekday filters for ProSync schedules.

    Weekdays follow Python's datetime convention (0=Monday, 6=Sunday).

    Args:
        value: None (daily), alias string ("workdays", "mon-fri", "weekend"),
            comma-separated string ("mon,wed,fri"), or iterable of weekday ints/names.

    Returns:
        A set of integers in range 0..6, or None if no weekday restriction is configured.

    Raises:
        ValueError: If weekdays cannot be parsed, contains invalid numbers/tokens,
            or resolves to an empty set.
        TypeError: If value is of unsupported type or contains booleans.
    """
    if value is None:
        return None

    if isinstance(value, bool):
        raise TypeError("weekdays cannot be a boolean")

    if isinstance(value, str):
        cleaned = value.strip().lower()
        if not cleaned:
            return None
        if cleaned in WEEKDAY_GROUPS:
            return set(WEEKDAY_GROUPS[cleaned])
        parts = [p.strip() for p in cleaned.replace(";", ",").split(",") if p.strip()]
        if not parts:
            raise ValueError("weekdays string cannot be empty")
        raw_items: list[int | str] = list(parts)
    elif isinstance(value, (list, set, tuple)):
        if not value:
            raise ValueError("weekdays iterable cannot be empty")
        raw_items = list(value)
    else:
        raise TypeError("weekdays must be a string, list, set, tuple, or None")

    parsed: set[int] = set()
    for item in raw_items:
        if isinstance(item, bool):
            raise TypeError("weekday item cannot be a boolean")
        if isinstance(item, int):
            if 0 <= item <= 6:
                parsed.add(item)
            else:
                raise ValueError(
                    f"invalid weekday index {item}: must be between 0 (Monday) and 6 (Sunday)"
                )
        elif isinstance(item, str):
            token = item.strip().lower()
            if not token:
                continue
            if token in WEEKDAY_GROUPS:
                parsed.update(WEEKDAY_GROUPS[token])
            elif token.isdigit():
                num = int(token)
                if 0 <= num <= 6:
                    parsed.add(num)
                else:
                    raise ValueError(f"invalid weekday number {num}: must be between 0 and 6")
            elif token in WEEKDAY_ALIASES:
                parsed.add(WEEKDAY_ALIASES[token])
            elif "-" in token or ".." in token:
                sep = "-" if "-" in token else ".."
                subparts = [sp.strip() for sp in token.split(sep, 1)]
                if len(subparts) == 2 and subparts[0] and subparts[1]:
                    start_str, end_str = subparts
                    start_day = (
                        int(start_str)
                        if start_str.isdigit()
                        else WEEKDAY_ALIASES.get(start_str)
                    )
                    end_day = (
                        int(end_str)
                        if end_str.isdigit()
                        else WEEKDAY_ALIASES.get(end_str)
                    )
                    if (
                        start_day is not None
                        and end_day is not None
                        and 0 <= start_day <= 6
                        and 0 <= end_day <= 6
                    ):
                        if start_day <= end_day:
                            parsed.update(range(start_day, end_day + 1))
                        else:
                            parsed.update(range(start_day, 7))
                            parsed.update(range(0, end_day + 1))
                    else:
                        raise ValueError(f"unknown weekday range: {item!r}")
                else:
                    raise ValueError(f"unknown weekday name or token: {item!r}")
            else:
                raise ValueError(f"unknown weekday name or token: {item!r}")
        else:
            raise TypeError(f"weekday item must be int or str, got {type(item).__name__}")

    if not parsed:
        raise ValueError("weekdays must resolve to at least one valid day (0-6)")
    return parsed


def next_daily_run(
    now: datetime,
    run_at: time,
    tz: ZoneInfo,
    weekdays: set[int] | list[int | str] | tuple[int | str, ...] | str | None = None,
) -> datetime:
    """Return the next daily occurrence of ``run_at`` in ``tz``, optionally restricted to ``weekdays``.

    The returned instant is strictly later than ``now``. Ambiguous wall times
    use their first occurrence (``fold=0``), so a daily job cannot run twice on
    the same local calendar date. Nonexistent wall times are shifted forward by
    the daylight-saving gap while preserving minutes and seconds.

    Args:
        now: Current timezone-aware instant.
        run_at: Local wall-clock time without timezone information.
        tz: IANA timezone carrying the daylight-saving transition rules.
        weekdays: Optional weekday filter (set/list of 0..6, alias string, or None).

    Raises:
        TypeError: If ``tz`` is not a :class:`zoneinfo.ZoneInfo`.
        ValueError: If ``now`` is naive, ``run_at`` has timezone information, or weekdays are invalid.
    """

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    if run_at.tzinfo is not None:
        raise ValueError("run_at must be a local wall time without tzinfo")
    if not isinstance(tz, ZoneInfo):
        raise TypeError("tz must be an IANA ZoneInfo timezone")

    valid_weekdays = parse_weekdays(weekdays)

    now_utc = now.astimezone(timezone.utc)
    local_date = now.astimezone(tz).date()

    max_days = 14 if valid_weekdays is not None else 3
    for days_ahead in range(max_days):
        candidate_date = local_date + timedelta(days=days_ahead)
        if valid_weekdays is not None and candidate_date.weekday() not in valid_weekdays:
            continue

        wall_time = datetime.combine(candidate_date, run_at)
        candidate = wall_time.replace(tzinfo=tz, fold=0)

        # A UTC roundtrip normalizes imaginary local times. For example,
        # Europe/Berlin 02:30 becomes 03:30 on the spring-forward date.
        normalized = candidate.astimezone(timezone.utc).astimezone(tz)
        if normalized.replace(tzinfo=None) != wall_time:
            candidate = normalized

        if candidate.astimezone(timezone.utc) > now_utc:
            return candidate

    raise RuntimeError("could not determine the next scheduled run")


__all__ = [
    "WEEKDAY_ALIASES",
    "WEEKDAY_GROUPS",
    "next_daily_run",
    "parse_daily_time",
    "parse_weekdays",
    "resolve_iana_timezone",
]
