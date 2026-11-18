"""demo_hypothesis.py — end-to-end demo of hypothesis ledger.

Propose -> get -> mark_pending -> record_outcome -> list -> summary
Leaves 1 hypothesis in DB (created_by='demo').

Usage:  py scripts\\demo_hypothesis.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.tutor.hypothesis import (
    propose, get, mark_pending, record_outcome,
    list_open, list_resolved, summary,
)


def main():
    print("Demo: hypothesis ledger end-to-end")
    print("=" * 60)

    print("\n1. Propose a hypothesis:")
    question = "Does the sign-flip drill reduce errors within 3 sessions?"
    print(f'   question: "{question}"')
    h = propose(
        question=question,
        finding={"source": "demo", "metric": "M_SIGN_ERROR_READING_ROOT"},
        scope_node="default_class",
        confidence=0.7,
        proposed_action="schedule 3 drill sessions on sign-flip",
        predicted_outcome="sign-flip errors drop by >=50% over 3 sessions",
        created_by="demo",
    )
    print(f"   hypothesis_id: {h['hypothesis_id']}")
    print(f"   status:        {h['status']}")
    print(f"   confidence:    {h['confidence']}")

    print("\n2. Retrieve by ID:")
    h2 = get(h["hypothesis_id"])
    print(f"   retrieved status: {h2['status']}")

    print("\n3. Mark pending (action taken):")
    h3 = mark_pending(h["hypothesis_id"])
    print(f"   status: {h3['status']}")

    print("\n4. Record outcome (prediction held):")
    h4 = record_outcome(
        h["hypothesis_id"],
        correct=True,
        notes="sign-flip errors dropped from 22 to 8 over 3 sessions",
    )
    print(f"   status:          {h4['status']}")
    print(f"   outcome_correct: {h4['outcome_correct']}")
    print(f"   resolved_at:     {h4['resolved_at']}")

    print("\n5. list_open():")
    opens = list_open()
    print(f"   {len(opens)} open hypotheses")

    print("\n6. list_resolved():")
    resolved = list_resolved()
    print(f"   {len(resolved)} resolved hypotheses")
    for r in resolved[:3]:
        mark = "confirmed" if r["status"] == "confirmed" else "refuted"
        print(f"     [{mark}] {r['question'][:60]}")

    print("\n7. summary():")
    s = summary()
    print(f"   {s}")

    print("\n" + "=" * 60)
    print("Demo complete. 1 hypothesis left in DB (created_by='demo').")
    return 0


if __name__ == "__main__":
    sys.exit(main())
