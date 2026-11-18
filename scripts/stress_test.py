"""Targeted stress test for cohort_view.py scale verification.

Creates a temp DB with 1,000 synthetic learners designed to exercise:
  - Chunked fetch (>500 learners, two batches)
  - Whole-class misconception (280 learners share M_SIGN_ERROR_READING_ROOT)
  - Small-group misconception (60 learners share M_INCOMPLETE_ROOTS)
  - Truncation (>20 priority learners → "Showing top 20 of N")
  - Needs-human bucket (30 learners with 3 failed drill outcomes)
  - Threshold arithmetic at scale (whole_class_threshold = 200 at n=1000)

Runs generate_class_view against the temp DB, then removes it.
Prints PASS/FAIL for 11 checks. Exits 0 if all pass, 1 otherwise.

Usage:
    py scripts\\stress_test.py
"""
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
import scripts.cohort_view as cv


SKILL = "algebra.quadratic.solve"
M_WHOLE_CLASS = "M_SIGN_ERROR_READING_ROOT"
M_SMALL_GROUP = "M_INCOMPLETE_ROOTS"


def _ts(days_ago=0, hours_ago=0):
    return (datetime.now(timezone.utc)
            - timedelta(days=days_ago, hours=hours_ago)).isoformat()


def _create_db(path):
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE attempt (
            attempt_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            learner_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            response TEXT,
            diagnosis_rule_id TEXT,
            misconception_id TEXT,
            hint_level TEXT,
            error_type TEXT,
            evidence_json TEXT,
            question_id TEXT
        );
        CREATE TABLE learner_events (
            event_id TEXT PRIMARY KEY,
            learner_id TEXT NOT NULL,
            skill_id TEXT,
            question_id TEXT,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            notes TEXT,
            session_id TEXT
        );
        CREATE TABLE mastery_decision (
            decision_id TEXT PRIMARY KEY,
            learner_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            policy_version TEXT NOT NULL,
            decided_at TEXT NOT NULL,
            tier_at_decision TEXT NOT NULL,
            evidence_json TEXT,
            question_ids TEXT,
            skill_coverage TEXT,
            retention_due_at TEXT NOT NULL,
            retention_status TEXT NOT NULL DEFAULT 'pending',
            retention_attempted_at TEXT,
            retention_pass_result INTEGER,
            retention_question_ids TEXT,
            retention_evidence_json TEXT,
            notes TEXT
        );
    """)
    conn.commit()
    return conn


def _add_attempts(conn, learner_id, misconception_id, n_attempts, pass_fraction):
    """Add n_attempts; pass_fraction of them are passes, rest are the misconception."""
    n_pass = int(n_attempts * pass_fraction)
    for i in range(n_attempts):
        is_pass = i < n_pass
        conn.execute(
            "INSERT INTO attempt VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                f"att_{learner_id}_{i}",
                f"sess_{learner_id}",
                learner_id,
                SKILL,
                _ts(days_ago=1, hours_ago=i),
                "x = 5",
                None,
                None if is_pass else misconception_id,
                None,
                "none" if is_pass else "wrong",
                "{}",
                "2025_P1_Q1.1.1",
            ),
        )


def _add_drill_escalation(conn, learner_id):
    """Three DRILL_OUTCOME events, all failed → triggers has_drill_escalation."""
    for i in range(3):
        notes = json.dumps({
            "skill_id": SKILL,
            "misconception_id": M_WHOLE_CLASS,
            "drill_passed": False,
        })
        conn.execute(
            "INSERT INTO learner_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                f"evt_{learner_id}_{i}",
                learner_id,
                SKILL,
                "2025_P1_Q1.1.1",
                "DRILL_OUTCOME",
                _ts(hours_ago=i),
                notes,
                f"sess_{learner_id}",
            ),
        )


def _populate(conn):
    # 250 learners sharing M_SIGN_ERROR_READING_ROOT (whole_class at n=1000)
    for i in range(250):
        lid = f"wc_{i:04d}"
        _add_attempts(conn, lid, M_WHOLE_CLASS, 40, 0.40)

    # 60 learners sharing M_INCOMPLETE_ROOTS (small_group at n=1000)
    for i in range(60):
        lid = f"sg_{i:04d}"
        _add_attempts(conn, lid, M_SMALL_GROUP, 40, 0.50)

    # 30 learners with drill escalation → needs_human bucket
    for i in range(30):
        lid = f"human_{i:04d}"
        _add_attempts(conn, lid, M_WHOLE_CLASS, 40, 0.30)
        _add_drill_escalation(conn, lid)

    # 660 stable learners (no failures, no signals)
    for i in range(660):
        lid = f"stable_{i:04d}"
        _add_attempts(conn, lid, None, 20, 0.85)

    conn.commit()


def main():
    temp_db = cv.ROOT / "data" / "learner_store" / "learners_stress_test.db"
    print(f"Creating temp DB: {temp_db}")
    conn = _create_db(temp_db)
    print("Populating 1,000 learners ...")
    _populate(conn)
    conn.close()

    original_db = cv.DB
    cv.DB = temp_db
    print(f"Pointed cohort_view at: {temp_db}")

    try:
        print("\nRunning generate_class_view(days=30) ...")
        md, plan_path, brief_path = cv.generate_class_view(days=30)
        if md is None:
            print("ERROR: generate_class_view returned None")
            return 1

        with open(plan_path, encoding="utf-8") as f:
            plan = json.load(f)

        brief_len = len(md)
        n_prio = len(plan["individual_priorities"])
        checks = [
            ("Chunked fetch: 1000 learners active",
             plan["active_learners"] == 1000,
             f"{plan['active_learners']} active"),
            ("Chunked fetch: accuracy matches expectation (~62.6%)",
             0.60 <= plan["summary"]["aggregate_accuracy"] <= 0.65,
             f"{plan['summary']['aggregate_accuracy']*100:.1f}%"),
            ("Brief length < 10,000 chars",
             brief_len < 10000,
             f"{brief_len:,} chars"),
            ("Priorities > 20 (truncation triggers)",
             n_prio > 20,
             f"{n_prio} priorities"),
            ("Truncation label appears",
             "Showing top 20 of" in md,
             "yes" if "Showing top 20 of" in md else "NO"),
            ("Whole-class threshold at scale = 200",
             "Class-wide threshold: 200" in md,
             "yes" if "Class-wide threshold: 200" in md else "NO"),
            ("Whole-class section populated",
             len(plan["class_wide_actions"]) > 0,
             f"{len(plan['class_wide_actions'])} whole-class"),
            ("Small-group section populated",
             len(plan["small_group_actions"]) > 0,
             f"{len(plan['small_group_actions'])} small groups"),
            ("60-learner cluster is small_group (not whole_class)",
             any(s["learners_affected"] == 60 for s in plan["small_group_actions"]),
             "yes" if any(s["learners_affected"] == 60 for s in plan["small_group_actions"]) else "NO"),
            ("Needs-human count == 30",
             plan["summary"]["needs_human_count"] == 30,
             f"{plan['summary']['needs_human_count']} needs human"),
            ("data_version present",
             bool(plan.get("data_version")),
             plan.get("data_version", "MISSING")),
            ("conversation_summary reserved",
             plan.get("conversation_summary", {}).get("status") == "not_yet_captured",
             plan.get("conversation_summary", {}).get("status", "MISSING")),
        ]

        print("\n" + "=" * 64)
        print("PASS / FAIL")
        print("=" * 64)
        all_pass = True
        for label, passed, detail in checks:
            mark = "PASS" if passed else "FAIL"
            print(f"  [{mark}] {label}: {detail}")
            if not passed:
                all_pass = False

        print("=" * 64)
        print(f"RESULT: {'A IS CLOSED' if all_pass else 'FAILURES ABOVE'}")
        print("=" * 64)

        print("\n--- Brief excerpt (first 1200 chars) ---")
        print(md[:1200])

        return 0 if all_pass else 1

    finally:
        cv.DB = original_db
        if temp_db.exists():
            temp_db.unlink()
            print(f"\nRemoved {temp_db}")


if __name__ == "__main__":
    sys.exit(main())