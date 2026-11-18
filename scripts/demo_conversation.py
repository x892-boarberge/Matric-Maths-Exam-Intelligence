"""demo_conversation.py — end-to-end B5a demo with LLM hook.

Shows rules-only capture, then LLM-escalation capture.

Usage:  py scripts\\demo_conversation.py
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.tutor.conversation import (
    capture_question, link_next_attempt, conversation_stats,
)

DB_PATH = ROOT / "data" / "learner_store" / "learners.db"
TEST_LEARNER = "demo_conv_learner"
TEST_SESSION = "demo_conv_session"


class _Store:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row


def fake_llm(text):
    """Simulated LLM classifier: overrides messy inputs."""
    t = text.lower()
    if "even matter" in t or "bruh" in t:
        return {"intent": "frustration", "confidence": 0.9,
                "answer_hint": "You've got this. Let's break it into steps."}
    if "what even" in t:
        return {"intent": "frustration", "confidence": 0.85,
                "answer_hint": "Take a breath. What part feels unclear?"}
    return None


def main():
    store = _Store()
    try:
        try:
            store.conn.execute(
                "INSERT OR IGNORE INTO learner (learner_id, created_at, last_seen) "
                "VALUES (?, datetime('now'), datetime('now'))",
                (TEST_LEARNER,),
            )
            store.conn.commit()
        except sqlite3.OperationalError:
            pass

        from src.tutor.cohort_nodes import add_member
        try:
            add_member(TEST_LEARNER, "default_class", conn=store.conn)
        except Exception:
            pass

        store.conn.execute(
            "DELETE FROM learner_events WHERE learner_id = ?", (TEST_LEARNER,)
        )
        store.conn.commit()

        print("Demo: conversation capture (B5a with LLM hook)")
        print("=" * 60)

        samples = [
            ("why does the sign flip?", "2025_P1_Q1.1.1", None),
            ("I don't understand this", "2025_P1_Q1.1.1", None),
            ("bruh why does this even matter", "2025_P1_Q1.1.1", fake_llm),
            ("hmm what even", "2025_P1_Q1.1.1", fake_llm),
            ("can you solve Q3 for me", "2025_P1_Q1.1.1", None),
        ]

        print("\nCapture 5 questions (some with LLM escalation):")
        for i, (text, qid, llm) in enumerate(samples, 1):
            r = capture_question(
                store, TEST_LEARNER, TEST_SESSION,
                skill_id="algebra.quadratic.solve",
                question_id=qid,
                question_text=text,
                llm_classify=llm,
            )
            llm_tag = " [LLM]" if r["classifier_source"] == "llm" else " [rule]"
            print(f"  {i}. intent={r['intent']:<18} "
                  f"rule_was={r['rule_intent']:<18}{llm_tag}  '{text[:35]}'")

        print("\nStats:")
        stats = conversation_stats("default_class", days=1)
        print(f"  total:               {stats['total']}")
        print(f"  by_intent:           {stats['by_intent']}")
        print(f"  by_source:           {stats['by_source']}")
        print(f"  rule_llm_agreement:  {stats['rule_llm_agreement']}")
        print(f"  deferred_count:      {stats['deferred_count']}")
        print(f"  top_lanes:")
        for lane, count in stats["top_lanes"]:
            print(f"    {count:>3}  {lane}")

        # Cleanup
        store.conn.execute(
            "DELETE FROM learner_events WHERE learner_id = ?", (TEST_LEARNER,)
        )
        store.conn.execute(
            "UPDATE cohort_membership SET left_at = datetime('now') "
            "WHERE learner_id = ? AND node_id = 'default_class' AND left_at IS NULL",
            (TEST_LEARNER,),
        )
        store.conn.commit()
        print("\nDemo complete. Cleaned up.")
        return 0
    finally:
        store.conn.close()


if __name__ == "__main__":
    sys.exit(main())
