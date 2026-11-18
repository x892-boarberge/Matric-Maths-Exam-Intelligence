"""cleanup_garbage_learners.py — soft-delete invalid learner IDs.

Correct rule: a single-character ID is garbage ONLY IF it has 0 attempts.
If it has attempts, it's a real learner (someone entered a 1-char name).

Invalid criteria:
  - empty / whitespace
  - >40 chars (pasted path)
  - path characters
  - single char AND 0 attempts

Usage:  py scripts\\cleanup_garbage_learners.py
"""
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB = ROOT / "data" / "learner_store" / "learners.db"
NODE_ID = "default_class"


def is_garbage(lid, conn=None):
    """Return (is_garbage, reason). Requires conn for attempt check."""
    if not lid or not lid.strip():
        return True, "empty"
    if len(lid) > 40:
        return True, "too long (likely pasted path)"
    if any(c in lid for c in '\\/:*?"<>|'):
        return True, "path characters"
    if len(lid) <= 1:
        # Only garbage if no attempts — a real learner might be named '1'
        if conn is not None:
            n = conn.execute(
                "SELECT COUNT(*) FROM attempt WHERE learner_id = ?", (lid,)
            ).fetchone()[0]
            if n > 0:
                return False, f"single char but has {n} attempts (real)"
        return True, "single char with 0 attempts"
    return False, ""


def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        members = conn.execute(
            "SELECT learner_id FROM cohort_membership "
            "WHERE node_id = ? AND left_at IS NULL ORDER BY learner_id",
            (NODE_ID,),
        ).fetchall()

        garbage = []
        clean = []
        for r in members:
            lid = r["learner_id"]
            bad, reason = is_garbage(lid, conn)
            if bad:
                garbage.append((lid, reason))
            else:
                clean.append(lid)

        print(f"Active members: {len(members)} | Clean: {len(clean)} | Garbage: {len(garbage)}")

        if not garbage:
            print("Nothing to clean.")
            return 0

        now = datetime.now(timezone.utc).isoformat()
        for lid, reason in garbage:
            n = conn.execute(
                "SELECT COUNT(*) FROM attempt WHERE learner_id = ?", (lid,)
            ).fetchone()[0]
            print(f"  marking left_at: {lid!r}  ({reason})  attempts={n}")
            conn.execute(
                "UPDATE cohort_membership SET left_at = ? "
                "WHERE learner_id = ? AND node_id = ? AND left_at IS NULL",
                (now, lid, NODE_ID),
            )
        conn.commit()

        sys.path.insert(0, str(ROOT))
        from src.tutor.cohort_nodes import rebuild_class_node
        _, dv = rebuild_class_node(NODE_ID, conn=conn)
        print(f"\nRebuilt {NODE_ID} @ {dv}")
        remaining = conn.execute(
            "SELECT COUNT(*) FROM cohort_membership WHERE node_id = ? AND left_at IS NULL",
            (NODE_ID,),
        ).fetchone()[0]
        print(f"Active members now: {remaining}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())