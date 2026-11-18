"""migrate_hierarchy.py — create the parent chain above 'default_class'.

B2 migration: adds school / district / province / national nodes.
Idempotent — safe to run multiple times.

Usage:  py scripts\\migrate_hierarchy.py
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.tutor.cohort_nodes import (
    DB, ensure_schema, create_node, get_node, rebuild_cascade,
)


HIERARCHY = [
    # (node_id, level, name, parent_id)
    ("national", "national", "South Africa", None),
    ("default_province", "province", "Default Province", "national"),
    ("default_district", "district", "Default District", "default_province"),
    ("default_school", "school", "Default School", "default_district"),
    ("default_class", "class", "Default Class", "default_school"),
]


def main():
    if not DB.exists():
        print(f"ERROR: {DB} not found")
        return 1

    print(f"DB: {DB}")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    try:
        ensure_schema(conn)

        # Create nodes top-down
        for node_id, level, name, parent_id in HIERARCHY:
            created = create_node(node_id, level, name, parent_id, conn=conn)
            print(f"  {'created' if created else 'exists  '} {level:<10} {node_id}")

        # If default_class already exists with parent_id=None, update it
        conn.execute(
            "UPDATE cohort_meta SET parent_id = 'default_school' "
            "WHERE node_id = 'default_class' AND parent_id IS NULL"
        )
        conn.commit()

        # Cascade rebuild from the leaf up
        print("\nCascade rebuild from default_class ...")
        results = rebuild_cascade("default_class", conn=conn)
        for node_id, dv in results:
            node = get_node(node_id, conn=conn)
            print(f"  {node_id:<20} @ {dv}  learners={node['learner_count']}  "
                  f"attempts={node['attempt_count']}")

        # Verify consistency: parent's learner_count >= child's learner_count
        print("\nConsistency check:")
        for i in range(len(HIERARCHY) - 1):
            child_id = HIERARCHY[i + 1][0] if i + 1 < len(HIERARCHY) else None
            # Compare each adjacent pair
        pairs = [
            ("default_class", "default_school"),
            ("default_school", "default_district"),
            ("default_district", "default_province"),
            ("default_province", "national"),
        ]
        for child, parent in pairs:
            c = get_node(child, conn=conn)
            p = get_node(parent, conn=conn)
            ok = p["learner_count"] >= c["learner_count"]
            mark = "PASS" if ok else "FAIL"
            print(f"  [{mark}] {parent:<20} ({p['learner_count']}) >= "
                  f"{child:<20} ({c['learner_count']})")

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())