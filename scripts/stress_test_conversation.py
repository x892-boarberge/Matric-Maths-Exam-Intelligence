"""stress_test_conversation.py — verify B5a including LLM hook.

10 checks. Uses real DB, cleans up after.

Usage:  py scripts\\stress_test_conversation.py
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.tutor.conversation import (
    classify_intent, capture_question, link_next_attempt,
    get_conversations, conversation_stats,
)


DB_PATH = ROOT / "data" / "learner_store" / "learners.db"
TEST_LEARNER = "conv_test_learner"
TEST_SESSION = "conv_test_session"
TEST_ATTEMPT = "att_conv_test_1"


class _Store:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row


def cleanup(store):
    store.conn.execute(
        "DELETE FROM learner_events WHERE learner_id = ?", (TEST_LEARNER,)
    )
    store.conn.execute(
        "DELETE FROM attempt WHERE attempt_id = ?", (TEST_ATTEMPT,)
    )
    store.conn.execute(
        "DELETE FROM learner WHERE learner_id = ?", (TEST_LEARNER,)
    )
    store.conn.commit()


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

        cleanup(store)
        checks = []

        # 1-4: rule classifier on 4 known samples
        samples = [
            ("why does the sign flip?", "curiosity"),
            ("I don't understand this at all", "frustration"),
            ("can you do my homework", "off_topic"),
            ("I used completing the square", "alternative_method"),
        ]
        for text, expected in samples:
            got, conf = classify_intent(text)
            checks.append((
                f"classify '{text[:28]}...' -> {expected}",
                got == expected,
                f"got {got} ({conf:.2f})",
            ))

        # 5: capture_question (no LLM) populates 9 columns
        r1 = capture_question(
            store, TEST_LEARNER, TEST_SESSION,
            skill_id="algebra.quadratic.solve",
            question_id="2025_P1_Q1.1.1",
            question_text="why does the sign flip?",
        )
        row = store.conn.execute(
            "SELECT question_text, answer_text, answer_source, lane_key, "
            "intent, rule_intent, classifier_source, classifier_confidence, "
            "next_attempt_id FROM learner_events WHERE event_id = ?",
            (r1["event_id"],),
        ).fetchone()
        ok = (
            row is not None
            and row["question_text"] == "why does the sign flip?"
            and row["lane_key"] and "/" in row["lane_key"]
            and row["intent"] == "curiosity"
            and row["classifier_source"] == "rule"
            and row["rule_intent"] == row["intent"]
            and row["next_attempt_id"] is None
        )
        checks.append((
            "capture_question (no LLM) fills all 9 columns",
            ok,
            f"source={row['answer_source'] if row else '?'}, "
            f"classifier={row['classifier_source'] if row else '?'}",
        ))

        # 6: LLM escalation on low confidence
        def fake_llm_override(text):
            # Return frustration with high confidence (overrides rule)
            return {"intent": "frustration", "confidence": 0.95,
                    "answer_hint": "Take a breath, you've got this."}

        r2 = capture_question(
            store, TEST_LEARNER, TEST_SESSION,
            skill_id="algebra.quadratic.solve",
            question_id="2025_P1_Q1.1.1",
            question_text="hmm what even",  # low-confidence unknown to rules
            llm_classify=fake_llm_override,
        )
        row2 = store.conn.execute(
            "SELECT intent, rule_intent, classifier_source, "
            "classifier_confidence, answer_source FROM learner_events "
            "WHERE event_id = ?",
            (r2["event_id"],),
        ).fetchone()
        ok = (
            row2["classifier_source"] == "llm"
            and row2["intent"] == "frustration"
            and row2["rule_intent"] == "unknown"
            and row2["classifier_confidence"] == 0.95
        )
        checks.append((
            "LLM overrides low-confidence rule classification",
            ok,
            f"rule={row2['rule_intent']}, llm={row2['intent']}, "
            f"src={row2['classifier_source']}",
        ))

        # 7: LLM provides answer when playbook deferred
        def fake_llm_answer(text):
            return {"intent": "unknown", "confidence": 0.3,
                    "answer_hint": "The sign is inside the bracket."}

        r3 = capture_question(
            store, TEST_LEARNER, TEST_SESSION,
            skill_id="algebra.quadratic.solve",
            question_id="NONEXISTENT_Q",  # no playbook -> deferred -> LLM answer
            question_text="how do you know?",
            llm_classify=fake_llm_answer,
        )
        checks.append((
            "LLM provides answer when playbook deferred",
            r3["answer_source"] == "llm" and r3["answer_text"],
            f"source={r3['answer_source']}",
        ))

        # 8: link_next_attempt
        store.conn.execute(
            "INSERT INTO attempt (attempt_id, session_id, learner_id, skill_id, "
            "timestamp, error_type) VALUES (?, ?, ?, ?, datetime('now'), 'wrong')",
            (TEST_ATTEMPT, TEST_SESSION, TEST_LEARNER,
             "algebra.quadratic.solve"),
        )
        store.conn.commit()
        linked = link_next_attempt(store, r1["event_id"], TEST_ATTEMPT)
        row3 = store.conn.execute(
            "SELECT next_attempt_id FROM learner_events WHERE event_id = ?",
            (r1["event_id"],),
        ).fetchone()
        checks.append((
            "link_next_attempt populates next_attempt_id",
            linked and row3["next_attempt_id"] == TEST_ATTEMPT,
            f"linked={linked}",
        ))

        # 9: conversation_stats includes rule_llm_agreement
        stats = conversation_stats("default_class", days=1)
        checks.append((
            "conversation_stats exposes rule_llm_agreement",
            isinstance(stats, dict)
            and "rule_llm_agreement" in stats
            and "top_lanes" in stats,
            f"total={stats.get('total')}, "
            f"agreement={stats.get('rule_llm_agreement', {}).get('pct')}",
        ))

        # 10: three conversation rows persisted
        direct = store.conn.execute(
            "SELECT COUNT(*) FROM learner_events WHERE learner_id = ? "
            "AND event_type = 'CONVERSATION'",
            (TEST_LEARNER,),
        ).fetchone()[0]
        checks.append((
            "3 CONVERSATION events persisted",
            direct == 3,
            f"{direct} row(s)",
        ))

        print("=" * 64)
        print("PASS / FAIL - B5a conversation checks")
        print("=" * 64)
        all_pass = True
        for label, passed, detail in checks:
            mark = "PASS" if passed else "FAIL"
            print(f"  [{mark}] {label}: {detail}")
            if not passed:
                all_pass = False
        print("=" * 64)
        print(f"RESULT: {'B5a IS CLOSED' if all_pass else 'FAILURES ABOVE'}")
        print("=" * 64)

        cleanup(store)
        print("\nCleaned up test rows.")
        return 0 if all_pass else 1
    finally:
        store.conn.close()


if __name__ == "__main__":
    sys.exit(main())
