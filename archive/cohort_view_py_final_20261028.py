"""Cohort view — class-level analysis, teaching plan, and escalation surfacing.

Aggregates individual learner state into a class-level brief. Four tiers:
  needs_human — drill escalation reached escalate_human (highest priority)
  urgent      — multiple HIGH signals
  moderate    — some needs
  stable      — doing fine

A learner with an escalated drill is *never* mixed into urgent/moderate —
they get their own top-of-brief section with explicit human-intervention
action. That's the tutor naming its own limit at class level.

Usage:
    python scripts/cohort_view.py                                    # all learners
    python scripts/cohort_view.py thabo alice ben --days 30          # explicit cohort
"""
import sys
import json
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
PLANS_DIR = ROOT / "data" / "plans"
REPORTS = ROOT / "data" / "reports"


def _parse(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _is_pass(error_type):
    return str(error_type or "").lower() in ("none", "match")


def _display(learner_id):
    s = str(learner_id).strip()
    if not s or s.isdigit():
        return f"Learner {s}"
    return s.replace("_", " ").title()


def _friendly_skill(skill_id):
    mapping = {
        "algebra.quadratic.solve": "Quadratic equations",
        "algebra.quadratic.inequality": "Quadratic inequalities",
        "algebra.surd.solve": "Surd equations",
        "algebra.simultaneous.solve": "Simultaneous equations",
        "algebra.exponential.solve": "Exponential equations",
        "trig.3d.length": "3D trigonometry (length)",
        "trig.reduction.simplify": "Trig reduction",
    }
    return mapping.get(skill_id, skill_id.split(".")[-1].replace("_", " "))


def _friendly_misconception(mid):
    if not mid:
        return None
    mapping = {
        "M_SIGN_ERROR_READING_ROOT": "flips sign reading a root from a bracket",
        "M_ALG_SIGN_FLIP_FACTOR": "flips signs when factorising",
        "M_INCOMPLETE_ROOTS": "stops after one root",
        "M_CALCULATION_ERROR": "arithmetic slips",
        "M_AND_OR_CONFUSION": "uses 'and' instead of 'or'",
        "M_COORDINATE_SWAP": "swaps x and y",
        "M_COORDINATE_SIGN_FLIP": "flips a coordinate sign",
        "M_INCOMPLETE_PAIR": "gives only one of x/y",
        "M_SURD_CALCULATION_ERROR": "arithmetic slips in surd equations",
        "M_INEQ_MISSING_INTERVAL": "misses the second interval",
        "M_INEQ_SIGN_FLIP": "flips an interval sign",
        "M_UNITS_IN_ANSWER": "adds units to a number answer",
    }
    return mapping.get(mid, mid.replace("M_", "").replace("_", " ").lower())


def _compute_drill_escalation(events):
    """Detect whether any skill/misconception pair has escalated to
    'escalate_human' (3+ consecutive failed drills with no passes).

    Returns a list of {skill_id, misconception_id, failed_drills, total_drills}
    — one per escalated drill. Empty list = no escalation.
    """
    # Group by SKILL only (not by misconception_id). A drill is a drill —
    # three consecutive failed drills on the same skill is evidence the
    # approach isn't working, regardless of whether the misconception ids
    # line up across events. This also correctly handles legacy events
    # that were logged before misconception_id was added to the schema.
    by_skill = defaultdict(list)
    for e in events:
        if e.get("event_type") != "DRILL_OUTCOME":
            continue
        try:
            notes = json.loads(e.get("notes") or "{}")
        except (json.JSONDecodeError, TypeError):
            notes = {}
        skill = e.get("skill_id") or notes.get("skill_id") or "unknown"
        mid = notes.get("misconception_id")
        passed = bool(notes.get("drill_passed", False))
        by_skill[skill].append({
            "ts": e.get("timestamp") or "",
            "passed": passed,
            "mid": mid,
        })

    escalated = []
    for skill, drills in by_skill.items():
        drills.sort(key=lambda d: d["ts"])
        recent = drills[-3:]
        if len(recent) >= 3 and sum(1 for d in recent if d["passed"]) == 0:
            # Report the misconception that appears most among recent failures
            mids = [d["mid"] for d in recent if d["mid"]]
            top_mid = "legacy"
            if mids:
                top_mid = Counter(mids).most_common(1)[0][0]
            escalated.append({
                "skill_id": skill,
                "misconception_id": top_mid,
                "failed_drills": len(recent),
                "total_drills": len(drills),
            })
    return escalated


def gather_cohort(learner_ids, days):
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    if not learner_ids:
        rows = conn.execute(
            "SELECT DISTINCT learner_id FROM attempt ORDER BY learner_id"
        ).fetchall()
        learner_ids = [r[0] for r in rows]

    if not learner_ids:
        conn.close()
        return [], {}, {}, {}

    placeholders = ",".join("?" * len(learner_ids))

    attempts = [dict(r) for r in conn.execute(
        f"SELECT * FROM attempt WHERE learner_id IN ({placeholders}) "
        f"AND timestamp >= ? ORDER BY learner_id, timestamp",
        (*learner_ids, since),
    ).fetchall()]

    events = [dict(r) for r in conn.execute(
        f"SELECT * FROM learner_events WHERE learner_id IN ({placeholders}) "
        f"AND timestamp >= ? ORDER BY learner_id, timestamp",
        (*learner_ids, since),
    ).fetchall()]

    try:
        decisions = [dict(r) for r in conn.execute(
            f"SELECT * FROM mastery_decision WHERE learner_id IN ({placeholders}) "
            f"ORDER BY decided_at DESC",
            tuple(learner_ids),
        ).fetchall()]
    except sqlite3.OperationalError:
        decisions = []

    conn.close()

    by_learner_attempts = defaultdict(list)
    for a in attempts:
        a2 = dict(a)
        a2["ts"] = _parse(a["timestamp"])
        a2["is_pass"] = _is_pass(a["error_type"])
        if a2["ts"]:
            by_learner_attempts[a["learner_id"]].append(a2)

    by_learner_events = defaultdict(list)
    for e in events:
        by_learner_events[e["learner_id"]].append(e)

    by_learner_decisions = defaultdict(list)
    for d in decisions:
        by_learner_decisions[d["learner_id"]].append(d)

    return learner_ids, by_learner_attempts, by_learner_events, by_learner_decisions


def summarize_learner(learner_id, attempts, events, decisions):
    name = _display(learner_id)
    if not attempts:
        return {
            "learner_id": learner_id, "display_name": name, "active": False,
            "total_attempts": 0, "accuracy": 0.0, "misconceptions": {},
            "quits": 0, "manual_variants": 0, "pending_retention": 0,
            "top_misconception": None, "top_misconception_count": 0,
            "escalated_drills": [], "has_drill_escalation": False,
        }

    total = len(attempts)
    passes = sum(1 for a in attempts if a["is_pass"])
    accuracy = passes / total if total else 0
    miscon = Counter(a["misconception_id"] for a in attempts if a["misconception_id"])
    top = miscon.most_common(1)[0] if miscon else (None, 0)
    quits = sum(1 for e in events if e.get("event_type") == "QUIT_AFTER_VARIANTS")
    manual_variants = sum(1 for e in events if e.get("event_type") == "MANUAL_VARIANT_REQUEST")
    pending_retention = sum(1 for d in decisions if d.get("retention_status") in ("pending", "failed"))
    escalated = _compute_drill_escalation(events)

    return {
        "learner_id": learner_id, "display_name": name, "active": True,
        "total_attempts": total, "accuracy": accuracy,
        "misconceptions": dict(miscon), "quits": quits,
        "manual_variants": manual_variants, "pending_retention": pending_retention,
        "top_misconception": top[0], "top_misconception_count": top[1],
        "escalated_drills": escalated,
        "has_drill_escalation": len(escalated) > 0,
    }


def aggregate_class(learner_summaries, days):
    active = [l for l in learner_summaries if l["active"]]
    n_active = len(active)
    n_total = len(learner_summaries)

    miscon_learners = defaultdict(set)
    miscon_count = Counter()
    for l in active:
        for mid, cnt in l["misconceptions"].items():
            miscon_learners[mid].add(l["learner_id"])
            miscon_count[mid] += cnt

    whole_class_threshold = max(2, int(n_active * 0.20))
    small_group_threshold = 3

    whole_class = []
    small_group = []
    for mid, learners in miscon_learners.items():
        shared = len(learners)
        total_occurrences = miscon_count[mid]
        entry = {
            "misconception_id": mid,
            "display_misconception": _friendly_misconception(mid),
            "learners_affected": shared,
            "total_occurrences": total_occurrences,
            "percentage_of_active": round(shared / n_active * 100, 1) if n_active else 0,
            "learner_ids": sorted(learners),
        }
        if shared >= whole_class_threshold:
            whole_class.append(entry)
        elif shared >= small_group_threshold:
            small_group.append(entry)

    whole_class.sort(key=lambda x: -x["learners_affected"])
    small_group.sort(key=lambda x: -x["learners_affected"])

    needs_human, urgent, moderate, stable = [], [], [], []
    for l in active:
        high_signals = 0
        if l["pending_retention"] > 0: high_signals += 1
        if l["top_misconception_count"] >= 10: high_signals += 1
        if l["quits"] >= 2: high_signals += 1
        if l["total_attempts"] >= 30 and l["accuracy"] < 0.20: high_signals += 1
        if l.get("has_drill_escalation"): high_signals += 1

        bucket = {
            "learner_id": l["learner_id"],
            "display_name": l["display_name"],
            "accuracy": round(l["accuracy"], 3),
            "attempts": l["total_attempts"],
            "high_signals": high_signals,
            "top_misconception": l["top_misconception"],
            "pending_retention": l["pending_retention"],
            "quits": l["quits"],
            "escalated_drills": l.get("escalated_drills") or [],
            "has_drill_escalation": bool(l.get("has_drill_escalation")),
        }
        if bucket["has_drill_escalation"]:
            needs_human.append(bucket)
        elif high_signals >= 2:
            urgent.append(bucket)
        elif high_signals == 1:
            moderate.append(bucket)
        else:
            stable.append(bucket)

    needs_human.sort(key=lambda x: -x["high_signals"])
    urgent.sort(key=lambda x: (-x["high_signals"], x["accuracy"]))
    moderate.sort(key=lambda x: x["accuracy"])
    stable.sort(key=lambda x: -x["accuracy"])

    inactive = [l for l in learner_summaries if not l["active"]]

    return {
        "n_learners_total": n_total, "n_learners_active": n_active,
        "n_learners_inactive": len(inactive),
        "whole_class_misconceptions": whole_class,
        "small_group_misconceptions": small_group,
        "needs_human_learners": needs_human,
        "urgent_learners": urgent, "moderate_learners": moderate,
        "stable_learners": stable,
        "inactive_learners": [
            {"learner_id": l["learner_id"], "display_name": l["display_name"]}
            for l in inactive
        ],
        "thresholds": {
            "whole_class_learners": whole_class_threshold,
            "small_group_learners": small_group_threshold,
        },
        "window_days": days,
    }


def build_class_plan(learner_summaries, class_agg, days):
    plan = {
        "plan_version": "1.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "cohort", "window_days": days,
        "class_size": class_agg["n_learners_total"],
        "active_learners": class_agg["n_learners_active"],
        "inactive_learners": class_agg["n_learners_inactive"],
        "summary": {
            "whole_class_issue_count": len(class_agg["whole_class_misconceptions"]),
            "small_group_issue_count": len(class_agg["small_group_misconceptions"]),
            "needs_human_count": len(class_agg.get("needs_human_learners", [])),
            "urgent_learner_count": len(class_agg["urgent_learners"]),
            "moderate_learner_count": len(class_agg["moderate_learners"]),
            "stable_learner_count": len(class_agg["stable_learners"]),
        },
        "class_wide_actions": [],
        "small_group_actions": [],
        "needs_human_learners": class_agg.get("needs_human_learners", []),
        "individual_priorities": [],
        "stable_learners": class_agg["stable_learners"],
        "inactive_learners": class_agg["inactive_learners"],
        "thresholds": class_agg["thresholds"],
    }

    for idx, entry in enumerate(class_agg["whole_class_misconceptions"], 1):
        plan["class_wide_actions"].append({
            "action_id": f"class_act_{idx:03d}",
            "type": "class_lesson",
            "misconception_id": entry["misconception_id"],
            "display_misconception": entry["display_misconception"],
            "learners_affected": entry["learners_affected"],
            "total_occurrences": entry["total_occurrences"],
            "percentage_of_class": entry["percentage_of_active"],
            "instruction": (
                f"Teach this misconception to the whole class. "
                f"{entry['learners_affected']} of {class_agg['n_learners_active']} "
                f"active learners made this error. Suggested format: 15-minute "
                f"whiteboard walkthrough, then 3 rapid-fire questions."
            ),
            "success_criterion": (
                "Learners who previously made this error avoid it on next attempt."
            ),
            "affected_learner_ids": entry["learner_ids"],
        })

    for idx, entry in enumerate(class_agg["small_group_misconceptions"], 1):
        plan["small_group_actions"].append({
            "action_id": f"group_act_{idx:03d}",
            "type": "small_group_lesson",
            "misconception_id": entry["misconception_id"],
            "display_misconception": entry["display_misconception"],
            "learners_affected": entry["learners_affected"],
            "total_occurrences": entry["total_occurrences"],
            "instruction": (
                f"Small-group intervention for {entry['learners_affected']} "
                f"learners sharing this misconception. Pull aside during "
                f"individual work time."
            ),
            "success_criterion": "Each learner shows one clean attempt after mini-lesson.",
            "affected_learner_ids": entry["learner_ids"],
        })

    _priority_list = (
        class_agg.get("needs_human_learners", [])
        + class_agg["urgent_learners"]
        + class_agg["moderate_learners"]
    )
    for idx, learner in enumerate(_priority_list, 1):
        individual_plan_ref = None
        plan_files = list(PLANS_DIR.glob(learner["learner_id"] + "_plan_*.json")) if PLANS_DIR.exists() else []
        if plan_files:
            latest = max(plan_files, key=lambda p: p.stat().st_mtime)
            individual_plan_ref = str(latest.relative_to(ROOT))

        if learner in class_agg.get("needs_human_learners", []):
            _urgency = "needs_human"
        elif learner in class_agg["urgent_learners"]:
            _urgency = "urgent"
        else:
            _urgency = "moderate"

        plan["individual_priorities"].append({
            "priority_rank": idx,
            "learner_id": learner["learner_id"],
            "display_name": learner["display_name"],
            "urgency": _urgency,
            "high_signals": learner["high_signals"],
            "current_accuracy": learner["accuracy"],
            "attempts": learner["attempts"],
            "top_misconception": learner["top_misconception"],
            "top_misconception_display": _friendly_misconception(learner["top_misconception"]),
            "pending_retention_checks": learner["pending_retention"],
            "quits_after_variants": learner["quits"],
            "escalated_drills": learner.get("escalated_drills") or [],
            "individual_plan_ref": individual_plan_ref,
            "action": (
                f"Human intervention recommended for {learner['display_name']} — "
                f"drill has exhausted the digital approach. Escalate to in-person "
                f"tutoring for the escalated skill."
                if _urgency == "needs_human"
                else f"Review {learner['display_name']}'s individual plan before "
                     f"next 1-on-1 check-in."
            ),
        })

    return plan


def render_class_brief(class_plan):
    L = []
    A = L.append

    A("# Class Teaching Brief")
    A("")
    gen = datetime.fromisoformat(class_plan["generated_at"].replace("Z", "+00:00"))
    A(f"*Generated {gen.strftime('%B %d, %Y')} · "
      f"covering the last {class_plan['window_days']} days · "
      f"{class_plan['active_learners']} active learners*")
    A("")

    s = class_plan["summary"]
    A("## At a glance")
    A("")
    A(f"- **Active learners:** {class_plan['active_learners']} of {class_plan['class_size']}")
    _inactive_names = [l["display_name"] for l in class_plan["inactive_learners"]]
    A(f"- **Inactive (no attempts):** {len(_inactive_names)} "
      + (f"({', '.join(_inactive_names)})" if _inactive_names else ""))
    A(f"- **Class-wide misconceptions:** {s['whole_class_issue_count']}")
    A(f"- **Small-group misconceptions:** {s['small_group_issue_count']}")
    A(f"- **Needs human intervention:** {s.get('needs_human_count', 0)} "
      f"(digital drill exhausted)")
    A(f"- **Urgent learners:** {s['urgent_learner_count']}")
    A(f"- **Moderate learners:** {s['moderate_learner_count']}")
    A(f"- **Stable learners:** {s['stable_learner_count']}")
    A("")

    _needs_human = class_plan.get("needs_human_learners", [])
    if _needs_human:
        A("## 🚨 Needs human intervention — digital approach exhausted")
        A("")
        A("These learners have been drilled on the same misconception 3+ times "
          "and it hasn't broken. Recommend in-person tutoring for the escalated "
          "skill, while keeping digital practice going on adjacent skills.")
        A("")
        A("| Learner | Accuracy | Escalated skill | Misconception | Failed drills |")
        A("|---|---|---|---|---|")
        for l in _needs_human:
            for drill in (l.get("escalated_drills") or [{}]):
                skill = _friendly_skill(drill.get("skill_id", "?"))
                mid = _friendly_misconception(drill.get("misconception_id"))
                failed = drill.get("failed_drills", 3)
                A(f"| {l['display_name']} | {l['accuracy']*100:.0f}% | "
                  f"{skill} | {mid or '—'} | {failed} |")
        A("")
        A("*Action: the parent letter for these learners already fires the "
          "human-tutor recommendation. Follow up directly.*")
        A("")

    A("## Teach the whole class this week")
    A("")
    if not class_plan["class_wide_actions"]:
        A(f"*No shared misconceptions reached the whole-class threshold "
          f"({class_plan['thresholds']['whole_class_learners']}+ learners).*")
        A("")
    else:
        for action in class_plan["class_wide_actions"]:
            A(f"### 🎯 {action['display_misconception']}")
            A("")
            A(f"**Affected:** {action['learners_affected']} learners "
              f"({action['percentage_of_class']}% of class), "
              f"{action['total_occurrences']} occurrences.")
            A("")
            A(f"**What to do:** {action['instruction']}")
            A("")

    if class_plan["small_group_actions"]:
        A("## Small-group interventions")
        A("")
        for action in class_plan["small_group_actions"]:
            A(f"### 👥 {action['display_misconception']}")
            A("")
            A(f"**Affected:** {action['learners_affected']} learners, "
              f"{action['total_occurrences']} occurrences.")
            A("")
            A(f"**What to do:** {action['instruction']}")
            A("")

    A("## Individual learner priorities")
    A("")
    if not class_plan["individual_priorities"]:
        A("*No learners need individual intervention this cycle.*")
        A("")
    else:
        A("| # | Learner | Urgency | Accuracy | Top misconception | Retention |")
        A("|---|---|---|---|---|---|")
        for p in class_plan["individual_priorities"]:
            if p["urgency"] == "needs_human":
                urg = "🚨 needs human"
            elif p["urgency"] == "urgent":
                urg = "🔴 urgent"
            else:
                urg = "🟡 moderate"
            mid = p["top_misconception_display"] or "—"
            ret = f"{p['pending_retention_checks']} pending" if p["pending_retention_checks"] else "—"
            A(f"| {p['priority_rank']} | {p['display_name']} | {urg} | "
              f"{p['current_accuracy']*100:.0f}% | {mid} | {ret} |")
        A("")

    if class_plan["stable_learners"]:
        A("## Doing fine — no action needed")
        A("")
        names = [l["display_name"] for l in class_plan["stable_learners"]]
        A(f"{len(names)} learners are progressing without concerning signals: "
          f"{', '.join(names)}.")
        A("")

    if class_plan["inactive_learners"]:
        A("## No activity this cycle")
        A("")
        names = [l["display_name"] for l in class_plan["inactive_learners"]]
        _word = "learner" if len(names) == 1 else "learners"
        A(f"{len(names)} {_word} recorded no attempts: {', '.join(names)}.")
        A("")

    A("---")
    A("")
    A(f"*Class-wide threshold: {class_plan['thresholds']['whole_class_learners']} "
      f"learners. Small-group threshold: {class_plan['thresholds']['small_group_learners']}. "
      f"Needs-human bucket: drill escalation reached escalate_human.*")
    A("")
    A(f"*This brief is a rendering of `data/plans/class_plan_*.json`.*")

    return "\n".join(L)


def generate_class_view(learner_ids=None, days=30):
    ids, attempts_by, events_by, decisions_by = gather_cohort(learner_ids or [], days)

    if not ids:
        print("No learners found in database.")
        return None, None, None

    summaries = []
    for lid in ids:
        summaries.append(summarize_learner(
            lid, attempts_by.get(lid, []), events_by.get(lid, []),
            decisions_by.get(lid, []),
        ))

    class_agg = aggregate_class(summaries, days)
    class_plan = build_class_plan(summaries, class_agg, days)
    md = render_class_brief(class_plan)

    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    plan_path = PLANS_DIR / f"class_plan_{ts}.json"
    brief_path = REPORTS / f"class_brief_{ts}.md"

    plan_path.write_text(json.dumps(class_plan, indent=2), encoding="utf-8")
    brief_path.write_text(md, encoding="utf-8")

    return md, plan_path, brief_path


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    days = 30
    if "--days" in sys.argv:
        try:
            days = int(sys.argv[sys.argv.index("--days") + 1])
        except (ValueError, IndexError):
            pass

    learner_ids = args if args else None
    md, plan_path, brief_path = generate_class_view(learner_ids, days)
    if md:
        print(md)
        print(f"\n\n📋 Class plan:  {plan_path}")
        print(f"📄 Class brief: {brief_path}")


if __name__ == "__main__":
    main()
