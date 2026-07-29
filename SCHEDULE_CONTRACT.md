# ProSync schedule contract

Status: Phase 2 for TW-PS-09

## Scope

ProSync supports interval schedules and an optional daily local-time schedule.
Phase 1 defines the daylight-saving-safe calculation; Phase 2 persists the
daily schema, exposes it from the connection context menu, and arms a one-shot
`QTimer` for the next valid occurrence.

## Daily local-time rules

- A schedule is a wall-clock time plus an explicit IANA timezone, such as
  `Europe/Berlin`.
- The calculated instant is always strictly later than the supplied current
  instant.
- If today's wall-clock time has passed, the next run is on the following
  local calendar date.
- During the spring daylight-saving jump, a nonexistent time is shifted
  forward by the transition gap. In Berlin, `02:30` therefore becomes `03:30`.
- During the repeated autumn hour, the first occurrence (`fold=0`) is used.
  The second occurrence is skipped so that a daily job runs at most once per
  local calendar date.
- Inputs without timezone information are rejected. Fixed-offset timezone
  objects are also rejected because they do not carry daylight-saving rules.
- The runtime dependency `tzdata` supplies the IANA database on Windows when
  the operating system does not expose it to Python.

## Daily schedule schema and runtime

- A daily connection stores `autosync.mode = "daily"`, `daily_time` in
  canonical `HH:MM` form, and an explicit IANA `timezone`.
- The context-menu action **Tägliche Uhrzeit festlegen…** validates both values
  before saving them to the local configuration. Existing interval schedules
  remain unchanged until a user selects this mode.
- The scheduler uses a single-shot timer. After a trigger it calculates and
  arms the next occurrence; when the application becomes active again after a
  resume, it recalculates all enabled daily schedules from the current time.
- Resume does not invent a missed synchronization. It only schedules the next
  valid local occurrence, so a suspended device cannot silently run multiple
  catch-up copies.

The implementation lives in `schedule_time.py` and `ProSyncStart_V3.1.py`.
Weekday schedules, migration of existing interval profiles, and an end-to-end
smoke against a controlled sync target remain Phase 3.
