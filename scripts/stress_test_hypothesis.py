"""stress_test_hypothesis.py — verify B4 (hypothesis ledger + warnings).

10 checks. Uses real DB, cleans up its own test data after.

Usage:  py scripts\\stress_test_hypothesis.py
"""
import sys
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.tutor.hypothesis import (
    propose, get, mark_pending, record_outcome,
    list_open, list_resolved, history_for_node, summary,
    DB as HYP_DB,
)
from src.tutor.analyst import correlate


TEST_TAG = "stress_test"


def cleanup():
    conn = sqlite3.connect(HYP_DB)
    try:
        try:
            conn.execute("DELETE FROM hypothesis WHERE created_by = ?", (TEST_TAG,))
            conn.commit()
        except sqlite3.OperationalError:
            pass  # table doesn't exist yet; nothing to clean
    finally:
        conn.close()


def main():
    cleanup()
    checks = []

    h1 = propose(
        question="Are learners with high quit rates also low accuracy?",
        finding={"test": "proposal_test"},
        scope_node="default_class",
        confidence=0.6,
        proposed_action="schedule confidence drill",
        predicted_outcome="quits drop by >=2 in next session",
        created_by=TEST_TAG,
    )
    checks.append((
        "propose creates row with status proposed",
        h1 is not None and h1["status"] == "proposed",
        f"status={h1.get('status') if h1 else 'None'}",
    ))

    h1b = get(h1["hypothesis_id"])
    checks.append((
        "get retrieves same hypothesis",
        h1b is not None and h1b["hypothesis_id"] == h1["hypothesis_id"],
        "ok" if h1b else "not found",
    ))

    h1c = mark_pending(h1["hypothesis_id"])
    checks.append((
        "mark_pending transitions to pending_measurement",
        h1c["status"] == "pending_measurement",
        f"status={h1c['status']}",
    ))

    h1d = record_outcome(h1["hypothesis_id"], correct=True, notes="drill worked")
    checks.append((
        "record_outcome(True) -> confirmed",
        h1d["status"] == "confirmed" and h1d["outcome_correct"] == 1,
        f"status={h1d['status']}, correct={h1d['outcome_correct']}",
    ))

    h2 = propose(
        question="Will a new playbook fix quadratic inequalities?",
        finding={"test": "refute_test"},
        scope_node="default_class",
        created_by=TEST_TAG,
    )
    h2b = record_outcome(h2["hypothesis_id"], correct=False, notes="still failing")
    checks.append((
        "record_outcome(False) -> refuted",
        h2b["status"] == "refuted" and h2b["outcome_correct"] == 0,
        f"status={h2b['status']}, correct={h2b['outcome_correct']}",
    ))

    h3 = propose(
        question="Open hypothesis for list_open test?",
        finding={},
        created_by=TEST_TAG,
    )
    opens = list_open()
    test_opens = [h for h in opens if h["created_by"] == TEST_TAG]
    checks.append((
        "list_open returns proposed/pending only",
        len(test_opens) == 1 and test_opens[0]["hypothesis_id"] == h3["hypothesis_id"],
        f"{len(test_opens)} open hypotheses",
    ))

    resolved = list_resolved()
    test_resolved = [h for h in resolved if h["created_by"] == TEST_TAG]
    checks.append((
        "list_resolved returns confirmed/refuted",
        len(test_resolved) == 2,
        f"{len(test_resolved)} resolved",
    ))

    s = summary()
    checks.append((
        "summary reflects confirmed/refuted counts",
        s["total"] >= 3 and s["by_status"].get("confirmed", 0) >= 1,
        f"total={s['total']}, confirmed={s['by_status'].get('confirmed', 0)}",
    ))

    hist = history_for_node("default_class")
    test_hist = [h for h in hist if h["created_by"] == TEST_TAG]
    checks.append((
        "history_for_node filters by scope_node",
        len(test_hist) >= 2,
        f"{len(test_hist)} test hypotheses for default_class",
    ))

    corr = correlate("default_class", "attempts", "accuracy")
    has_warning = "warnings" in corr and len(corr["warnings"]) > 0
    checks.append((
        "correlate() emits warnings on structural artifact",
        has_warning,
        f"{len(corr.get('warnings', []))} warnings" if has_warning else "NO WARNINGS",
    ))

    print("=" * 64)
    print("PASS / FAIL - B4 hypothesis checks")
    print("=" * 64)
    all_pass = True
    for label, passed, detail in checks:
        mark = "PASS" if passed else "FAIL"
        print(f"  [{mark}] {label}: {detail}")
        if not passed:
            all_pass = False
    print("=" * 64)
    print(f"RESULT: {'B4 IS CLOSED' if all_pass else 'FAILURES ABOVE'}")
    print("=" * 64)

    if corr.get("warnings"):
        print("\nCorrelate warnings (proof of spurious guard):")
        for w in corr["warnings"]:
            print(f"  - {w}")

    cleanup()
    print(f"\nCleaned up hypotheses with created_by='{TEST_TAG}'")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
