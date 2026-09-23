"""
Learner store (SQLite).

Holds the persistent learner state that survives across sessions:
  learner, session, attempt, mastery

Public:
    open_store(path)                    -> LearnerStore
    LearnerStore.load_learner(id)       -> dict
    LearnerStore.save_attempt(...)      -> None
    LearnerStore.recompute_mastery(id, skill_id) -> str
    LearnerStore.get_mastery(id, skill) -> dict
    LearnerStore.start_session(...)     -> str  (session_id)
    LearnerStore.end_session(session_id) -> None

Mastery criteria (from N08, locked):
  3 correct out of 4 attempts, matching structure type, on two
  separate sittings within 14 days, on unseen items only.
"""
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional


SCHEMA = """
CREATE TABLE IF NOT EXISTS learner (
    learner_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    last_seen TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS session (
    session_id TEXT PRIMARY KEY,
    learner_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    skill_id TEXT
);

CREATE TABLE IF NOT EXISTS attempt (
    attempt_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    learner_id TEXT NOT NULL,
    skill_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    response TEXT,
    diagnosis_rule_id TEXT,
    misconception_id TEXT,
    hint_level TEXT,
    error_type TEXT
);

CREATE TABLE IF NOT EXISTS mastery (
    learner_id TEXT NOT NULL,
    skill_id TEXT NOT NULL,
    mastery_state TEXT NOT NULL,
    sittings_passed INTEGER NOT NULL DEFAULT 0,
    last_sitting_at TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (learner_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_attempt_learner_skill
    ON attempt (learner_id, skill_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_mastery_learner
    ON mastery (learner_id);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LearnerStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # ---------- learner ----------

    def load_learner(self, learner_id: str) -> dict:
        row = self.conn.execute(
            "SELECT * FROM learner WHERE learner_id = ?", (learner_id,)
        ).fetchone()
        now = _now()
        if row is None:
            self.conn.execute(
                "INSERT INTO learner (learner_id, created_at, last_seen) "
                "VALUES (?, ?, ?)", (learner_id, now, now)
            )
            self.conn.commit()
            return {"learner_id": learner_id, "created_at": now,
                    "last_seen": now, "is_new": True}
        self.conn.execute(
            "UPDATE learner SET last_seen = ? WHERE learner_id = ?",
            (now, learner_id)
        )
        self.conn.commit()
        return {**dict(row), "is_new": False}

    # ---------- session ----------

    def start_session(self, learner_id: str, skill_id: str) -> str:
        session_id = "sess_" + uuid.uuid4().hex[:12]
        self.conn.execute(
            "INSERT INTO session (session_id, learner_id, started_at, skill_id) "
            "VALUES (?, ?, ?, ?)",
            (session_id, learner_id, _now(), skill_id)
        )
        self.conn.commit()
        return session_id

    def end_session(self, session_id: str) -> None:
        self.conn.execute(
            "UPDATE session SET ended_at = ? WHERE session_id = ?",
            (_now(), session_id)
        )
        self.conn.commit()

    # ---------- attempt ----------

    def save_attempt(self, session_id: str, learner_id: str, skill_id: str,
                     response: str, diagnosis_rule_id: str,
                     misconception_id: Optional[str],
                     hint_level: Optional[str],
                     error_type: str) -> str:
        attempt_id = "att_" + uuid.uuid4().hex[:12]
        self.conn.execute(
            "INSERT INTO attempt "
            "(attempt_id, session_id, learner_id, skill_id, timestamp, "
            " response, diagnosis_rule_id, misconception_id, hint_level, error_type) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (attempt_id, session_id, learner_id, skill_id, _now(),
             response, diagnosis_rule_id, misconception_id, hint_level, error_type)
        )
        self.conn.commit()
        return attempt_id

    # ---------- mastery ----------

    def get_mastery(self, learner_id: str, skill_id: str) -> dict:
        row = self.conn.execute(
            "SELECT * FROM mastery WHERE learner_id = ? AND skill_id = ?",
            (learner_id, skill_id)
        ).fetchone()
        if row is None:
            return {"learner_id": learner_id, "skill_id": skill_id,
                    "mastery_state": MasteryState.NOT_STARTED.value,
                    "sittings_passed": 0, "last_sitting_at": None}
        return dict(row)

    def recompute_mastery(self, learner_id: str, skill_id: str) -> str:
        """
        Apply the N08 mastery criteria to the stored attempts.

        3 correct out of 4 within a single sitting (session).
        2 sittings within 14 days.
        """
        # Get all sessions for this learner + skill, ordered by time
        sessions = self.conn.execute(
            "SELECT session_id, started_at FROM session "
            "WHERE learner_id = ? AND skill_id = ? "
            "ORDER BY started_at", (learner_id, skill_id)
        ).fetchall()

        sittings_passed = []
        for s in sessions:
            rows = self.conn.execute(
                "SELECT error_type FROM attempt "
                "WHERE session_id = ? ORDER BY timestamp", (s["session_id"],)
            ).fetchall()
            correct = sum(1 for r in rows if r["error_type"] == "none")
            total = len(rows)
            if total >= 4 and correct >= 3:
                sittings_passed.append(s["started_at"])

        # Compute state
        state = MasteryState.NOT_STARTED.value
        last_sitting = None
        if sittings_passed:
            # Check the 14-day window between the two most recent passed sittings
            if len(sittings_passed) >= 2:
                try:
                    t2 = datetime.fromisoformat(sittings_passed[-1])
                    t1 = datetime.fromisoformat(sittings_passed[-2])
                    if (t2 - t1) <= timedelta(days=14):
                        state = MasteryState.MASTERED.value
                    else:
                        state = MasteryState.NEAR_MASTERY.value
                except Exception:
                    state = MasteryState.NEAR_MASTERY.value
            else:
                state = MasteryState.NEAR_MASTERY.value
            last_sitting = sittings_passed[-1]
        else:
            any_attempt = self.conn.execute(
                "SELECT COUNT(*) as n FROM attempt "
                "WHERE learner_id = ? AND skill_id = ?",
                (learner_id, skill_id)
            ).fetchone()
            if any_attempt and any_attempt["n"] > 0:
                state = MasteryState.PRACTISING.value

        self.conn.execute(
            "INSERT INTO mastery "
            "(learner_id, skill_id, mastery_state, sittings_passed, "
            " last_sitting_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(learner_id, skill_id) DO UPDATE SET "
            "  mastery_state = excluded.mastery_state, "
            "  sittings_passed = excluded.sittings_passed, "
            "  last_sitting_at = excluded.last_sitting_at, "
            "  updated_at = excluded.updated_at",
            (learner_id, skill_id, state, len(sittings_passed),
             last_sitting, _now())
        )
        self.conn.commit()
        return state

    def close(self):
        self.conn.close()


# Import here to avoid circular import in tests
from .schemas import MasteryState


def open_store(path: Path) -> LearnerStore:
    return LearnerStore(path)
