import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB = ROOT / "data" / "learner_store" / "learners.db"
NODE_ID = "default_class"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
try:
    # Restore any learner that has attempts but was incorrectly soft-deleted
    rows = conn.execute(
        "SELECT cm.learner_id, COUNT(a.attempt_id) AS n "
        "FROM cohort_membership cm "
        "LEFT JOIN attempt a ON a.learner_id = cm.learner_id "
        "WHERE cm.node_id = ? AND cm.left_at IS NOT NULL "
        "GROUP BY cm.learner_id HAVING n > 0",
        (NODE_ID,),
    ).fetchall()
    if not rows:
        print("No learners to restore.")
    else:
        for r in rows:
            print(f"Restoring {r['learner_id']!r} (attempts={r['n']})")
            conn.execute(
                "UPDATE cohort_membership SET left_at = NULL "
                "WHERE learner_id = ? AND node_id = ? AND left_at IS NOT NULL",
                (r["learner_id"], NODE_ID),
            )
        conn.commit()
    sys.path.insert(0, str(ROOT))
    from src.tutor.cohort_nodes import rebuild_class_node
    _, dv = rebuild_class_node(NODE_ID, conn=conn)
    print(f"Rebuilt {NODE_ID} @ {dv}")
    remaining = conn.execute(
        "SELECT COUNT(*) FROM cohort_membership WHERE node_id = ? AND left_at IS NULL",
        (NODE_ID,),
    ).fetchone()[0]
    print(f"Active members now: {remaining}")
finally:
    conn.close()
