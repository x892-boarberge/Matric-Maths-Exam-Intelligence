"""migrate_conversation.py — extend learner_events for Q&A capture.

Adds 9 columns: question_text, answer_text, answer_source, lane_key,
intent, rule_intent, classifier_source, classifier_confidence, next_attempt_id.

Idempotent — safe to run multiple times.

Usage:  py scripts\\migrate_conversation.py
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB = ROOT / "data" / "learner_store" / "learners.db"

NEW_COLUMNS = [
    ("question_text",         "TEXT"),
    ("answer_text",           "TEXT"),
    ("answer_source",         "TEXT"),
    ("lane_key",              "TEXT"),
    ("intent",                "TEXT"),
    ("rule_intent",           "TEXT"),
    ("classifier_source",     "TEXT"),
    ("classifier_confidence", "REAL"),
    ("next_attempt_id",       "TEXT"),
]


def table_exists(conn, name):
    return conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (name,)
    ).fetchone() is not None


def column_exists(conn, table, column):
    return any(
        r[1] == column
        for r in conn.execute(f"PRAGMA table_info({table})").fetchall()
    )


def main():
    if not DB.exists():
        print(f"ERROR: {DB} not found")
        return 1

    conn = sqlite3.connect(DB)
    try:
        if not table_exists(conn, "learner_events"):
            print("ERROR: learner_events table not found. Run CLI once first.")
            return 1

        added = 0
        skipped = 0
        for col, typ in NEW_COLUMNS:
            if column_exists(conn, "learner_events", col):
                skipped += 1
                print(f"  exists   {col}")
            else:
                conn.execute(f"ALTER TABLE learner_events ADD COLUMN {col} {typ}")
                added += 1
                print(f"  added    {col} {typ}")

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_intent "
            "ON learner_events(intent, timestamp)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_rule_intent "
            "ON learner_events(rule_intent, timestamp)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_lane "
            "ON learner_events(lane_key, timestamp)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_next_attempt "
            "ON learner_events(next_attempt_id)"
        )
        conn.commit()

        print(f"\nDone: {added} added, {skipped} already existed")
        print("Indexes: idx_events_intent, idx_events_rule_intent, "
              "idx_events_lane, idx_events_next_attempt")

        print("\nlearner_events columns:")
        for r in conn.execute("PRAGMA table_info(learner_events)").fetchall():
            print(f"  {r[1]:<24} {r[2]}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
