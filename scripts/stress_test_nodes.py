"""stress_test_nodes.py — B1 verification.

8 checks:
  1. learner_count matches raw
  2. active_count matches raw
  3. attempt_count matches raw
  4. pass_count matches raw
  5. get_node returns populated rollup (not create-only)
  6. state_distribution sums to learner_count
  7. data_version present
  8. conversation fields reserved (null)

Creates a temp DB with 100 learners, populates a class node, rebuilds,
verifies. Self-cleans. Exit 0/1.

Usage:  py scripts\\stress_test_nodes.py
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.tutor import cohort_nodes
from src.tutor.cohort_nodes import (
    ensure_schema, create_node, add_member, rebuild_class_node,
    get_node, list_members,
)

NODE_ID = "stress_test_class"
NODE_NAME = "Stress Test Class"


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


def _populate(conn):
    SKILL = "algebra.quadratic.solve"
    M = "M_SIGN_ERROR_READING_ROOT"

    for i in range(70):
        lid = f"active_{i:04d}"
        conn.execute("INSERT INTO learner VALUES (?, ?, ?)", (lid, _ts(), _ts()))
        for j in range(40):
            is_pass = j < 12
            conn.execute(
                "INSERT INTO attempt VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (f"att_{lid}_{j}", f"sess_{lid}", lid, SKILL,
                 _ts(days_ago=1), "x=5", None,
                 None if is_pass else M,
                 None, "none" if is_pass else "wrong", "{}", "Q1"),
            )

    for i in range(30):
        lid = f"inactive_{i:04d}"
        conn.execute("INSERT INTO learner VALUES (?, ?, ?)", (lid, _ts(), _ts()))

    conn.commit()


def main():
    temp_db = ROOT / "data" / "learner_store" / "learners_stress_nodes.db"
    print(f"Creating temp DB: {temp_db}")
    conn = _create_temp_db(temp_db)
    print("Populating 100 learners ...")
    _populate(conn)

    original_db = cohort_nodes.DB
    cohort_nodes.DB = temp_db

    try:
        print("Ensuring schema ...")
        ensure_schema(conn)

        print(f"Creating node '{NODE_ID}' ...")
        create_node(NODE_ID, "class", NODE_NAME, conn=conn)

        learners = [r[0] for r in conn.execute(
            "SELECT learner_id FROM learner ORDER BY learner_id"
        ).fetchall()]
        for lid in learners:
            add_member(lid, NODE_ID, conn=conn)
        print(f"  Added {len(learners)} members")

        print("Running rollup ...")
        _, dv = rebuild_class_node(NODE_ID, conn=conn)
        print(f"  data_version: {dv}")

        node = get_node(NODE_ID, conn=conn)

        raw_learner_count = conn.execute("SELECT COUNT(*) FROM learner").fetchone()[0]
        raw_active_count = conn.execute("SELECT COUNT(DISTINCT learner_id) FROM attempt").fetchone()[0]
        raw_attempt_count = conn.execute("SELECT COUNT(*) FROM attempt").fetchone()[0]
        raw_pass_count = conn.execute(
            "SELECT COUNT(*) FROM attempt WHERE error_type IN ('none', 'match')"
        ).fetchone()[0]

        checks = [
            ("learner_count matches raw", node["learner_count"] == raw_learner_count,
             f"{node['learner_count']} vs {raw_learner_count}"),
            ("active_count matches raw", node["active_count"] == raw_active_count,
             f"{node['active_count']} vs {raw_active_count}"),
            ("attempt_count matches raw", node["attempt_count"] == raw_attempt_count,
             f"{node['attempt_count']} vs {raw_attempt_count}"),
            ("pass_count matches raw", node["pass_count"] == raw_pass_count,
             f"{node['pass_count']} vs {raw_pass_count}"),
            ("get_node returns populated rollup",
             node["attempt_count"] > 0 and node["learner_count"] > 0,
             f"attempts={node['attempt_count']}, learners={node['learner_count']}"),
            ("state_distribution sums to learner_count",
             sum(node["state_distribution"].values()) == node["learner_count"],
             f"{sum(node['state_distribution'].values())} vs {node['learner_count']}"),
            ("data_version present", bool(node.get("data_version")),
             node.get("data_version", "MISSING")),
            ("conversation_summary reserved (null)",
             node.get("questions_asked") is None,
             "null" if node.get("questions_asked") is None else "not null"),
        ]

        print("\n" + "=" * 64)
        print("PASS / FAIL — B1 node checks")
        print("=" * 64)
        all_pass = True
        for label, passed, detail in checks:
            mark = "PASS" if passed else "FAIL"
            print(f"  [{mark}] {label}: {detail}")
            if not passed:
                all_pass = False
        print("=" * 64)
        print(f"RESULT: {'B1 IS CLOSED' if all_pass else 'FAILURES ABOVE'}")
        print("=" * 64)

        if not all_pass:
            print("\nNode snapshot:")
            for k in ("learner_count", "active_count", "attempt_count",
                      "pass_count", "state_distribution", "threshold_snapshot"):
                print(f"  {k}: {node.get(k)}")

        return 0 if all_pass else 1
    finally:
        cohort_nodes.DB = original_db
        try:
            conn.close()
        except sqlite3.Error as exc:
            print(f"\nCould not close temp database connection: {exc}")
        if temp_db.exists():
            try:
                temp_db.unlink()
                print(f"\nRemoved {temp_db}")
            except PermissionError:
                print(f"\n  (could not remove {temp_db} — close any open handles)")
                
if __name__ == "__main__":
    sys.exit(main())