"""Warm-open session flow.

At the start of a session, MethodMarker greets the learner by name,
using a time-of-day greeting (Good morning / afternoon / evening),
summarises where they are, and asks if they have school homework.

The tutor does NOT solve the homework. It works from a variant.
That variant flow is on the backlog (see docs/backlog.md, section H)
and will be built during the OpenAI phase.

Timezone:
    Default is South African Standard Time (SAST, UTC+2, no DST).
    If the learner row has a `timezone` column (IANA name, e.g.
    "Europe/London"), that is used. An explicit tz_name argument
    to greet()/warm_open() overrides both.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

_SAST_OFFSET = timedelta(hours=2)  # South Africa: UTC+2, no DST

# The tutor persona's first name. Change here to rename the tutor.
TUTOR_NAME = "Tanaka"


def _first_name(learner_id: str) -> str:
    s = (learner_id or "learner").strip()
    return s.split()[0].split("_")[0].capitalize()


def _now_local(tz_name: Optional[str]) -> datetime:
    """Current time in the learner's tz, falling back to SAST."""
    if tz_name and ZoneInfo is not None:
        try:
            return datetime.now(ZoneInfo(tz_name))
        except Exception:
            pass
    try:
        if ZoneInfo is not None:
            return datetime.now(ZoneInfo("Africa/Johannesburg"))
    except Exception:
        pass
    return datetime.now(timezone.utc) + _SAST_OFFSET


def _time_of_day(now: datetime) -> str:
    """Time-of-day band. Late night is 'Hello', not 'Good morning'."""
    h = now.hour
    if 5 <= h < 12:
        return "Good morning"
    if 12 <= h < 17:
        return "Good afternoon"
    if 17 <= h < 22:
        return "Good evening"
    return "Hello"  # 22:00 - 04:59


def _last_seen(store, learner_id: str) -> Optional[str]:
    try:
        row = store.conn.execute(
            "SELECT last_seen FROM learner WHERE learner_id = ?",
            (learner_id,),
        ).fetchone()
        return row["last_seen"] if row else None
    except Exception:
        return None


def _learner_tz(store, learner_id: str) -> Optional[str]:
    """Read the learner's tz from the learner row, if the column exists."""
    try:
        row = store.conn.execute(
            "SELECT timezone FROM learner WHERE learner_id = ?",
            (learner_id,),
        ).fetchone()
        if row and row["timezone"]:
            return row["timezone"]
    except Exception:
        pass
    return None


def _days_since(iso: Optional[str]) -> Optional[int]:
    if not iso:
        return None
    try:
        then = datetime.fromisoformat(iso)
        if then.tzinfo is None:
            then = then.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return max(0, (now - then).days)
    except Exception:
        return None


def _is_new_learner(store, learner_id: str) -> bool:
    """Brand new = no last_seen AND no session rows."""
    if _last_seen(store, learner_id):
        return False
    try:
        row = store.conn.execute(
            "SELECT COUNT(*) FROM session WHERE learner_id = ?",
            (learner_id,),
        ).fetchone()
        if row and row[0] > 0:
            return False
    except Exception:
        pass
    return True


def _mastery_summary(store, learner_id: str) -> dict:
    out = {"mastered": [], "near_mastery": [], "practising": [], "not_started": []}
    try:
        rows = store.conn.execute(
            "SELECT skill_id, mastery_state FROM mastery WHERE learner_id = ?",
            (learner_id,),
        ).fetchall()
    except Exception:
        return out
    for r in rows:
        state = (r["mastery_state"] or "not_started").lower()
        out.setdefault(state, []).append(r["skill_id"])
    return out


def _friendly_skill(skill_id: str) -> str:
    parts = skill_id.split(".")
    if len(parts) >= 2:
        return " ".join(parts[1:]).replace(".", " ")
    return skill_id


def _tutor_intro(learner_name: str) -> str:
    """Self-introduction clause for a first meeting.

    Returns "" when the learner shares the tutor's first name, so we
    don't say "I'm Tanaka" to a learner also called Tanaka.
    """
    if (TUTOR_NAME or "").strip().lower() == (learner_name or "").strip().lower():
        return ""
    return f" I'm {TUTOR_NAME}."


def greet(
    learner_id: str,
    store,
    tz_name: Optional[str] = None,
    now: Optional[datetime] = None,
    _is_new: Optional[bool] = None,
) -> str:
    """Warm greeting. Time-of-day aware. No 'again' for a first meeting.

    Priority for timezone:
        1. tz_name argument
        2. learner.timezone column (if present)
        3. SAST (Africa/Johannesburg, UTC+2)

    `now` is for testing only; leave it None in production.
    """
    name = _first_name(learner_id)
    tz = tz_name or _learner_tz(store, learner_id)
    moment = now if now is not None else _now_local(tz)
    tod = _time_of_day(moment)

    if _is_new is None:
        _is_new = _is_new_learner(store, learner_id)
    if _is_new:
        return f"{tod}, {name}.{_tutor_intro(name)} Welcome — it's great to meet you."

    days = _days_since(_last_seen(store, learner_id))
    if days is None:
        return f"{tod}, {name}. Welcome back."
    if days == 0:
        return f"{tod}, {name}. Good to see you again."
    if days == 1:
        return f"{tod}, {name}. Welcome back."
    if days <= 7:
        return f"{tod}, {name}. Good to see you again."
    return f"{tod}, {name}. Good to see you again — it's been a little while."


def progress_preview(
    learner_id: str,
    store,
    is_new: Optional[bool] = None,
) -> str:
    """Summary of where the learner is.

    `is_new` lets the caller pass in the pre-session new-ness decision
    so we don't have to re-derive it. If None, we derive it here.
    """
    m = _mastery_summary(store, learner_id)
    if not any(m.values()):
        if is_new is None:
            is_new = _is_new_learner(store, learner_id)
        if is_new:
            return "This is our first session together. Let's see where you are."
        return "No mastery data yet. Let's see where you are."
    lines = []
    if m.get("mastered"):
        topics = ", ".join(_friendly_skill(s) for s in m["mastered"][:2])
        lines.append(f"You have mastered: {topics}.")
    if m.get("near_mastery"):
        topics = ", ".join(_friendly_skill(s) for s in m["near_mastery"][:2])
        lines.append(f"You are close on: {topics}.")
    if m.get("practising"):
        topics = ", ".join(_friendly_skill(s) for s in m["practising"][:2])
        lines.append(f"Still working on: {topics}.")
    return " ".join(lines)


def ask_homework() -> str:
    return ("Do you have homework or an assignment from school you would like to "
            "work through? (yes / no)")


def warm_open(
    learner_id: str,
    store,
    tz_name: Optional[str] = None,
) -> dict:
    g = greet(learner_id, store, tz_name=tz_name)
    p = progress_preview(learner_id, store)
    h = ask_homework()
    print()
    print("=" * 60)
    print(f"  {g}")
    print()
    if p:
        print(f"  {p}")
        print()
    print(f"  {h}")
    print("=" * 60)
    return {"greeting": g, "preview": p, "homework_prompt": h}
