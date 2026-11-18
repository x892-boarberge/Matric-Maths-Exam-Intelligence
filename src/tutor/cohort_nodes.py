"""cohort_nodes.py — precomputed cohort rollups for O(1) queries at any N.

B1: class level, single node, rollup works.
B2: hierarchy (school/district/province/national), cascade rebuild, node-read.

Append-only design: every rebuild inserts a new snapshot row with a new
data_version. Never mutates existing rows.

Levels (top-down):
  national
    province_<id>
      district_<id>
        school_<id>
          class_<id>
"""
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict, Counter


def _find_root():
    r = Path(".").resolve()
    for c in [r, *r.parents]:
        if (c / "src" / "tutor").is_dir():
            return c
    return r


ROOT = _find_root()
DB = ROOT / "data" / "learner_store" / "learners.db"


LEVEL_PARENT = {
    "class": "school",
    "school": "district",
    "district": "province",
    "province": "national",
    "national": None,
}


SCHEMA = """
CREATE TABLE IF NOT EXISTS cohort_meta (
    node_id    TEXT PRIMARY KEY,
    level      TEXT NOT NULL,
    parent_id  TEXT,
    name       TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (parent_id) REFERENCES cohort_meta(node_id)
);

CREATE TABLE IF NOT EXISTS cohort_node (
    node_id            TEXT NOT NULL,
    data_version       TEXT NOT NULL,
    learner_count      INTEGER NOT NULL DEFAULT 0,
    active_count       INTEGER NOT NULL DEFAULT 0,
    attempt_count      INTEGER NOT NULL DEFAULT 0,
    pass_count         INTEGER NOT NULL DEFAULT 0,
    state_distribution TEXT NOT NULL DEFAULT '{}',
    misconception_freq TEXT NOT NULL DEFAULT '{}',
    threshold_snapshot TEXT NOT NULL DEFAULT '{}',
    questions_asked    INTEGER,
    answers_given      INTEGER,
    answer_acceptance  REAL,
    improvement_after  REAL,
    computed_at        TEXT NOT NULL,
    computed_from      TEXT NOT NULL,
    notes              TEXT,
    PRIMARY KEY (node_id, data_version),
    FOREIGN KEY (node_id) REFERENCES cohort_meta(node_id)
);

CREATE INDEX IF NOT EXISTS idx_node_latest ON cohort_node(node_id, computed_at DESC);
CREATE INDEX IF NOT EXISTS idx_node_data_version ON cohort_node(data_version);

CREATE TABLE IF NOT EXISTS cohort_membership (
    learner_id TEXT NOT NULL,
    node_id    TEXT NOT NULL,
    joined_at  TEXT NOT NULL,
    left_at    TEXT,
    PRIMARY KEY (learner_id, node_id, joined_at),
    FOREIGN KEY (node_id) REFERENCES cohort_meta(node_id)
);

CREATE INDEX IF NOT EXISTS idx_membership_learner ON cohort_membership(learner_id, left_at);
CREATE INDEX IF NOT EXISTS idx_membership_node ON cohort_membership(node_id, left_at);
"""


def ensure_schema(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _data_version():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _rows_to_dicts(cur):
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def list_members(node_id, conn=None):
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        return [r[0] for r in conn.execute(
            "SELECT learner_id FROM cohort_membership "
            "WHERE node_id = ? AND left_at IS NULL ORDER BY learner_id",
            (node_id,),
        ).fetchall()]
    finally:
        if close_after:
            conn.close()


def list_descendant_learners(node_id, conn):
    """Return all learners in this node OR any descendant.
    Walks the parent_id tree downward.
    """
    node_ids = [node_id]
    frontier = [node_id]
    while frontier:
        cur = conn.execute(
            f"SELECT node_id FROM cohort_meta WHERE parent_id IN "
            f"({','.join('?' * len(frontier))})",
            tuple(frontier),
        ).fetchall()
        children = [r[0] for r in cur]
        if not children:
            break
        node_ids.extend(children)
        frontier = children

    placeholders = ",".join("?" * len(node_ids))
    learners = set()
    for r in conn.execute(
        f"SELECT DISTINCT learner_id FROM cohort_membership "
        f"WHERE node_id IN ({placeholders}) AND left_at IS NULL",
        tuple(node_ids),
    ).fetchall():
        learners.add(r[0])
    return sorted(learners)


def create_node(node_id, level, name, parent_id=None, conn=None):
    """Create a node's identity row. Idempotent — no-op if exists.
    Validates that parent's level matches the expected level ladder.
    Returns True if created, False if already existed.
    """
    if level not in LEVEL_PARENT:
        raise ValueError(f"Unknown level '{level}'. Expected one of {list(LEVEL_PARENT)}")
    expected_parent_level = LEVEL_PARENT[level]
    if expected_parent_level is None and parent_id is not None:
        raise ValueError(f"Level '{level}' must have parent_id=None, got '{parent_id}'")
    if expected_parent_level is not None and parent_id is None:
        raise ValueError(f"Level '{level}' must have parent_id at level '{expected_parent_level}'")

    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        existing = conn.execute(
            "SELECT 1 FROM cohort_meta WHERE node_id = ?", (node_id,)
        ).fetchone()
        if existing:
            return False
        if parent_id is not None:
            parent = conn.execute(
                "SELECT level FROM cohort_meta WHERE node_id = ?", (parent_id,)
            ).fetchone()
            if not parent:
                raise ValueError(f"Parent '{parent_id}' not found")
            if parent[0] != expected_parent_level:
                raise ValueError(
                    f"Parent '{parent_id}' has level '{parent[0]}', "
                    f"but level '{level}' expects parent level '{expected_parent_level}'"
                )
        conn.execute(
            "INSERT INTO cohort_meta (node_id, level, parent_id, name, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (node_id, level, parent_id, name, _now_iso()),
        )
        conn.commit()
        return True
    finally:
        if close_after:
            conn.close()


def add_member(learner_id, node_id, conn=None):
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        existing = conn.execute(
            "SELECT 1 FROM cohort_membership "
            "WHERE learner_id = ? AND node_id = ? AND left_at IS NULL",
            (learner_id, node_id),
        ).fetchone()
        if existing:
            return False
        conn.execute(
            "INSERT INTO cohort_membership (learner_id, node_id, joined_at) "
            "VALUES (?, ?, ?)",
            (learner_id, node_id, _now_iso()),
        )
        conn.commit()
        return True
    finally:
        if close_after:
            conn.close()


def rebuild_node(node_id, conn=None, days=30):
    """Recompute rollup for ANY node level. Aggregates from raw attempts
    for all descendant learners. Inserts a new snapshot. Returns (node_id, data_version).

    Raises ValueError if node doesn't exist.
    """
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        node_meta = conn.execute(
            "SELECT level, name FROM cohort_meta WHERE node_id = ?", (node_id,)
        ).fetchone()
        if not node_meta:
            raise ValueError(f"Node '{node_id}' not found.")

        members = list_descendant_learners(node_id, conn)
        learner_count = len(members)
        dv = _data_version()
        now = _now_iso()

        if learner_count == 0:
            conn.execute(
                "INSERT INTO cohort_node "
                "(node_id, data_version, learner_count, active_count, "
                "attempt_count, pass_count, state_distribution, misconception_freq, "
                "threshold_snapshot, computed_at, computed_from) "
                "VALUES (?, ?, 0, 0, 0, 0, '{}', '{}', '{}', ?, 'live')",
                (node_id, dv, now),
            )
            conn.commit()
            return (node_id, dv)

        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        placeholders = ",".join("?" * learner_count)

        cur = conn.execute(
            f"SELECT * FROM attempt WHERE learner_id IN ({placeholders}) "
            f"AND timestamp >= ? ORDER BY learner_id, timestamp",
            (*members, since),
        )
        attempts = _rows_to_dicts(cur)

        cur = conn.execute(
            f"SELECT * FROM learner_events WHERE learner_id IN ({placeholders}) "
            f"AND timestamp >= ? ORDER BY learner_id, timestamp",
            (*members, since),
        )
        events = _rows_to_dicts(cur)

        try:
            cur = conn.execute(
                f"SELECT * FROM mastery_decision WHERE learner_id IN ({placeholders}) "
                f"ORDER BY decided_at DESC",
                (*members,),
            )
            decisions = _rows_to_dicts(cur)
        except sqlite3.OperationalError:
            decisions = []

        import sys as _sys
        if str(ROOT) not in _sys.path:
            _sys.path.insert(0, str(ROOT))
        from scripts.cohort_view import summarize_learner, aggregate_class

        by_learner_attempts = defaultdict(list)
        for a in attempts:
            a2 = dict(a)
            a2["is_pass"] = str(a.get("error_type") or "").lower() in ("none", "match")
            by_learner_attempts[a["learner_id"]].append(a2)

        by_learner_events = defaultdict(list)
        for e in events:
            by_learner_events[e["learner_id"]].append(e)

        by_learner_decisions = defaultdict(list)
        for d in decisions:
            by_learner_decisions[d["learner_id"]].append(d)

        summaries = [
            summarize_learner(
                lid,
                by_learner_attempts.get(lid, []),
                by_learner_events.get(lid, []),
                by_learner_decisions.get(lid, []),
            )
            for lid in members
        ]
        agg = aggregate_class(summaries, days)

        active_count = agg["n_learners_active"]
        attempt_count = len(attempts)
        pass_count = sum(1 for a in attempts
                         if str(a.get("error_type") or "").lower() in ("none", "match"))

        state_dist = {
            "needs_human": len(agg["needs_human_learners"]),
            "urgent": len(agg["urgent_learners"]),
            "moderate": len(agg["moderate_learners"]),
            "stable": len(agg["stable_learners"]),
            "inactive": agg["n_learners_inactive"],
        }

        miscon_learners = defaultdict(set)
        miscon_errors = Counter()
        for lid, alist in by_learner_attempts.items():
            for a in alist:
                mid = a.get("misconception_id")
                if mid:
                    miscon_learners[mid].add(lid)
                    miscon_errors[mid] += 1

        miscon_freq = {
            mid: {"learners": len(learners), "errors": miscon_errors[mid]}
            for mid, learners in miscon_learners.items()
        }

        threshold_snapshot = dict(agg["thresholds"])
        threshold_snapshot["window_days"] = days

        conn.execute(
            "INSERT INTO cohort_node "
            "(node_id, data_version, learner_count, active_count, "
            "attempt_count, pass_count, state_distribution, misconception_freq, "
            "threshold_snapshot, computed_at, computed_from) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'live')",
            (
                node_id, dv, learner_count, active_count,
                attempt_count, pass_count,
                json.dumps(state_dist, sort_keys=True),
                json.dumps(miscon_freq, sort_keys=True),
                json.dumps(threshold_snapshot, sort_keys=True),
                now,
            ),
        )
        conn.commit()
        return (node_id, dv)
    finally:
        if close_after:
            conn.close()


def rebuild_class_node(node_id, conn=None, days=30):
    """Backward-compat wrapper. Calls rebuild_node. Level must be 'class'."""
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        row = conn.execute(
            "SELECT level FROM cohort_meta WHERE node_id = ?", (node_id,)
        ).fetchone()
        if not row:
            raise ValueError(f"Node '{node_id}' not found.")
        if row[0] != "class":
            raise ValueError(f"rebuild_class_node expects level='class', got '{row[0]}'")
        return rebuild_node(node_id, conn=conn, days=days)
    finally:
        if close_after:
            conn.close()


def rebuild_cascade(node_id, conn=None, days=30):
    """Rebuild node_id, then walk up the parent chain and rebuild each ancestor.
    Returns list of (node_id, data_version) in bottom-up order.
    """
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        results = []
        current = node_id
        while current:
            results.append(rebuild_node(current, conn=conn, days=days))
            row = conn.execute(
                "SELECT parent_id FROM cohort_meta WHERE node_id = ?", (current,)
            ).fetchone()
            current = row[0] if row else None
        return results
    finally:
        if close_after:
            conn.close()


def get_node(node_id, data_version=None, conn=None):
    """Read the latest (or specific) snapshot. Returns dict with parsed JSON, or None."""
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        close_after = True
    try:
        if data_version:
            cur = conn.execute(
                "SELECT * FROM cohort_node WHERE node_id = ? AND data_version = ?",
                (node_id, data_version),
            )
        else:
            cur = conn.execute(
                "SELECT * FROM cohort_node WHERE node_id = ? "
                "ORDER BY computed_at DESC LIMIT 1",
                (node_id,),
            )
        row = cur.fetchone()
        if not row:
            return None
        if hasattr(row, "keys"):
            d = dict(row)
        else:
            cols = [c[0] for c in cur.description]
            d = dict(zip(cols, row))
        for col in ("state_distribution", "misconception_freq", "threshold_snapshot"):
            try:
                d[col] = json.loads(d.get(col) or "{}")
            except json.JSONDecodeError:
                d[col] = {}
        return d
    finally:
        if close_after:
            conn.close()


def get_ancestors(node_id, conn=None):
    """Return list of ancestor node_ids from immediate parent up to root."""
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        ancestors = []
        current = node_id
        while True:
            row = conn.execute(
                "SELECT parent_id FROM cohort_meta WHERE node_id = ?", (current,)
            ).fetchone()
            if not row or not row[0]:
                break
            ancestors.append(row[0])
            current = row[0]
        return ancestors
    finally:
        if close_after:
            conn.close()