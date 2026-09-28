"""Tutor discovery store.

The beginning of the tutor's institutional memory.

A discovery is a first-class object: a pattern the tutor noticed that
its existing rules could not explain. The evidence (raw learner lines)
is preserved. Recurrence strengthens the pattern. The teacher can
confirm, dismiss, or promote it.

Per docs/architecture.md:
  - discoveries are persistent
  - evidence is preserved
  - recurrence strengthens (times_seen, learners_affected)
  - teacher can confirm / dismiss / promote
  - the LLM explanation is optional and revisable
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalise_lines(lines: list[str]) -> str:
    """Canonical pattern from raw learner lines.

    Lowercase, collapse whitespace, treat commas and 'or' as equivalent.
    The goal: 'x = 3 or 1' and 'x=3 or 1' produce the same key.
    """
    parts = []
    for ln in lines:
        s = ln.lower().strip()
        s = re.sub(r"\s+", "", s)
        s = s.replace(",", "or")
        parts.append(s)
    return " | ".join(parts)


class DiscoveryStore:
    """Storage layer for the Tutor Learning Engine.

    A DiscoveryStore is bound to the same sqlite connection as the
    LearnerStore so learner and tutor memory share one file.
    """

    def __init__(self, conn):
        self.conn = conn

    def record(
        self,
        learner_id: str,
        skill_id: str,
        question_id: str,
        learner_lines: list[str],
        expected_answer: str,
        session_id: Optional[str] = None,
        n08_match: Optional[str] = None,
        dbe_rule_match: Optional[str] = None,
        llm_explanation: Optional[str] = None,
        llm_certainty: Optional[float] = None,
    ) -> str:
        """Record an unresolved case. Returns the discovery_id.

        The tutor decides errors on its own evidence: memo, math grader,
        N08 library, DBE reports, recurrence, LLM reasoning. Teacher
        confirmation is an optional additional signal, not a gate.

        If an identical (skill_id, pattern) already exists, increments it,
        adds this learner, and recomputes confidence from all signals.
        """
        pattern = _normalise_lines(learner_lines)
        existing = self.conn.execute(
            "SELECT discovery_id, times_seen, learners_affected, evidence_signals "
            "FROM tutor_discovery "
            "WHERE skill_id = ? AND pattern_description = ?",
            (skill_id, pattern),
        ).fetchone()

        if existing:
            try:
                learners = json.loads(existing["learners_affected"])
            except Exception:
                learners = []
            if learner_id not in learners:
                learners.append(learner_id)

            try:
                signals = json.loads(existing["evidence_signals"] or "{}")
            except Exception:
                signals = {}
            signals["recurrence_count"] = int(signals.get("recurrence_count", 1)) + 1
            signals["learners_affected"] = learners
            if n08_match and not signals.get("n08_match"):
                signals["n08_match"] = n08_match
            if dbe_rule_match and not signals.get("dbe_rule_match"):
                signals["dbe_rule_match"] = dbe_rule_match

            new_conf = compute_confidence(signals)
            new_status = derive_status(new_conf, signals)

            self.conn.execute(
                "UPDATE tutor_discovery SET "
                "  times_seen = times_seen + 1, "
                "  last_seen_at = ?, "
                "  learners_affected = ?, "
                "  evidence_signals = ?, "
                "  confidence = ?, "
                "  status = ? "
                "WHERE discovery_id = ?",
                (_now(), json.dumps(learners), json.dumps(signals),
                 new_conf, new_status, existing["discovery_id"]),
            )
            self.conn.commit()
            return existing["discovery_id"]

        signals = dict(SIGNAL_DEFAULTS)
        signals["learners_affected"] = [learner_id]
        signals["recurrence_count"] = 1
        if n08_match:
            signals["n08_match"] = n08_match
        if dbe_rule_match:
            signals["dbe_rule_match"] = dbe_rule_match
        if llm_explanation:
            signals["llm_explanation"] = llm_explanation
        if llm_certainty is not None:
            signals["llm_certainty"] = llm_certainty

        conf = compute_confidence(signals)
        status = derive_status(conf, signals)

        disc_id = "disc_" + uuid.uuid4().hex[:12]
        self.conn.execute(
            "INSERT INTO tutor_discovery "
            "(discovery_id, pattern_description, example_lines, "
            " first_seen_at, last_seen_at, times_seen, learners_affected, "
            " confidence, skill_id, question_id, expected_answer, "
            " session_id, status, evidence_signals, llm_explanation) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                disc_id,
                pattern,
                json.dumps(learner_lines),
                _now(), _now(), 1,
                json.dumps([learner_id]),
                conf,
                skill_id, question_id, expected_answer,
                session_id,
                status,
                json.dumps(signals),
                llm_explanation,
            ),
        )
        self.conn.commit()
        return disc_id

    def add_teacher_note(self, discovery_id: str, note: str) -> None:
        self.conn.execute(
            "UPDATE tutor_discovery SET teacher_notes = ? "
            "WHERE discovery_id = ?",
            (note, discovery_id),
        )
        self.conn.commit()

    def set_status(self, discovery_id: str, status: str) -> None:
        """status in {'open', 'confirmed', 'dismissed', 'promoted'}"""
        if status not in ("open", "confirmed", "dismissed", "promoted"):
            raise ValueError("invalid status: " + status)
        self.conn.execute(
            "UPDATE tutor_discovery SET status = ?, "
            "  promoted_to_rule = CASE WHEN ? = 'promoted' "
            "    THEN 1 ELSE promoted_to_rule END "
            "WHERE discovery_id = ?",
            (status, status, discovery_id),
        )
        self.conn.commit()

    def get(self, discovery_id: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM tutor_discovery WHERE discovery_id = ?",
            (discovery_id,),
        ).fetchone()
        return dict(row) if row else None

    def list_open(self, limit: int = 50) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM tutor_discovery WHERE status = 'open' "
            "ORDER BY times_seen DESC, last_seen_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def list_recurring(self, min_times: int = 3) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM tutor_discovery WHERE times_seen >= ? "
            "ORDER BY times_seen DESC, last_seen_at DESC",
            (min_times,),
        ).fetchall()
        return [dict(r) for r in rows]



    def add_signal(self, discovery_id: str, name: str, value) -> None:
        """Add or update a single evidence signal. Recomputes confidence + status."""
        row = self.conn.execute(
            "SELECT evidence_signals FROM tutor_discovery WHERE discovery_id = ?",
            (discovery_id,),
        ).fetchone()
        if not row:
            raise ValueError("no such discovery: " + discovery_id)
        try:
            signals = json.loads(row["evidence_signals"] or "{}")
        except Exception:
            signals = {}
        signals[name] = value
        conf = compute_confidence(signals)
        status = derive_status(conf, signals)
        self.conn.execute(
            "UPDATE tutor_discovery SET evidence_signals = ?, confidence = ?, "
            "  status = ?, last_seen_at = ? WHERE discovery_id = ?",
            (json.dumps(signals), conf, status, _now(), discovery_id),
        )
        self.conn.commit()

    def set_llm_explanation(self, discovery_id: str, text: str,
                             certainty: Optional[float] = None) -> None:
        """Called by the LLM cognitive instrument when it reasons about an unknown."""
        self.conn.execute(
            "UPDATE tutor_discovery SET llm_explanation = ? WHERE discovery_id = ?",
            (text, discovery_id),
        )
        self.add_signal(discovery_id, "llm_explanation", text)
        if certainty is not None:
            self.add_signal(discovery_id, "llm_certainty", float(certainty))

    def endorse(self, discovery_id: str, note: str = "") -> None:
        """Teacher says: yes this is real. One signal among many."""
        self.add_signal(discovery_id, "teacher_endorsed", True)
        if note:
            self.add_signal(discovery_id, "teacher_note", note)

    def dismiss(self, discovery_id: str, note: str = "") -> None:
        """Teacher says: this is noise. Strong negative signal."""
        self.add_signal(discovery_id, "teacher_dismissed", True)
        if note:
            self.add_signal(discovery_id, "teacher_note", note)

    def promote(self, discovery_id: str) -> None:
        """Tutor's own decision to make this pattern permanent."""
        self.add_signal(discovery_id, "promoted_to_rule", True)

    def recompute(self, discovery_id: str) -> dict:
        """Force a confidence + status recompute. Useful after bulk signal changes."""
        row = self.conn.execute(
            "SELECT evidence_signals FROM tutor_discovery WHERE discovery_id = ?",
            (discovery_id,),
        ).fetchone()
        if not row:
            raise ValueError("no such discovery: " + discovery_id)
        try:
            signals = json.loads(row["evidence_signals"] or "{}")
        except Exception:
            signals = {}
        conf = compute_confidence(signals)
        status = derive_status(conf, signals)
        self.conn.execute(
            "UPDATE tutor_discovery SET confidence = ?, status = ? WHERE discovery_id = ?",
            (conf, status, discovery_id),
        )
        self.conn.commit()
        return {"confidence": conf, "status": status, "signals": signals}

    def summary(self) -> dict:
        cur = self.conn.execute
        total = cur("SELECT COUNT(*) FROM tutor_discovery").fetchone()[0]
        open_ = cur(
            "SELECT COUNT(*) FROM tutor_discovery WHERE status = 'open'"
        ).fetchone()[0]
        recurring = cur(
            "SELECT COUNT(*) FROM tutor_discovery WHERE times_seen >= 3"
        ).fetchone()[0]
        confirmed = cur(
            "SELECT COUNT(*) FROM tutor_discovery WHERE status = 'confirmed'"
        ).fetchone()[0]
        return {
            "total": total,
            "open": open_,
            "recurring": recurring,
            "teacher_confirmed": confirmed,
        }



# ============================================================
# Signal model — tutor decides on its own evidence
# ============================================================

# Signal names — each one is a fact the tutor knows, not an opinion.
# Additional signals can be added without breaking existing records.
SIGNAL_DEFAULTS = {
    "answer_wrong": False,            # math_grader said NO_MATCH
    "steps_missing": [],              # list of step indices NOT_MATCHED
    "n08_match": None,                # misconception_id from N08 library
    "dbe_rule_match": None,           # PR_* rule id from DBE diagnostic reports
    "llm_explanation": None,          # free text, from LLM cognitive instrument
    "recurrence_count": 1,            # how many times this pattern has been seen
    "learners_affected": [],          # learner_ids
    "cross_skill": False,             # same pattern seen on different skills
    "successful_intervention": None,  # True / False / None after transfer test
    "teacher_note": None,             # teacher's context if given
    "teacher_endorsed": False,        # teacher added a boost
    "teacher_dismissed": False,       # teacher flagged as noise
}


# Weights — how much each signal contributes to confidence.
# Tunable. None required. This is the tutor's own math.
SIGNAL_WEIGHTS = {
    "answer_wrong": 0.15,
    "steps_missing": 0.10,
    "n08_match": 0.25,
    "dbe_rule_match": 0.20,
    "llm_certainty": 0.15,
    "recurrence_per_occurrence": 0.05,   # capped at 0.30
    "recurrence_cap": 0.30,
    "cross_skill": 0.10,
    "successful_intervention": 0.20,
    "teacher_endorsed": 0.15,
    "teacher_dismissed": -0.50,
}


def compute_confidence(signals: dict) -> float:
    """Compute confidence from evidence signals. Never exceeds 1.0, never below 0.0."""
    score = 0.0
    if signals.get("answer_wrong"):
        score += SIGNAL_WEIGHTS["answer_wrong"]
    if signals.get("steps_missing"):
        score += SIGNAL_WEIGHTS["steps_missing"]
    if signals.get("n08_match"):
        score += SIGNAL_WEIGHTS["n08_match"]
    if signals.get("dbe_rule_match"):
        score += SIGNAL_WEIGHTS["dbe_rule_match"]
    llm_cert = signals.get("llm_certainty")
    if isinstance(llm_cert, (int, float)):
        score += SIGNAL_WEIGHTS["llm_certainty"] * float(llm_cert)
    rec = int(signals.get("recurrence_count", 1))
    score += min(SIGNAL_WEIGHTS["recurrence_cap"],
                 (rec - 1) * SIGNAL_WEIGHTS["recurrence_per_occurrence"])
    if signals.get("cross_skill"):
        score += SIGNAL_WEIGHTS["cross_skill"]
    if signals.get("successful_intervention") is True:
        score += SIGNAL_WEIGHTS["successful_intervention"]
    if signals.get("teacher_endorsed"):
        score += SIGNAL_WEIGHTS["teacher_endorsed"]
    if signals.get("teacher_dismissed"):
        score += SIGNAL_WEIGHTS["teacher_dismissed"]
    return max(0.0, min(1.0, score))


def derive_status(confidence: float, signals: dict) -> str:
    """The tutor decides its own status. Teacher is one signal, not a gate."""
    if signals.get("teacher_dismissed"):
        return "teacher_dismissed"
    if signals.get("promoted_to_rule"):
        return "promoted"
    if signals.get("teacher_endorsed"):
        return "teacher_endorsed"
    if confidence >= 0.55:
        return "established"
    if int(signals.get("recurrence_count", 1)) >= 3:
        return "recurring"
    return "noticed"
