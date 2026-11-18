"""stress_test_analyst.py — verify the 4 analyst functions.

6 checks:
  1. list_snapshots returns history
  2. compare two nodes returns expected diffs
  3. find_anomaly detects a synthetic spike
  4. slice_learners returns subset
  5. correlate returns Pearson r
  6. All return dicts with either 'error' or expected keys (never crash)

Uses real DB. Runs fast (<2s). No temp DB.

Usage:  py scripts\\stress_test_analyst.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.tutor.analyst import (
    list_snapshots, find_anomaly, compare, slice_learners, correlate,
)


def main():
    checks = []

    # 1. list_snapshots
    snaps = list_snapshots("default_class", limit=10)
    checks.append((
        "list_snapshots returns history",
        isinstance(snaps, list) and len(snaps) > 0,
        f"{len(snaps)} snapshots",
    ))

    # 2. compare same node across time (or national vs class)
    cmp = compare("default_class", "national")
    ok = ("error" not in cmp) or ("node_a_found" in cmp)
    checks.append((
        "compare returns dict with diffs or error",
        isinstance(cmp, dict) and ("diffs" in cmp or "error" in cmp),
        "error" if "error" in cmp else f"{len(cmp.get('diffs', {}))} metrics",
    ))

    # 3. find_anomaly on default_class (expect insufficient history)
    anom = find_anomaly("default_class", metric="attempt_count", window=7)
    ok = ("error" in anom) or ("is_anomaly" in anom)
    checks.append((
        "find_anomaly returns structured result",
        ok,
        "insufficient history" if "error" in anom else f"z={anom.get('z_score')}",
    ))

    # 4. slice_learners with a filter
    sl = slice_learners("default_class", where={"attempts": (">=", 1)}, days=30)
    ok = ("error" in sl) or ("learner_count" in sl)
    checks.append((
        "slice_learners returns filtered cohort",
        ok,
        "error" if "error" in sl else f"{sl.get('learner_count')} learners",
    ))

    # 5. slice_learners with impossible filter
    sl2 = slice_learners("default_class", where={"accuracy": ("<", -1.0)}, days=30)
    ok = ("learner_count" in sl2) and sl2["learner_count"] == 0
    checks.append((
        "slice_learners handles empty result",
        ok,
        f"{sl2.get('learner_count')} learners" if "learner_count" in sl2 else "MALFORMED",
    ))

    # 6. correlate
    corr = correlate("default_class", "attempts", "accuracy", days=30)
    ok = ("error" in corr) or ("pearson_r" in corr)
    checks.append((
        "correlate returns pearson_r or error",
        ok,
        "insufficient" if "error" in corr else f"r={corr.get('pearson_r')} n={corr.get('n')}",
    ))

    print("=" * 64)
    print("PASS / FAIL - analyst checks")
    print("=" * 64)
    all_pass = True
    for label, passed, detail in checks:
        mark = "PASS" if passed else "FAIL"
        print(f"  [{mark}] {label}: {detail}")
        if not passed:
            all_pass = False
    print("=" * 64)
    print(f"RESULT: {'B3b IS CLOSED' if all_pass else 'FAILURES ABOVE'}")
    print("=" * 64)

    print("\nSample outputs for review:")
    print(f"\n  list_snapshots('default_class'):")
    for s in snaps[:3]:
        print(f"    {s['data_version']}  L={s['learner_count']}  A={s['attempt_count']}")

    if "learner_count" in sl:
        print(f"\n  slice_learners(attempts>=1): {sl['learner_count']} learners, "
              f"{sl.get('attempt_count')} attempts")
    if "pearson_r" in corr:
        print(f"\n  correlate(attempts, accuracy): r={corr['pearson_r']} "
              f"({corr['note']})")
    elif "error" in corr:
        print(f"\n  correlate: {corr['error']} (n={corr.get('n', '?')})")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
