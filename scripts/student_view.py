"""Tanaka's letter to the student.

150 words. Warm. Specific. Honest. Same data, human language.

Reads from the same DB. Produces a markdown "letter" that:
- Leads with a win
- Names one specific struggle in plain English
- Gives one action
- Ends with a hook back into a session
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict


def _find_root():
    r = Path(".").resolve()
    for c in [r, *r.parents]:
        if (c / "src" / "tutor").is_dir():
            return c
    return r


ROOT = _find_root()
DB = ROOT / "data" / "learner_store" / "learners.db"


def _parse(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _is_pass(error_type):
    return str(error_type or "").lower() in ("none", "match")


def _natural_misconception(mid):
    """Map misconception id → plain-English phrase."""
    if not mid:
        return None
    mapping = {
        "M_SIGN_ERROR_READING_ROOT": "flipped signs when reading roots from brackets",
        "M_ALG_SIGN_FLIP_FACTOR": "flipped signs when factorising",
        "M_SIGN_ERROR_FACTORISATION": "flipped signs when factorising",
        "M_INCOMPLETE_ROOTS": "stopped after finding one root",
        "M_CALCULATION_ERROR": "rushed the final calculation",
        "M_AND_OR_CONFUSION": "used 'and' where the memo wants 'or'",
        "M_COORDINATE_SWAP": "swapped x and y",
        "M_COORDINATE_SIGN_FLIP": "flipped a sign on one coordinate",
        "M_INCOMPLETE_PAIR": "stopped after finding only one of x or y",
        "M_SURD_CALCULATION_ERROR": "squared both sides but slipped on the arithmetic",
        "M_INEQ_MISSING_INTERVAL": "found one interval but missed the second",
        "M_INEQ_SIGN_FLIP": "flipped a sign in the interval",
        "M_UNITS_IN_ANSWER": "added units where the memo wants just a number",
    }
    return mapping.get(mid, mid.replace("M_", "").replace("_", " ").lower())


def build_letter(learner_id, days=7):
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    try:
        attempts = [dict(r) for r in conn.execute(
            "SELECT * FROM attempt WHERE learner_id = ? AND timestamp >= ? "
            "ORDER BY timestamp ASC",
            (learner_id, since),
        ).fetchall()]

        events = [dict(r) for r in conn.execute(
            "SELECT * FROM learner_events WHERE learner_id = ? AND timestamp >= ? "
            "ORDER BY timestamp ASC",
            (learner_id, since),
        ).fetchall()]
    finally:
        conn.close()

    if not attempts:
        return f"""# A note from Tanaka

Hi {learner_id},

I haven't seen you in a few days. When you're ready to pick things back up, just open the tutor and pick a question — I'll be here.

There's no rush. Learning Maths is a marathon, not a sprint.

— Tanaka
"""

    # ─── Compute narrative elements ─────────────────────────────────────────
    attempts_parsed = []
    for a in attempts:
        a2 = dict(a)
        a2["ts"] = _parse(a["timestamp"])
        a2["is_pass"] = _is_pass(a["error_type"])
        a2["is_variant"] = str(a.get("question_id") or "").startswith("VAR_")
        if a2["ts"]:
            attempts_parsed.append(a2)

    # Streak: consecutive days with attempts (ending today)
    days_with_attempts = set(a["ts"].date() for a in attempts_parsed)
    today = datetime.now(timezone.utc).date()
    streak = 0
    d = today
    while d in days_with_attempts:
        streak += 1
        d -= timedelta(days=1)

    # Total questions answered this window
    total = len(attempts_parsed)
    passes = sum(1 for a in attempts_parsed if a["is_pass"])
    pass_rate = passes / total if total else 0

    # Misconception frequencies
    miscon = Counter(a["misconception_id"] for a in attempts_parsed if a["misconception_id"])

    # Best streak within sessions — longest run of passes
    longest_run = 0
    current_run = 0
    for a in attempts_parsed:
        if a["is_pass"]:
            current_run += 1
            longest_run = max(longest_run, current_run)
        else:
            current_run = 0

    # Skills practiced — but pick the one with the most struggles
    # (where the misconception is densest, not alphabetically first)
    miscon_skill = Counter()
    for a in attempts_parsed:
        if a["misconception_id"]:
            miscon_skill[a["skill_id"]] += 1
    if miscon_skill:
        # Skill where most misconceptions live
        skill_label = _friendly_skill_name(miscon_skill.most_common(1)[0][0])
    else:
        # Fallback to most-practiced skill
        skills_count = Counter(a["skill_id"] for a in attempts_parsed)
        if skills_count:
            skill_label = _friendly_skill_name(skills_count.most_common(1)[0][0])
        else:
            skill_label = "Maths"

    # Engagement signals
    manual_variants = sum(1 for e in events if e["event_type"] == "MANUAL_VARIANT_REQUEST")
    homework_downloads = sum(1 for e in events if e["event_type"] == "HOMEWORK_DOWNLOAD")

    # ─── Build the narrative ────────────────────────────────────────────────
    L = []
    A = L.append

    A(f"# A note from Tanaka")
    A("")
    A(f"Hi {learner_id.replace('_', ' ').title()},")
    A("")

    # Opening — acknowledge effort AND honesty about where they are
    if pass_rate < 0.4 and total >= 20:
        # Struggling learner with real volume
        if streak >= 3:
            A(f"**{streak} days in a row.** That's real commitment. "
              f"You put in {total} questions this week — and {passes} of them landed.")
        else:
            A(f"You worked through **{total} questions** this week. "
              f"{passes} of them landed, {total - passes} didn't. That's what "
              f"pushing at the edge of what you know looks like.")
    elif streak >= 3:
        A(f"**{streak} days in a row.** That's not luck — that's you building a habit. "
          f"I notice things like that.")
    elif total >= 20:
        A(f"You've worked through **{total} questions** in the last {days} days. "
          f"That's real effort.")
    elif total >= 5:
        A(f"You've been showing up. **{total} questions** in the last {days} days — "
          f"every one of them counts.")
    else:
        A(f"Every question is a step. **{total} of them** this week — "
          f"that's how learning happens.")

    A("")

    # A specific recent win — framed honestly
    if longest_run >= 3 and pass_rate < 0.5:
        # Struggling learner — don't pretend the win overrides the struggle
        A(f"You showed me something on your best run. **{longest_run} in a row.** "
          f"Same brain, same student. That's the version of you we're building toward.")
        A("")
    elif longest_run >= 3:
        # Strong learner — the win is representative, celebrate it more
        A(f"You got **{longest_run} in a row right** at one point. "
          f"That's the level you're working at now.")
        A("")

    # The specific struggle, in plain English
    if miscon:
        top_mid, top_count = miscon.most_common(1)[0]
        if top_count >= 3:
            natural = _natural_misconception(top_mid)
            A(f"Here's what I've noticed. On {skill_label.lower()}, "
              f"you keep **{natural}**. {top_count} times this week. "
              f"That's a habit — and habits can be broken.")
            A("")

            # Only claim "you're getting closer" if we can back it with data
            # Compute pass rate on later attempts vs earlier
            _half = len(attempts_parsed) // 2
            _early = attempts_parsed[:_half]
            _late = attempts_parsed[_half:]
            _early_pass = sum(1 for a in _early if a["is_pass"]) / len(_early) if _early else 0
            _late_pass = sum(1 for a in _late if a["is_pass"]) / len(_late) if _late else 0
            if _late_pass > _early_pass + 0.1:
                A(f"Here's what I can prove: your accuracy improved from "
                  f"{_early_pass*100:.0f}% in the first half of the week to "
                  f"{_late_pass*100:.0f}% in the second. You're actually getting better.")
                A("")

    # The one next action
    if miscon:
        top_mid = miscon.most_common(1)[0][0]
        drill = _drill_for(top_mid, skill_label)
        A(f"**One thing to do next:** {drill}")
        A("")

    # The hook — an open invitation, not a command
    A("---")
    A("")
    if manual_variants > 0:
        A(f"You asked for **{manual_variants} extra practice question{'s' if manual_variants != 1 else ''}** on your own time this week. "
          f"That's not ordinary. Most students do the minimum. You didn't.")
        A("")
        A(f"Whenever you're ready, pick a new question. I'll be here.")
    else:
        A(f"When you're ready for the next one, just open the tutor and pick a question. "
          f"I'll remember where we left off.")
    A("")
    A("— Tanaka")
    A("")
    A(f"_(Week of {datetime.now(timezone.utc).strftime('%B %d, %Y')} · "
      f"{total} questions · {passes} right · {days}-day window)_")

    return "\n".join(L)


def _friendly_skill_name(skill_id):
    """skill_id → human label."""
    mapping = {
        "algebra.quadratic.solve": "Quadratic equations",
        "algebra.quadratic.inequality": "Quadratic inequalities",
        "algebra.surd.solve": "Surd equations",
        "algebra.simultaneous.solve": "Simultaneous equations",
        "algebra.exponential.solve": "Exponential equations",
        "trig.3d.length": "3D trigonometry",
        "trig.reduction.simplify": "Trig reduction",
    }
    return mapping.get(skill_id, skill_id.split(".")[-1].replace("_", " ").title())


def _drill_for(mid, skill_label):
    """Turn a misconception into a specific practice instruction."""
    mapping = {
        "M_SIGN_ERROR_READING_ROOT":
            "Ten questions on reading roots from brackets. "
            "Remember: the sign inside the bracket is the OPPOSITE of the root.",
        "M_ALG_SIGN_FLIP_FACTOR":
            "Ten questions on factorising with signs. "
            "Watch the middle term — it decides the signs.",
        "M_SIGN_ERROR_FACTORISATION":
            "Ten questions on factorising with signs. Slow down on the middle term.",
        "M_INCOMPLETE_ROOTS":
            "Ten questions where you write BOTH roots before pressing done.",
        "M_CALCULATION_ERROR":
            "Five questions where you write every step out loud before "
            "typing the final answer. No shortcuts.",
        "M_AND_OR_CONFUSION":
            "Five questions where you join roots with 'or'. "
            "The memo is strict about this.",
        "M_INEQ_MISSING_INTERVAL":
            "Five inequality questions where you always write TWO intervals. "
            "Sketch the parabola first.",
        "M_UNITS_IN_ANSWER":
            "Five 'solve for x' questions. Remember: just the number, no units.",
    }
    return mapping.get(mid, f"Practice more {skill_label.lower()}. One question at a time.")


def main():
    import sys
    learner = sys.argv[1] if len(sys.argv) > 1 else "tanaka"
    days = 7
    if len(sys.argv) > 2:
        try:
            days = int(sys.argv[2])
        except ValueError:
            pass
    letter = build_letter(learner, days)
    print(letter)

    # Save
    reports = ROOT / "data" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = reports / f"{learner}_letter_{ts}.md"
    out.write_text(letter, encoding="utf-8")
    print(f"\n\n📄 Saved: {out}")


if __name__ == "__main__":
    main()
