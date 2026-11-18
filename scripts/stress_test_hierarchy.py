"""stress_test_hierarchy.py — B2 verification.

Builds national -> province -> 2 districts -> 4 schools -> 8 classes
with 1000 learners. Rebuilds cascades, verifies rollups.
Self-cleans.

Usage:  py scripts\\stress_test_hierarchy.py
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.tutor import cohort_nodes
from src.tutor.cohort_nodes import (
    ensure_schema, create_node, add_member, rebuild_node,
    rebuild_cascade, get_node, get_ancestors, list_descendant_learners,
)


def _ts(days_ago=0):
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def _create_temp_db(path):
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE attempt (
            attempt_id TEXT PRIMARY KEY, session_id TEXT NOT NULL,
            learner_id TEXT NOT NULL, skill_id TEXT NOT NULL,
            timestamp TEXT NOT NULL, response TEXT, diagnosis_rule_id TEXT,
            misconception_id TEXT, hint_level TEXT, error_type TEXT,
            evidence_json TEXT, question_id TEXT
        );
        CREATE TABLE learner_events (
            event_id TEXT PRIMARY KEY, learner_id TEXT NOT NULL, skill_id TEXT,
            question_id TEXT, event_type TEXT NOT NULL, timestamp TEXT NOT NULL,
            notes TEXT, session_id TEXT
        );
        CREATE TABLE mastery_decision (
            decision_id TEXT PRIMARY KEY, learner_id TEXT NOT NULL,
            skill_id TEXT NOT NULL, policy_version TEXT NOT NULL,
            decided_at TEXT NOT NULL, tier_at_decision TEXT NOT NULL,
            evidence_json TEXT, question_ids TEXT, skill_coverage TEXT,
            retention_due_at TEXT NOT NULL,
            retention_status TEXT NOT NULL DEFAULT 'pending',
            retention_attempted_at TEXT, retention_pass_result INTEGER,
            retention_question_ids TEXT, retention_evidence_json TEXT, notes TEXT
        );
        CREATE TABLE learner (
            learner_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL, last_seen TEXT NOT NULL
        );
    """)
    conn.commit()
    return conn


def _populate_hierarchy(conn):
    N = 1000
    classes = 8
    SKILL = "algebra.quadratic.solve"
    M = "M_SIGN_ERROR_READING_ROOT"

    create_node("national", "national", "South Africa", None, conn=conn)
    create_node("province_1", "province", "Province 1", "national", conn=conn)
    for d in range(2):
        dist_id = f"district_{d}"
        create_node(dist_id, "district", f"District {d}", "province_1", conn=conn)
        for s in range(2):
            school_id = f"school_{d}_{s}"
            create_node(school_id, "school", f"School {d}-{s}", dist_id, conn=conn)
            for c in range(2):
                class_id = f"class_{d}_{s}_{c}"
                create_node(class_id, "class", f"Class {d}-{s}-{c}", school_id, conn=conn)

    for i in range(N):
        class_idx = i % classes
        d = class_idx // 4
        s = (class_idx % 4) // 2
        c = class_idx % 2
        class_id = f"class_{d}_{s}_{c}"

        lid = f"L{i:04d}"
        conn.execute("INSERT INTO learner VALUES (?, ?, ?)", (lid, _ts(), _ts()))
        add_member(lid, class_id, conn=conn)

        for j in range(20):
            is_pass = j < 8
            conn.execute(
                "INSERT INTO attempt VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (f"att_{lid}_{j}", f"sess_{lid}", lid, SKILL,
                 _ts(days_ago=1), "x=5", None,
                 None if is_pass else M,
                 None, "none" if is_pass else "wrong", "{}", "Q1"),
            )
    conn.commit()


def main():
    temp_db = ROOT / "data" / "learner_store" / "learners_hierarchy_stress.db"
    print(f"Creating temp DB: {temp_db}")
    conn = _create_temp_db(temp_db)
    ensure_schema(conn)
    print("Building hierarchy + 1000 learners ...")
    _populate_hierarchy(conn)

    original_db = cohort_nodes.DB
    cohort_nodes.DB = temp_db

    try:

        print("Cascade rebuild from each class ...")
        for d in range(2):
            for s in range(2):
                for c in range(2):
                    rebuild_cascade(f"class_{d}_{s}_{c}", conn=conn)

        print("Verifying consistency ...")

        class_checks = []
        for d in range(2):
            for s in range(2):
                for c in range(2):
                    class_id = f"class_{d}_{s}_{c}"
                    node = get_node(class_id, conn=conn)
                    class_checks.append(node["learner_count"] == 125)
        classes_ok = all(class_checks)

        national = get_node("national", conn=conn)
        national_ok = national["learner_count"] == 1000
        attempts_ok = national["attempt_count"] == 20000
        pass_ok = national["pass_count"] == 8000

        ancestors = get_ancestors("class_0_0_0", conn=conn)
        ancestors_ok = ancestors == ["school_0_0", "district_0", "province_1", "national"]

        parents_ok = True
        for d in range(2):
            dist_id = f"district_{d}"
            dist = get_node(dist_id, conn=conn)
            sum_schools = sum(
                get_node(f"school_{d}_{s}", conn=conn)["learner_count"]
                for s in range(2)
            )
            if dist["learner_count"] != sum_schools:
                parents_ok = False
                break

        checks = [
            ("8 class nodes each have 125 learners", classes_ok,
             "yes" if classes_ok else "MISMATCH"),
            ("national learner_count = 1000", national_ok,
             f"{national['learner_count']}"),
            ("national attempt_count = 20000", attempts_ok,
             f"{national['attempt_count']}"),
            ("national pass_count = 8000", pass_ok,
             f"{national['pass_count']}"),
            ("get_ancestors returns 4 levels", ancestors_ok,
             f"{len(ancestors)} levels: {ancestors}"),
            ("district learner_count = sum of schools", parents_ok,
             "yes" if parents_ok else "MISMATCH"),
        ]

        print("\n" + "=" * 64)
        print("PASS / FAIL - B2 hierarchy checks")
        print("=" * 64)
        all_pass = True
        for label, passed, detail in checks:
            mark = "PASS" if passed else "FAIL"
            print(f"  [{mark}] {label}: {detail}")
            if not passed:
                all_pass = False
        print("=" * 64)
        print(f"RESULT: {'B2 IS CLOSED' if all_pass else 'FAILURES ABOVE'}")
        print("=" * 64)

        if not all_pass:
            print("\nNational snapshot:")
            for k in ("learner_count", "active_count", "attempt_count",
                      "pass_count", "state_distribution"):
                print(f"  {k}: {national.get(k)}")

        return 0 if all_pass else 1
    finally:
        cohort_nodes.DB = original_db
        try:
            conn.close()
        except Exception:
            pass
        if temp_db.exists():
            try:
                temp_db.unlink()
                print(f"\nRemoved {temp_db}")
            except PermissionError:
                print(f"\n  (could not remove {temp_db})")


if __name__ == "__main__":
    sys.exit(main())
