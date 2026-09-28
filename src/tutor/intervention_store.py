"""Intervention + outcome store.

The measurement layer of the Tutor Learning Engine.

When the tutor takes a corrective action (shows a memo line, routes to a
prerequisite, offers a worked example), that action is logged as an
intervention. When the learner demonstrates improvement later, that is
logged as an outcome.

The fourth question -- "did that teaching actually work?" -- is
answered by looking at the outcome table.

Design principles (from docs/spirit.md):
  - Every corrective action is measured, not assumed.
  - Transfer matters more than immediate performance.
  - Outcomes feed back into discoveries as signals.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _days_between(iso_a: str, iso_b: str) -> Optional[int]:
    try:
        a = datetime.fromisoformat(iso_a)
        b = datetime.fromisoformat(iso_b)
        return abs((b - a).days)
    except Exception:
        return None


ACTION_TYPES = (
    "memo_line_shown",       # tutor showed the memo's version of a missed step
    "prerequisite_drill",    # tutor routed to a foundational drill
    "worked_example",        # tutor showed a sibling / worked example
    "hint",                  # tutor gave a specific hint
    "teacher_referred",      # discovery referred to teacher dashboard
)

RESULT_VALUES = ("improved", "unchanged", "worsened", "unknown")


class InterventionStore:
    """Log interventions and outcomes against the same sqlite connection."""

    def __init__(self, conn):
        self.conn = conn

    # ------------------------------------------------------------------
    # Interventions
    # ------------------------------------------------------------------

    def log(
        self,
        learner_id: str,
        skill_id: str,
        action_type: str,
        action_desc: str,
        discovery_id: Optional[str] = None,
        question_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> str:
        if action_type not in ACTION_TYPES:
            raise ValueError("invalid action_type: " + action_type)
        inv_id = "inv_" + uuid.uuid4().hex[:12]
        self.conn.execute(
            "INSERT INTO intervention "
            "(intervention_id, learner_id, discovery_id, skill_id, question_id, "
            " action_type, action_desc, applied_at, session_id, context) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                inv_id, learner_id, discovery_id, skill_id, question_id,
                action_type, action_desc, _now(), session_id,
                json.dumps(context or {}),
            ),
        )
        self.conn.commit()
        return inv_id

    def get(self, intervention_id: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM intervention WHERE intervention_id = ?",
            (intervention_id,),
        ).fetchone()
        return dict(row) if row else None

    def list_open(self, learner_id: str, skill_id: str) -> list[dict]:
        """Interventions on this learner + skill with no outcome recorded yet."""
        rows = self.conn.execute(
            "SELECT i.* FROM intervention i "
            "LEFT JOIN outcome o ON o.intervention_id = i.intervention_id "
            "WHERE i.learner_id = ? AND i.skill_id = ? AND o.outcome_id IS NULL "
            "ORDER BY i.applied_at DESC",
            (learner_id, skill_id),
        ).fetchall()
        return [dict(r) for r in rows]

    def list_recent(self, limit: int = 50) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM intervention ORDER BY applied_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Outcomes
    # ------------------------------------------------------------------

    def record_outcome(
        self,
        intervention_id: str,
        learner_id: str,
        result: str,
        measurement_kind: str = "transfer",
        evidence: Optional[dict] = None,
    ) -> str:
        if result not in RESULT_VALUES:
            raise ValueError("invalid result: " + result)
        inv = self.get(intervention_id)
        if not inv:
            raise ValueError("no such intervention: " + intervention_id)
        days = _days_between(inv["applied_at"], _now())
        out_id = "out_" + uuid.uuid4().hex[:12]
        self.conn.execute(
            "INSERT INTO outcome "
            "(outcome_id, intervention_id, learner_id, measured_at, "
            " measurement_kind, result, days_since, evidence) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                out_id, intervention_id, learner_id, _now(),
                measurement_kind, result, days,
                json.dumps(evidence or {}),
            ),
        )
        self.conn.commit()

        # Feed back into the discovery as a signal
        if inv.get("discovery_id"):
            self._update_discovery_signal(
                inv["discovery_id"], result, inv["action_type"]
            )
        return out_id

    def _update_discovery_signal(
        self, discovery_id: str, result: str, action_type: str
    ) -> None:
        """Reflect the outcome back into the discovery's evidence signals."""
        try:
            row = self.conn.execute(
                "SELECT evidence_signals FROM tutor_discovery WHERE discovery_id = ?",
                (discovery_id,),
            ).fetchone()
            if not row:
                return
            try:
                signals = json.loads(row["evidence_signals"] or "{}")
            except Exception:
                signals = {}
            # Aggregate: any successful intervention proves it can be fixed
            history = signals.get("intervention_history", [])
            history.append({
                "action": action_type,
                "result": result,
                "at": _now(),
            })
            signals["intervention_history"] = history[-20:]  # cap
            if result == "improved":
                signals["successful_intervention"] = True
            elif result == "worsened" and not signals.get("successful_intervention"):
                signals["successful_intervention"] = False
            self.conn.execute(
                "UPDATE tutor_discovery SET evidence_signals = ?, "
                "  last_seen_at = ? WHERE discovery_id = ?",
                (json.dumps(signals), _now(), discovery_id),
            )
            self.conn.commit()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Effectiveness
    # ------------------------------------------------------------------

    def effectiveness(self, discovery_id: str) -> dict:
        """Across all interventions for a discovery: how often did it work?"""
        rows = self.conn.execute(
            "SELECT o.result, COUNT(*) as n FROM outcome o "
            "JOIN intervention i ON i.intervention_id = o.intervention_id "
            "WHERE i.discovery_id = ? "
            "GROUP BY o.result",
            (discovery_id,),
        ).fetchall()
        counts = {r["result"]: r["n"] for r in rows}
        total = sum(counts.values())
        improved = counts.get("improved", 0)
        return {
            "discovery_id": discovery_id,
            "total": total,
            "improved": improved,
            "unchanged": counts.get("unchanged", 0),
            "worsened": counts.get("worsened", 0),
            "rate": (improved / total) if total else 0.0,
        }

    def summary(self) -> dict:
        cur = self.conn.execute
        total_inv = cur("SELECT COUNT(*) FROM intervention").fetchone()[0]
        total_out = cur("SELECT COUNT(*) FROM outcome").fetchone()[0]
        improved = cur(
            "SELECT COUNT(*) FROM outcome WHERE result = 'improved'"
        ).fetchone()[0]
        return {
            "interventions": total_inv,
            "outcomes": total_out,
            "improved": improved,
            "measured_rate": (improved / total_out) if total_out else 0.0,
        }
