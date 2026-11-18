"""migrate_to_nodes.py — one-time B1 migration.

Creates cohort_meta, cohort_node, cohort_membership tables.
Creates a 'default_class' node, adds all learners as members,
runs initial rollup.

Idempotent — safe to run multiple times.

Usage:  py scripts\\migrate_to_nodes.py
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.tutor.cohort_nodes import (
    DB, ensure_schema, create_node, add_member,
    rebuild_class_node, get_node, list_members,
)

NODE_ID = "default_class"
NODE_NAME = "Default Class"


def main():
    if not DB.exists():
        print(f"ERROR: {DB} not found")
        return 1

    print(f"DB: {DB}")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    try:
        print("Ensuring schema ...")
        ensure_schema(conn)

        print(f"Creating node '{NODE_ID}' (level=class) ...")
        created = create_node(NODE_ID, "class", NODE_NAME, conn=conn)
        print(f"  {'created' if created else 'already existed'}")

        learners = [r[0] for r in conn.execute(
            "SELECT learner_id FROM learner ORDER BY learner_id"
        ).fetchall()]
        if not learners:
            learners = [r[0] for r in conn.execute(
                "SELECT DISTINCT learner_id FROM attempt ORDER BY learner_id"
            ).fetchall()]
            if learners:
                print(f"  (learner table empty, using {len(learners)} from attempt)")

        print(f"Adding {len(learners)} learners to '{NODE_ID}' ...")
        added = 0
        for lid in learners:
            if add_member(lid, NODE_ID, conn=conn):
                added += 1
        print(f"  {added} new, {len(learners) - added} already members")

        print("Running initial rollup ...")
        node_id, dv = rebuild_class_node(NODE_ID, conn=conn)
        print(f"  {node_id} @ {dv}")

        node = get_node(NODE_ID, conn=conn)
        print("\nNode snapshot:")
        for k in ("node_id", "data_version", "learner_count", "active_count",
                  "attempt_count", "pass_count", "computed_from"):
            print(f"  {k}: {node.get(k)}")
        print(f"  state_distribution: {node.get('state_distribution')}")
        print(f"  threshold_snapshot: {node.get('threshold_snapshot')}")
        print(f"  misconception_freq ({len(node.get('misconception_freq', {}))} misconceptions)")

        members = list_members(NODE_ID, conn)
        print(f"\nMembers ({len(members)}): {members}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
