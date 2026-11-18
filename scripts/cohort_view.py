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


def _chunked_fetch(conn, sql, params, learner_ids, chunk=500):
    out = []
    for i in range(0, len(learner_ids), chunk):
        sub = learner_ids[i:i + chunk]
        ph = ",".join("?" * len(sub))
        out.extend(conn.execute(
            sql.format(placeholders=ph), (*sub, *params)
        ).fetchall())
    return out


def _agg_accuracy(active):
    total = sum(l["total_attempts"] for l in active)
    passes = sum(l.get("passes", 0) for l in active)
    return (passes / total) if total else 0.0


def _agg_accuracy_ci(active, z=1.96):
    n = sum(l["total_attempts"] for l in active)
    p = _agg_accuracy(active)
    if n == 0:
        return (0.0, 0.0)
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


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

    attempts = [dict(r) for r in _chunked_fetch(
        conn,
        "SELECT * FROM attempt WHERE learner_id IN ({placeholders}) "
        "AND timestamp >= ? ORDER BY learner_id, timestamp",
        (since,), learner_ids,
    )]

    events = [dict(r) for r in _chunked_fetch(
        conn,
        "SELECT * FROM learner_events WHERE learner_id IN ({placeholders}) "
        "AND timestamp >= ? ORDER BY learner_id, timestamp",
        (since,), learner_ids,
    )]

    try:
        decisions = [dict(r) for r in _chunked_fetch(
            conn,
            "SELECT * FROM mastery_decision WHERE learner_id IN ({placeholders}) "
            "ORDER BY decided_at DESC",
            (), learner_ids,
        )]
    except sqlite3.OperationalError as e:
        print(f"[cohort_view] WARN: mastery_decision unavailable: {e}",
              file=sys.stderr)
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
            "total_attempts": 0, "passes": 0, "accuracy": 0.0,
            "misconceptions": {},
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
        "total_attempts": total, "passes": passes, "accuracy": accuracy,
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

    WHOLE_CLASS_ABS = 5
    SMALL_GROUP_ABS = 5
    SMALL_GROUP_CAP = 200
    whole_class_threshold = max(WHOLE_CLASS_ABS, int(n_active * 0.20))
    small_group_threshold = SMALL_GROUP_ABS
    small_group_cap = SMALL_GROUP_CAP

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
        elif small_group_threshold <= shared <= small_group_cap:
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
        "aggregate_accuracy": _agg_accuracy(active),
        "aggregate_accuracy_ci": _agg_accuracy_ci(active),
        "census_or_sample": "census",
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
            "small_group_cap": small_group_cap,
        },
        "window_days": days,
    }


def build_class_plan(learner_summaries, class_agg, days, data_version=None):
    _dv = data_version or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    plan = {
        "plan_version": "1.2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_version": _dv,
        "scope": "cohort", "window_days": days,
        "census_or_sample": class_agg.get("census_or_sample", "census"),
        "class_size": class_agg["n_learners_total"],
        "active_learners": class_agg["n_learners_active"],
        "inactive_learners": class_agg["n_learners_inactive"],
        "summary": {
            "aggregate_accuracy": class_agg.get("aggregate_accuracy", 0.0),
            "aggregate_accuracy_ci": class_agg.get("aggregate_accuracy_ci", (0.0, 0.0)),
            "census_or_sample": class_agg.get("census_or_sample", "census"),
            "whole_class_issue_count": len(class_agg["whole_class_misconceptions"]),
            "small_group_issue_count": len(class_agg["small_group_misconceptions"]),
            "needs_human_count": len(class_agg.get("needs_human_learners", [])),
            "urgent_learner_count": len(class_agg["urgent_learners"]),
            "moderate_learner_count": len(class_agg["moderate_learners"]),
            "stable_learner_count": len(class_agg["stable_learners"]),
        },
        "conversation_summary": {
            "status": "not_yet_captured",
            "questions_asked": None,
            "answers_given": None,
            "answer_acceptance_rate": None,
            "improvement_after_answer": None,
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
        plan_files = list(PLANS_DIR.glob(str(learner["learner_id"]) + "_plan_*.json")) if PLANS_DIR.exists() else []
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
    _active_word = "learner" if class_plan['active_learners'] == 1 else "learners"
    A(f"*Generated {gen.strftime('%B %d, %Y')} · "
      f"covering the last {class_plan['window_days']} days · "
      f"{class_plan['active_learners']} active {_active_word}*")
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

    _acc = s.get("aggregate_accuracy", 0.0)
    _ci = s.get("aggregate_accuracy_ci", (0.0, 0.0))
    A(f"- **Aggregate accuracy:** {_acc*100:.1f}% "
      f"(95% CI {_ci[0]*100:.1f}–{_ci[1]*100:.1f}%) — attempt-pooled")
    A(f"- **Report scope:** {s.get('census_or_sample', 'census')}")
    A("")

    A("## Distribution by state")
    A("")
    A("| State | Learners | % of active |")
    A("|---|---|---|")
    _n = max(1, class_plan["active_learners"])
    A(f"| Needs human | {s.get('needs_human_count', 0)} | "
      f"{s.get('needs_human_count', 0)/_n*100:.1f}% |")
    A(f"| Urgent | {s['urgent_learner_count']} | {s['urgent_learner_count']/_n*100:.1f}% |")
    A(f"| Moderate | {s['moderate_learner_count']} | {s['moderate_learner_count']/_n*100:.1f}% |")
    A(f"| Stable | {s['stable_learner_count']} | {s['stable_learner_count']/_n*100:.1f}% |")
    A("")

    _needs_human = class_plan.get("needs_human_learners", [])
    if _needs_human:
        A("## 🚨 Needs human intervention — digital approach exhausted")
        A("")
        A("These learners have been drilled on the same misconception 3+ times "
          "and it hasn't broken. Recommend in-person tutoring for the escalated "
          "skill, while keeping digital practice going on adjacent skills.")
        A("")
        _nh_top = _needs_human[:20]
        if len(_needs_human) > 20:
            A(f"*Showing top {len(_nh_top)} of {len(_needs_human)} learners. "
              f"Full list in `data/plans/class_plan_*.json`.*")
            A("")
        A("| Learner | Accuracy | Escalated skill | Misconception | Failed drills |")
        A("|---|---|---|---|---|")
        for l in _nh_top:
            for drill in (l.get("escalated_drills") or [{}]):
                skill = _friendly_skill(drill.get("skill_id", "?"))
                mid = _friendly_misconception(drill.get("misconception_id"))
                failed = drill.get("failed_drills", 3)
                A(f"| {l['display_name']} | {l['accuracy']*100:.0f}% | "
                  f"{skill} | {mid or '—'} | {failed} |")
        A("")
        if len(_needs_human) > 20:
            A(f"*{len(_needs_human) - len(_nh_top)} more learners in this bucket "
              f"— see full list in JSON.*")
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
    _priorities = class_plan["individual_priorities"]
    if not _priorities:
        A("*No learners need individual intervention this cycle.*")
        A("")
    else:
        _top_n = _priorities[:20]
        _total = len(_priorities)
        if _total > len(_top_n):
            A(f"*Showing top {len(_top_n)} of {_total} learners. "
              f"Full list in `data/plans/class_plan_*.json`.*")
            A("")
        A("| # | Learner | Urgency | Accuracy | Top misconception | Retention |")
        A("|---|---|---|---|---|---|")
        for p in _top_n:
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
        _by_urgency = Counter(p["urgency"] for p in _priorities)
        A(f"*Breakdown of all {_total}: needs human {_by_urgency.get('needs_human', 0)}, "
          f"urgent {_by_urgency.get('urgent', 0)}, "
          f"moderate {_by_urgency.get('moderate', 0)}.*")
        A("")

    if class_plan["stable_learners"]:
        A("## Doing fine — no action needed")
        A("")
        names = [l["display_name"] for l in class_plan["stable_learners"]]
        if len(names) <= 10:
            A(f"{len(names)} learners are progressing without concerning signals: "
              f"{', '.join(names)}.")
        else:
            A(f"{len(names)} learners are progressing without concerning signals. "
              f"Full list in `data/plans/class_plan_*.json`.")
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
      f"learners. Small-group threshold: {class_plan['thresholds']['small_group_learners']} "
      f"(capped at {class_plan['thresholds'].get('small_group_cap', 200)}). "
      f"Needs-human bucket: drill escalation reached escalate_human.*")
    A("")
    A(f"*This brief is a rendering of `data/plans/class_plan_*.json`.*")

    return "\n".join(L)


def generate_class_view(learner_ids=None, days=30, use_node=None, node_id=None):
    """Generate class view.

    use_node:
      None  - auto: read node if fresh (<24h), else raw
      True  - force node (warns + falls back if stale/missing)
      False - force raw aggregation
    node_id: which node to read. Defaults to 'default_class'.
    """
    if use_node is True or (use_node is None and node_id):
        try:
            sys.path.insert(0, str(ROOT))
            from src.tutor.cohort_nodes import get_node, list_members
            target_node = node_id or "default_class"
            node = get_node(target_node)
            if node:
                computed = datetime.fromisoformat(node["computed_at"].replace("Z", "+00:00"))
                age = (datetime.now(timezone.utc) - computed).total_seconds()
                is_fresh = age < 86400
                if is_fresh:
                    members = list_members(target_node)
                    return _render_from_node(node, members, days)
                elif use_node is True:
                    print(f"  [node {target_node} is stale ({age/3600:.1f}h) - using raw]")
        except Exception as e:
            print(f"  [node read failed: {e} - falling back to raw]")

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

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    class_agg = aggregate_class(summaries, days)
    class_plan = build_class_plan(summaries, class_agg, days, data_version=ts)
    md = render_class_brief(class_plan)

    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    plan_path = PLANS_DIR / f"class_plan_{ts}.json"
    brief_path = REPORTS / f"class_brief_{ts}.md"

    plan_path.write_text(json.dumps(class_plan, indent=2), encoding="utf-8")
    brief_path.write_text(md, encoding="utf-8")

    return md, plan_path, brief_path


def _render_from_node(node, member_ids, days):
    """Render brief from node snapshot. O(1) path: one row read, one file write."""
    plan = {
        "plan_version": "1.3-node",
        "generated_at": node["computed_at"],
        "data_version": node["data_version"],
        "source": "node",
        "scope": "cohort",
        "window_days": days,
        "census_or_sample": "census",
        "class_size": node["learner_count"],
        "active_learners": node["active_count"],
        "inactive_learners": node["state_distribution"].get("inactive", 0),
        "summary": {
            "aggregate_accuracy": (
                node["pass_count"] / node["attempt_count"]
                if node["attempt_count"] else 0.0
            ),
            "aggregate_accuracy_ci": (0.0, 0.0),
            "census_or_sample": "census",
            "whole_class_issue_count": 0,
            "small_group_issue_count": 0,
            "needs_human_count": node["state_distribution"].get("needs_human", 0),
            "urgent_learner_count": node["state_distribution"].get("urgent", 0),
            "moderate_learner_count": node["state_distribution"].get("moderate", 0),
            "stable_learner_count": node["state_distribution"].get("stable", 0),
        },
        "conversation_summary": {
            "status": "not_yet_captured" if node.get("questions_asked") is None else "captured",
            "questions_asked": node.get("questions_asked"),
            "answers_given": node.get("answers_given"),
            "answer_acceptance_rate": node.get("answer_acceptance"),
            "improvement_after_answer": node.get("improvement_after"),
        },
        "class_wide_actions": [],
        "small_group_actions": [],
        "needs_human_learners": [],
        "individual_priorities": [],
        "stable_learners": [],
        "inactive_learners": [],
        "thresholds": node.get("threshold_snapshot", {}),
    }
    md = render_class_brief(plan)

    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    plan_path = PLANS_DIR / f"class_plan_{ts}.json"
    brief_path = REPORTS / f"class_brief_{ts}.md"
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    brief_path.write_text(md, encoding="utf-8")
    return md, plan_path, brief_path


def main():
    import argparse
    p = argparse.ArgumentParser(description="Class teaching brief.")
    p.add_argument("learner_ids", nargs="*",
                   help="Explicit learner IDs (default: all)")
    p.add_argument("--days", type=int, default=30,
                   help="Window in days (default: 30)")
    a = p.parse_args()

    learner_ids = a.learner_ids or None
    md, plan_path, brief_path = generate_class_view(learner_ids, a.days)
    if md:
        print(md)
        print(f"\n\n📋 Class plan:  {plan_path}")
        print(f"🗺️ Class brief: {brief_path}")


if __name__ == "__main__":
    main()