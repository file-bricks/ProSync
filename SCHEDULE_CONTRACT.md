# ProSync schedule contract

Status: Phase 1 for TW-PS-09

## Scope

ProSync currently executes automatic synchronization at fixed minute
intervals. Phase 1 adds only a pure calculation for the next daily local-time
run. It does not yet change configuration, the GUI, or `QTimer`.

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

The implementation lives in `schedule_time.py`. Configuration persistence,
user controls, timer re-arming after resume, weekday schedules, and migration
from interval schedules remain later phases.
