"""conversation.py — capture Q&A between learner and Tanaka.

Pipeline (rules-first, LLM-fallback):
  learner types '?<question>'
    -> classify_intent (rules)            confidence?
         >= 0.7 -> use rule intent
         <  0.7 -> escalate to llm_classify (if provided)
    -> match_playbook_answer(intent)      answer_source='playbook' or 'deferred'
         deferred + llm_classify -> try llm answer_hint, source='llm'
    -> store event, link next attempt

answer_source values:
  playbook  - from a playbook's fatal_error / fast_path / demonstration
  deferred  - no answer given yet (queued for later review or LLM)
  llm       - from an llm_classify callable
  rule      - from a deterministic rule (future)
  learned   - from a proven binding (future flywheel)
  fallback  - generic fallback (future)

classifier_source values:
  rule  - rule classifier decided intent
  llm   - LLM classifier decided intent (override)

Cost: O(1) per capture, O(1) per link.
"""
import json
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path


def _find_root():
    r = Path(".").resolve()
    for c in [r, *r.parents]:
        if (c / "src" / "tutor").is_dir():
            return c
    return r


ROOT = _find_root()
PLAYBOOKS_DIR = ROOT / "data" / "processed" / "tutor" / "playbooks"
DB_PATH = ROOT / "data" / "learner_store" / "learners.db"


QUESTION_WORDS = ("why", "how", "what", "when", "where", "which", "who")
FRUSTRATION_WORDS = (
    "don't get", "dont get", "don't understand", "dont understand",
    "confused", "hate", "stupid", "give up", "frustrated",
    "i can't", "i cant", "help me", "stuck", "too hard",
    "this is impossible", "impossible", "bruh", "can't do",
)
HOMEWORK_WORDS = (
    "do my", "solve it for", "just give me", "answer for me",
    "write the answer", "do it for me", "solve for me",
)
INSIGHT_WORDS = (
    "i see", "i notice", "i realize", "i realised", "i figured",
    "i get it now", "ah i", "i understand now", "now i see",
)
ALTERNATIVE_WORDS = (
    "i tried", "i used", "i did it", "i solved", "i worked it",
    "by completing", "by factoring",
)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def classify_intent(text):
    """Rule-based intent classifier. Returns (intent, confidence).

    Intents: curiosity, frustration, off_topic, insight, alternative_method,
             question_about_work, unknown
    """
    if not text or not text.strip():
        return "unknown", 0.0
    t = text.strip().lower()
    if t.startswith("?"):
        t = t[1:].strip()
    elif t.startswith("/ask"):
        t = t[4:].strip()

    if any(w in t for w in HOMEWORK_WORDS):
        return "off_topic", 0.9
    if any(w in t for w in FRUSTRATION_WORDS):
        return "frustration", 0.85
    if any(w in t for w in INSIGHT_WORDS):
        return "insight", 0.8
    if any(w in t for w in ALTERNATIVE_WORDS):
        return "alternative_method", 0.75
    first_word = t.split()[0] if t.split() else ""
    if first_word in QUESTION_WORDS:
        return "curiosity", 0.85
    if t.endswith("?"):
        return "curiosity", 0.7
    return "unknown", 0.3


def _load_playbook(question_id):
    if not question_id or not PLAYBOOKS_DIR.exists():
        return None
    p = PLAYBOOKS_DIR / f"{question_id}.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    parts = question_id.split(".")
    while len(parts) > 1:
        parts.pop()
        p = PLAYBOOKS_DIR / f"{'.'.join(parts)}.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return None
    return None


def match_playbook_answer(question_id, intent):
    """Return (answer_text, answer_source). Source is 'playbook', 'deferred',
    or 'declined'.

    Playbook structure: top-level has question_id, foundation_text,
    acronym_strip, subquestions. subquestions is a dict keyed by "1.1.1" etc.
    Each subquestion has variant_question, demonstration, memo_marks,
    fast_path, fatal_error, answer_book_layout, hack, trap, presentation.
    """
    pb = _load_playbook(question_id)
    if not pb:
        return None, "deferred"

    # Homework / off-topic: log but decline explicitly
    if intent == "off_topic":
        return None, "declined"

    # Descend into subquestions if present
    content = pb
    if "subquestions" in pb and isinstance(pb["subquestions"], dict):
        sq_key = ""
        if "_Q" in question_id:
            sq_key = question_id.split("_Q")[-1]
        if sq_key and sq_key in pb["subquestions"]:
            content = pb["subquestions"][sq_key]

    def _get(key):
        v = content.get(key)
        if v is None and content is not pb:
            v = pb.get(key)
        return v

    if intent == "curiosity":
        answer = _get("fatal_error") or _get("fast_path") or _get("hack")
        if answer:
            return answer, "playbook"

    if intent == "frustration":
        fast = _get("fast_path")
        if fast:
            return f"Let's try the fast path: {fast}", "playbook"
        fatal = _get("fatal_error")
        if fatal:
            return f"Take a breath. The key thing here: {fatal}", "playbook"

    if intent == "alternative_method":
        demo = _get("demonstration")
        if demo:
            if isinstance(demo, list):
                demo = " ".join(str(d) for d in demo)
            return f"Here's the standard way: {demo}", "playbook"

    if intent == "question_about_work":
        fast = _get("fast_path")
        if fast:
            return fast, "playbook"

    # Fallback: fatal_error if present
    fatal = _get("fatal_error")
    if fatal:
        return fatal, "playbook"

    return None, "deferred"


def capture_question(store, learner_id, session_id, skill_id, question_id,
                     question_text, llm_classify=None):
    """Capture a learner question. Rules first, LLM fallback if provided.

    llm_classify (optional): callable(text) -> dict with keys:
        {'intent': str, 'confidence': float, 'answer_hint': str|None}
        When None (default): rules-only. Ships safe before November.

    Returns dict with:
        event_id, intent, rule_intent, confidence, classifier_source,
        answer_text, answer_source, lane_key
    """
    if not question_text or not question_text.strip():
        return None

    text = question_text.strip()

    # Step 1: rules
    rule_intent, rule_confidence = classify_intent(text)
    intent = rule_intent
    confidence = rule_confidence
    classifier_source = "rule"

    # Step 2: LLM escalation if low confidence
    if confidence < 0.7 and llm_classify is not None:
        try:
            result = llm_classify(text) or {}
            llm_intent = result.get("intent")
            llm_conf = float(result.get("confidence", 0.0))
            if llm_intent and llm_conf > confidence:
                intent = llm_intent
                confidence = llm_conf
                classifier_source = "llm"
        except Exception:
            pass

    # Step 3: playbook match
    answer_text, answer_source = match_playbook_answer(question_id, intent)

    # Step 4: LLM answer fallback if no playbook answer
    if answer_source == "deferred" and llm_classify is not None:
        try:
            result = llm_classify(text) or {}
            hint = result.get("answer_hint")
            if hint:
                answer_text = hint
                answer_source = "llm"
        except Exception:
            pass

    lane_key = f"{skill_id or 'unknown'}/none/intent:{intent}"

    event_id = "conv_" + uuid.uuid4().hex[:12]
    store.conn.execute(
        "INSERT INTO learner_events "
        "(event_id, learner_id, skill_id, question_id, event_type, timestamp, "
        "notes, session_id, question_text, answer_text, answer_source, "
        "lane_key, intent, rule_intent, classifier_source, "
        "classifier_confidence, next_attempt_id) "
        "VALUES (?, ?, ?, ?, 'CONVERSATION', ?, NULL, ?, ?, ?, ?, "
        "?, ?, ?, ?, ?, NULL)",
        (event_id, learner_id, skill_id, question_id, _now_iso(),
         session_id, text, answer_text, answer_source,
         lane_key, intent, rule_intent, classifier_source,
         confidence),
    )
    store.conn.commit()

    return {
        "event_id": event_id,
        "intent": intent,
        "rule_intent": rule_intent,
        "confidence": confidence,
        "classifier_source": classifier_source,
        "answer_text": answer_text,
        "answer_source": answer_source,
        "lane_key": lane_key,
    }


def link_next_attempt(store, conversation_event_id, attempt_id):
    """Link a conversation event to its next attempt. Idempotent."""
    if not conversation_event_id or not attempt_id:
        return False
    cur = store.conn.execute(
        "UPDATE learner_events SET next_attempt_id = ? "
        "WHERE event_id = ? AND next_attempt_id IS NULL",
        (attempt_id, conversation_event_id),
    )
    store.conn.commit()
    return cur.rowcount > 0


def get_conversations(node_id, days=30, intent=None, conn=None):
    """Analyst query: list CONVERSATION events for a node's members."""
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        close_after = True
    try:
        from .cohort_nodes import list_descendant_learners
        members = list_descendant_learners(node_id, conn=conn)
        if not members:
            return []

        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        placeholders = ",".join("?" * len(members))

        params = list(members) + [since]
        sql = (
            f"SELECT * FROM learner_events "
            f"WHERE learner_id IN ({placeholders}) "
            f"AND event_type = 'CONVERSATION' "
            f"AND timestamp >= ?"
        )
        if intent:
            sql += " AND intent = ?"
            params.append(intent)
        sql += " ORDER BY timestamp DESC"

        return [dict(r) for r in conn.execute(sql, tuple(params)).fetchall()]
    finally:
        if close_after:
            conn.close()


def conversation_stats(node_id, days=30, conn=None):
    """Analyst summary: counts by intent, by source, by lane; LLM agreement rate.

    Returns:
      {'node_id', 'window_days', 'total', 'by_intent', 'by_source',
       'rule_llm_agreement': {'compared': N, 'agreed': M, 'pct': P},
       'answered', 'answered_pct', 'linked', 'linked_pct',
       'deferred_count', 'top_lanes': [(lane, count), ...]}
    """
    convs = get_conversations(node_id, days=days, conn=conn)
    by_intent = {}
    by_source = {}
    by_lane = {}
    linked = 0
    answered = 0
    deferred_count = 0
    compared = 0
    agreed = 0

    for c in convs:
        i = c.get("intent") or "unknown"
        s = c.get("answer_source") or "unknown"
        ln = c.get("lane_key") or "unknown"
        by_intent[i] = by_intent.get(i, 0) + 1
        by_source[s] = by_source.get(s, 0) + 1
        by_lane[ln] = by_lane.get(ln, 0) + 1
        if c.get("next_attempt_id"):
            linked += 1
        if c.get("answer_text"):
            answered += 1
        if s == "deferred":
            deferred_count += 1
        # Rule vs LLM agreement
        ri = c.get("rule_intent")
        cs = c.get("classifier_source")
        if ri and i and cs == "llm":
            compared += 1
            if ri == i:
                agreed += 1

    total = len(convs)
    top_lanes = sorted(by_lane.items(), key=lambda x: -x[1])[:5]

    return {
        "node_id": node_id,
        "window_days": days,
        "total": total,
        "by_intent": by_intent,
        "by_source": by_source,
        "rule_llm_agreement": {
            "compared": compared,
            "agreed": agreed,
            "pct": round(agreed / compared * 100, 1) if compared else None,
        },
        "answered": answered,
        "answered_pct": round(answered / total * 100, 1) if total else 0.0,
        "linked": linked,
        "linked_pct": round(linked / total * 100, 1) if total else 0.0,
        "deferred_count": deferred_count,
        "top_lanes": top_lanes,
    }
