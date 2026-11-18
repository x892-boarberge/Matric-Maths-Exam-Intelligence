"""Retention check scheduler for durable mastery verification.

Handles:
- Finding pending retention checks (soft prompt to learner)
- Finding overdue checks (>grace window past due)
- Marking pending checks as missing when overdue
- Recording retention test results

The states are distinct by design:
    pending     — check due, not yet attempted (default)
    passed      — attempted, passed at retention threshold
    failed      — attempted, failed at retention threshold
    missing     — grace window passed without attempt
    dismissed   — learner explicitly opted out permanently
"""
from datetime import datetime, timezone, timedelta
import json


def _now():
    return datetime.now(timezone.utc)


def _parse(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def get_pending_retention_checks(conn, learner_id):
    """Return decisions where retention is due (or soon) and status='pending'.
    Sorted by due date, oldest first.
    """
    now_iso = _now().isoformat()
    rows = conn.execute(
        """SELECT * FROM mastery_decision
           WHERE learner_id = ?
             AND retention_status = 'pending'
             AND retention_due_at <= ?
           ORDER BY retention_due_at ASC""",
        (learner_id, now_iso),
    ).fetchall()
    return [dict(zip([d[0] for d in conn.execute(
        "SELECT * FROM mastery_decision LIMIT 0").description], r)) for r in rows]


def get_all_pending_retention_checks(conn, learner_id):
    """All pending checks (including ones not yet due). For reporting."""
    rows = conn.execute(
        """SELECT * FROM mastery_decision
           WHERE learner_id = ? AND retention_status = 'pending'
           ORDER BY retention_due_at ASC""",
        (learner_id,),
    ).fetchall()
    return [dict(zip([d[0] for d in conn.execute(
        "SELECT * FROM mastery_decision LIMIT 0").description], r)) for r in rows]


def mark_missing_overdue(conn, grace_days=None):
    """For every pending decision past due + grace, mark as 'missing'.
    Called at session start. Idempotent.
    """
    if grace_days is None:
        # Default from policy
        row = conn.execute(
            "SELECT retention_grace_days FROM mastery_policy "
            "ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        grace_days = row[0] if row else 7

    now = _now()
    updated = 0
    pending = conn.execute(
        "SELECT decision_id, retention_due_at FROM mastery_decision "
        "WHERE retention_status = 'pending'"
    ).fetchall()
    for decision_id, due_str in pending:
        due = _parse(due_str)
        if not due:
            continue
        if now > due + timedelta(days=grace_days):
            conn.execute(
                "UPDATE mastery_decision SET retention_status = 'missing' "
                "WHERE decision_id = ? AND retention_status = 'pending'",
                (decision_id,),
            )
            updated += 1
    if updated:
        conn.commit()
    return updated


def log_retention_result(conn, decision_id, pass_result,
                         question_ids, skill_coverage, evidence):
    """Record the result of a retention attempt.

    pass_result: True/False
    question_ids: list of question ids used
    skill_coverage: dict describing the coverage (which subtopics/patterns)
    evidence: dict with per-question results, marks, misconception_ids
    """
    status = "passed" if pass_result else "failed"
    conn.execute(
        """UPDATE mastery_decision
           SET retention_status = ?,
               retention_attempted_at = ?,
               retention_pass_result = ?,
               retention_question_ids = ?,
               retention_evidence_json = ?
           WHERE decision_id = ?""",
        (
            status,
            _now().isoformat(),
            1 if pass_result else 0,
            json.dumps(question_ids),
            json.dumps(evidence),
            decision_id,
        ),
    )
    conn.commit()
    return status


def dismiss_decision(conn, decision_id, reason=""):
    """Mark a retention check as permanently dismissed (learner opted out)."""
    conn.execute(
        """UPDATE mastery_decision
           SET retention_status = 'dismissed',
               retention_attempted_at = ?,
               notes = COALESCE(notes, '') || ' | Dismissed: ' || ?
           WHERE decision_id = ?""",
        (_now().isoformat(), reason or "learner opted out", decision_id),
    )
    conn.commit()


def get_durable_mastery(conn, learner_id, skill_id):
    """Return True if learner has a passed retention check for this skill
    under any policy version. Once durable, always durable (until re-test).
    """
    row = conn.execute(
        """SELECT 1 FROM mastery_decision
           WHERE learner_id = ? AND skill_id = ?
             AND retention_status = 'passed'
           LIMIT 1""",
        (learner_id, skill_id),
    ).fetchone()
    return row is not None


def get_retention_summary(conn, learner_id):
    """Return dict: {skill_id: {status, decided_at, due_at, ...}} for reporting."""
    rows = conn.execute(
        """SELECT skill_id, retention_status, decided_at, retention_due_at,
                  retention_attempted_at
           FROM mastery_decision
           WHERE learner_id = ?
           ORDER BY decided_at DESC""",
        (learner_id,),
    ).fetchall()
    out = {}
    for skill_id, status, decided, due, attempted in rows:
        # Keep the most recent decision per skill
        if skill_id not in out:
            out[skill_id] = {
                "status": status,
                "decided_at": decided,
                "due_at": due,
                "attempted_at": attempted,
            }
    return out
