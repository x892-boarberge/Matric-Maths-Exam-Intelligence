"""Versioned mastery policy and decision logging.

The single source of truth for how mastery claims are made.
Policy lives in the database so every decision retains the exact rule that produced it.
"""
from datetime import datetime, timezone, timedelta
import json
import uuid


INITIAL_POLICY = {
    "version": "v1_2026_10",
    "threshold_k": 4,
    "threshold_n": 5,
    "sittings_required": 2,
    "spacing_min_days": 7,
    "spacing_max_days": 14,
    "variant_required": True,
    "retention_delay_days": 30,
    "retention_grace_days": 7,
    "retention_threshold_k": 4,
    "retention_threshold_n": 5,
    "notes": ("Initial policy, provisional. Subject to calibration against "
              "retention outcomes. Change only through explicit version bump."),
}


def _now():
    return datetime.now(timezone.utc).isoformat()


def seed_initial_policy(conn):
    """Insert initial policy if not present. Returns True if inserted."""
    existing = conn.execute(
        "SELECT version FROM mastery_policy WHERE version = ?",
        (INITIAL_POLICY["version"],),
    ).fetchone()
    if existing:
        return False
    conn.execute(
        """INSERT INTO mastery_policy
           (version, threshold_k, threshold_n, sittings_required,
            spacing_min_days, spacing_max_days, variant_required,
            retention_delay_days, retention_grace_days,
            retention_threshold_k, retention_threshold_n,
            created_at, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            INITIAL_POLICY["version"],
            INITIAL_POLICY["threshold_k"],
            INITIAL_POLICY["threshold_n"],
            INITIAL_POLICY["sittings_required"],
            INITIAL_POLICY["spacing_min_days"],
            INITIAL_POLICY["spacing_max_days"],
            1 if INITIAL_POLICY["variant_required"] else 0,
            INITIAL_POLICY["retention_delay_days"],
            INITIAL_POLICY["retention_grace_days"],
            INITIAL_POLICY["retention_threshold_k"],
            INITIAL_POLICY["retention_threshold_n"],
            _now(),
            INITIAL_POLICY["notes"],
        ),
    )
    conn.commit()
    return True


def load_policy(conn, version=None):
    """Load policy by version, or the most recent one."""
    if version:
        row = conn.execute(
            "SELECT * FROM mastery_policy WHERE version = ?", (version,)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM mastery_policy ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
    if not row:
        return None
    cols = [d[0] for d in row.keys()] if hasattr(row, "keys") else None
    if cols:
        return dict(row)
    return dict(zip(
        [d[0] for d in conn.execute("SELECT * FROM mastery_policy LIMIT 0").description],
        row,
    ))


def log_decision(conn, learner_id, skill_id, tier_at_decision,
                 evidence, question_ids, skill_coverage,
                 policy_version=None):
    """Log a mastery decision. Skips if an identical decision already exists
    for (learner, skill, current tier, policy_version) - avoids duplicate logging
    when the report is regenerated repeatedly.

    Returns the decision_id (new or existing), or None on error.
    """
    policy = load_policy(conn, policy_version)
    if not policy:
        return None

    # Idempotency check: same (learner, skill, tier, policy)
    existing = conn.execute(
        """SELECT decision_id FROM mastery_decision
           WHERE learner_id = ? AND skill_id = ? AND tier_at_decision = ?
                 AND policy_version = ?
           ORDER BY decided_at DESC LIMIT 1""",
        (learner_id, skill_id, tier_at_decision, policy["version"]),
    ).fetchone()
    if existing:
        return existing[0]

    # Only log L4-provisional decisions (those that claim mastery)
    if tier_at_decision != "L4-provisional":
        return None

    decision_id = "dec_" + uuid.uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    due = now + timedelta(days=policy["retention_delay_days"])

    conn.execute(
        """INSERT INTO mastery_decision
           (decision_id, learner_id, skill_id, policy_version, decided_at,
            tier_at_decision, evidence_json, question_ids, skill_coverage,
            retention_due_at, retention_status, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
        (
            decision_id,
            learner_id,
            skill_id,
            policy["version"],
            now.isoformat(),
            tier_at_decision,
            json.dumps(evidence) if not isinstance(evidence, str) else evidence,
            json.dumps(question_ids) if not isinstance(question_ids, str) else question_ids,
            json.dumps(skill_coverage) if not isinstance(skill_coverage, str) else skill_coverage,
            due.isoformat(),
            "Scheduled at provisional-mastery decision. Retention check due day %d." % policy["retention_delay_days"],
        ),
    )
    conn.commit()
    return decision_id


def get_decision(conn, decision_id):
    row = conn.execute(
        "SELECT * FROM mastery_decision WHERE decision_id = ?", (decision_id,)
    ).fetchone()
    if not row:
        return None
    return dict(zip([d[0] for d in conn.execute(
        "SELECT * FROM mastery_decision LIMIT 0").description], row))
