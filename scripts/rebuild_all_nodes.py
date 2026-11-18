"""rebuild_all_nodes.py — scheduled rebuild of the cohort node tree.

Rebuilds bottom-up (class -> school -> district -> province -> national),
so each node is rebuilt exactly once. No cascades, no duplicates.

Usage:
  py scripts\\rebuild_all_nodes.py
  py scripts\\rebuild_all_nodes.py --dry-run
  py scripts\\rebuild_all_nodes.py --days 30
"""
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.tutor.cohort_nodes import (
    DB, ensure_schema, rebuild_node, get_node,
)

LEVEL_ORDER = ["class", "school", "district", "province", "national"]


def main():
    dry_run = "--dry-run" in sys.argv
    days = 30
    if "--days" in sys.argv:
        try:
            days = int(sys.argv[sys.argv.index("--days") + 1])
        except (ValueError, IndexError):
            pass

    if not DB.exists():
        print(f"ERROR: {DB} not found")
        return 1

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    try:
        ensure_schema(conn)

        # Load all nodes grouped by level
        by_level = {lvl: [] for lvl in LEVEL_ORDER}
        for r in conn.execute(
            "SELECT node_id, level FROM cohort_meta ORDER BY level, node_id"
        ).fetchall():
            if r["level"] in by_level:
                by_level[r["level"]].append(r["node_id"])

        total = sum(len(v) for v in by_level.values())
        if total == 0:
            print("No nodes found. Run migrate_hierarchy.py first.")
            return 1

        print(f"Rebuild plan (days={days}, dry_run={dry_run}):")
        for lvl in LEVEL_ORDER:
            n = len(by_level[lvl])
            if n:
                print(f"  {lvl:<10} {n} node(s)")

        if dry_run:
            print("\n--dry-run: no changes.")
            return 0

        print(f"\nRebuilding {total} nodes bottom-up ...")
        t0 = time.time()
        results = []
        failures = []

        for lvl in LEVEL_ORDER:
            for node_id in by_level[lvl]:
                try:
                    nid, dv = rebuild_node(node_id, conn=conn, days=days)
                    node = get_node(nid, conn=conn)
                    results.append((lvl, node_id, dv, node["learner_count"],
                                    node["attempt_count"]))
                    print(f"  {lvl:<10} {node_id:<22} @ {dv}  "
                          f"L={node['learner_count']:<5} A={node['attempt_count']}")
                except Exception as e:
                    failures.append((node_id, str(e)))
                    print(f"  FAILED     {node_id:<22} {e}")

        elapsed = time.time() - t0
        print(f"\nDone in {elapsed:.2f}s")
        print(f"  Rebuilt:  {len(results)}")
        print(f"  Failed:   {len(failures)}")

        if failures:
            print("\nFailures:")
            for nid, err in failures:
                print(f"  {nid}: {err}")
            return 1

        # Sanity: root rollup >= leaf rollup
        if "national" in by_level and by_level["national"]:
            root = get_node(by_level["national"][0], conn=conn)
            leaves = [r for r in results if r[0] == "class"]
            leaf_total = sum(r[3] for r in leaves)
            print(f"\nConsistency:")
            print(f"  national learner_count: {root['learner_count']}")
            print(f"  sum of class learners:  {leaf_total}")
            if root["learner_count"] != leaf_total:
                print(f"  [WARN] mismatch — check hierarchy topology")
            else:
                print(f"  [PASS]")

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
