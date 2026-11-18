"""hypothesis.py — analyst hypothesis ledger.

Every analysis Tanaka runs should be logged: the question, the data
snapshot, the finding, the proposed action, the predicted outcome.
Later, when the outcome is measurable, log whether the prediction held.

Discipline this enforces:
  - You can tell if a "trend" is new or was already seen last week
  - You can tell if your interventions work
  - Institutional memory survives across sessions

Status values:
  proposed             - hypothesis written, not yet tested
  pending_measurement  - action taken, waiting for predicted outcome
  confirmed            - prediction held
  refuted              - prediction failed
  abandoned            - superseded or no longer relevant

Cost: O(1) per operation (single-row insert or read).
"""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _find_root():
    r = Path(".").resolve()
    for c in [r, *r.parents]:
        if (c / "src" / "tutor").is_dir():
            return c
    return r


ROOT = _find_root()
DB = ROOT / "data" / "learner_store" / "learners.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS hypothesis (
    hypothesis_id     TEXT PRIMARY KEY,
    generated_at      TEXT NOT NULL,
    question          TEXT NOT NULL,
    scope_node        TEXT,
    data_version      TEXT,
    finding_json      TEXT NOT NULL,
    confidence        REAL,
    proposed_action   TEXT,
    predicted_outcome TEXT,
    status            TEXT NOT NULL DEFAULT 'proposed',
    resolved_at       TEXT,
    outcome_correct   INTEGER,
    notes             TEXT,
    created_by        TEXT NOT NULL DEFAULT 'analyst'
);

CREATE INDEX IF NOT EXISTS idx_hypothesis_node_status
    ON hypothesis(scope_node, status, generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_hypothesis_status
    ON hypothesis(status, generated_at DESC);
"""


def _now():
    return datetime.now(timezone.utc).isoformat()


def ensure_schema(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def _row_to_dict(row, cur):
    if hasattr(row, "keys"):
        d = dict(row)
    else:
        cols = [c[0] for c in cur.description]
        d = dict(zip(cols, row))
    try:
        d["finding_json"] = json.loads(d.get("finding_json") or "{}")
    except json.JSONDecodeError:
        d["finding_json"] = {}
    return d


def propose(question, finding, scope_node=None, data_version=None,
            confidence=None, proposed_action=None, predicted_outcome=None,
            created_by="analyst", conn=None):
    """Create a new hypothesis. Returns the full hypothesis dict.

    finding: dict — the raw analyst output (any analyst function's return)
    confidence: 0.0-1.0 or None (unknown)
    """
    if not question or not question.strip():
        raise ValueError("question cannot be empty")
    if not isinstance(finding, dict):
        raise ValueError("finding must be a dict")

    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        ensure_schema(conn)
        hid = "hyp_" + uuid.uuid4().hex[:12]
        conn.execute(
            "INSERT INTO hypothesis "
            "(hypothesis_id, generated_at, question, scope_node, data_version, "
            "finding_json, confidence, proposed_action, predicted_outcome, "
            "status, created_by) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'proposed', ?)",
            (hid, _now(), question.strip(), scope_node, data_version,
             json.dumps(finding, sort_keys=True, default=str),
             confidence, proposed_action, predicted_outcome, created_by),
        )
        conn.commit()
        return get(hid, conn=conn)
    finally:
        if close_after:
            conn.close()


def get(hypothesis_id, conn=None):
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        close_after = True
    try:
        ensure_schema(conn)
        cur = conn.execute(
            "SELECT * FROM hypothesis WHERE hypothesis_id = ?",
            (hypothesis_id,),
        )
        row = cur.fetchone()
        return _row_to_dict(row, cur) if row else None
    finally:
        if close_after:
            conn.close()


def mark_pending(hypothesis_id, conn=None):
    """Transition proposed -> pending_measurement (action was taken)."""
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        ensure_schema(conn)
        h = get(hypothesis_id, conn=conn)
        if not h:
            raise ValueError(f"hypothesis '{hypothesis_id}' not found")
        if h["status"] != "proposed":
            raise ValueError(
                f"can only mark pending from 'proposed', current is '{h['status']}'"
            )
        conn.execute(
            "UPDATE hypothesis SET status = 'pending_measurement' "
            "WHERE hypothesis_id = ?",
            (hypothesis_id,),
        )
        conn.commit()
        return get(hypothesis_id, conn=conn)
    finally:
        if close_after:
            conn.close()


def record_outcome(hypothesis_id, correct, notes=None, outcome_detail=None,
                   conn=None):
    """Record that a prediction held (correct=True) or failed.

    correct: bool — did the predicted outcome occur?
    outcome_detail: optional dict — extra evidence
    """
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        ensure_schema(conn)
        h = get(hypothesis_id, conn=conn)
        if not h:
            raise ValueError(f"hypothesis '{hypothesis_id}' not found")

        status = "confirmed" if correct else "refuted"
        final_notes = notes
        if outcome_detail:
            detail_str = json.dumps(outcome_detail, sort_keys=True, default=str)
            final_notes = (notes + "\n" if notes else "") + "outcome: " + detail_str

        conn.execute(
            "UPDATE hypothesis SET status = ?, resolved_at = ?, "
            "outcome_correct = ?, notes = ? WHERE hypothesis_id = ?",
            (status, _now(), 1 if correct else 0, final_notes, hypothesis_id),
        )
        conn.commit()
        return get(hypothesis_id, conn=conn)
    finally:
        if close_after:
            conn.close()


def list_open(conn=None):
    """Return all proposed or pending_measurement hypotheses, newest first."""
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        close_after = True
    try:
        ensure_schema(conn)
        cur = conn.execute(
            "SELECT * FROM hypothesis "
            "WHERE status IN ('proposed', 'pending_measurement') "
            "ORDER BY generated_at DESC"
        )
        return [_row_to_dict(r, cur) for r in cur.fetchall()]
    finally:
        if close_after:
            conn.close()


def list_resolved(limit=20, conn=None):
    """Return confirmed/refuted hypotheses, newest first."""
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        close_after = True
    try:
        ensure_schema(conn)
        cur = conn.execute(
            "SELECT * FROM hypothesis "
            "WHERE status IN ('confirmed', 'refuted') "
            "ORDER BY resolved_at DESC LIMIT ?",
            (limit,),
        )
        return [_row_to_dict(r, cur) for r in cur.fetchall()]
    finally:
        if close_after:
            conn.close()


def history_for_node(node_id, conn=None):
    """All hypotheses scoped to a node, newest first."""
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        close_after = True
    try:
        ensure_schema(conn)
        cur = conn.execute(
            "SELECT * FROM hypothesis WHERE scope_node = ? "
            "ORDER BY generated_at DESC",
            (node_id,),
        )
        return [_row_to_dict(r, cur) for r in cur.fetchall()]
    finally:
        if close_after:
            conn.close()


def summary(conn=None):
    """Aggregate: counts by status, accuracy of resolved predictions."""
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        close_after = True
    try:
        ensure_schema(conn)
        rows = conn.execute(
            "SELECT status, COUNT(*) AS n FROM hypothesis GROUP BY status"
        ).fetchall()
        by_status = {r[0]: r[1] for r in rows}
        confirmed = by_status.get("confirmed", 0)
        refuted = by_status.get("refuted", 0)
        resolved = confirmed + refuted
        return {
            "by_status": by_status,
            "total": sum(by_status.values()),
            "open": (by_status.get("proposed", 0)
                     + by_status.get("pending_measurement", 0)),
            "resolved": resolved,
            "confirmed": confirmed,
            "refuted": refuted,
            "accuracy": (confirmed / resolved) if resolved else None,
        }
    finally:
        if close_after:
            conn.close()
