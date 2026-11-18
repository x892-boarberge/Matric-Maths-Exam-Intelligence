"""analyst.py — deterministic query tools Tanaka calls during analysis.

Design principle: numbers are deterministic. The LLM chooses which tool
to call and interprets the result. Every function returns a dict with the
number AND the query that produced it, so the answer can be audited.

Cost transparency:
  find_anomaly  - O(snapshots)  - reads node history (cheap)
  compare       - O(1)          - two node snapshots (cheap)
  slice_learners - O(filtered)  - raw attempt scan (costly at scale)
  correlate     - O(learners)   - per-learner aggregation (costly at scale)

Functions named *_cheap can be called freely. Functions named *_scan
require explicit intent — they read raw data.

No LLM is invoked by any function in this module.
"""
import sqlite3
import statistics
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter

from .cohort_nodes import (
    DB, get_node, list_members, list_descendant_learners,
)


def _find_root():
    r = Path(".").resolve()
    for c in [r, *r.parents]:
        if (c / "src" / "tutor").is_dir():
            return c
    return r


ROOT = _find_root()


def _get_snapshots(node_id, limit=10, conn=None):
    """Internal: fetch N most recent snapshots of a node, newest first."""
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        close_after = True
    try:
        rows = conn.execute(
            "SELECT * FROM cohort_node WHERE node_id = ? "
            "ORDER BY computed_at DESC LIMIT ?",
            (node_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        if close_after:
            conn.close()


def list_snapshots(node_id, limit=20, conn=None):
    """List recent snapshots of a node, newest first. Returns list of dicts
    with data_version, computed_at, learner_count, active_count, attempt_count,
    pass_count, and source."""
    snaps = _get_snapshots(node_id, limit=limit, conn=conn)
    return [
        {
            "data_version": s["data_version"],
            "computed_at": s["computed_at"],
            "learner_count": s["learner_count"],
            "active_count": s["active_count"],
            "attempt_count": s["attempt_count"],
            "pass_count": s["pass_count"],
        }
        for s in snaps
    ]


def find_anomaly(node_id, metric="attempt_count", window=7, threshold=2.0, conn=None):
    """Detect if the latest value of `metric` is anomalous vs trailing baseline.

    Cost: O(window) - reads `window+1` snapshots, no raw scan.

    Returns:
      current, baseline_mean, baseline_std, z_score, is_anomaly, snapshots_used
      or {'error': ...} if insufficient history.
    """
    snaps = _get_snapshots(node_id, limit=window + 1, conn=conn)
    if len(snaps) < 3:
        return {
            "error": "insufficient history",
            "snapshots_found": len(snaps),
            "minimum_required": 3,
            "hint": "run rebuild_all_nodes.py multiple times to accumulate history",
        }

    latest = snaps[0]
    baseline = snaps[1:]
    values = [s.get(metric) for s in baseline if s.get(metric) is not None]
    if not values:
        return {"error": f"metric '{metric}' not found in baseline snapshots"}
    if latest.get(metric) is None:
        return {"error": f"metric '{metric}' not found in latest snapshot"}

    current = latest[metric]
    mean = statistics.mean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0

    if stdev == 0:
        z = float("inf") if current != mean else 0.0
    else:
        z = (current - mean) / stdev

    return {
        "node_id": node_id,
        "metric": metric,
        "current": current,
        "baseline_mean": round(mean, 3),
        "baseline_std": round(stdev, 3),
        "z_score": round(z, 3) if z != float("inf") else "inf",
        "is_anomaly": abs(z) > threshold if z != float("inf") else True,
        "threshold": threshold,
        "snapshots_used": len(values),
        "window": window,
    }


def compare(node_a, node_b, metric=None, conn=None):
    """Compare two nodes (or two snapshots via data_version strings).

    Cost: O(1) - reads up to two snapshot rows.

    If `metric` given, returns {a, b, delta} for that metric.
    Else returns per-metric diffs for learner/active/attempt/pass counts.
    """
    a = get_node(node_a, conn=conn)
    b = get_node(node_b, conn=conn)
    if not a or not b:
        return {
            "error": "node not found",
            "node_a_found": bool(a),
            "node_b_found": bool(b),
        }

    if metric:
        va = a.get(metric, 0) or 0
        vb = b.get(metric, 0) or 0
        return {
            "node_a": node_a,
            "node_b": node_b,
            "metric": metric,
            "a": va,
            "b": vb,
            "delta": vb - va,
            "pct_change": round((vb - va) / va * 100, 2) if va else None,
        }

    metrics = ("learner_count", "active_count", "attempt_count", "pass_count")
    diffs = {}
    for m in metrics:
        va = a.get(m, 0) or 0
        vb = b.get(m, 0) or 0
        diffs[m] = {
            "a": va,
            "b": vb,
            "delta": vb - va,
            "pct_change": round((vb - va) / va * 100, 2) if va else None,
        }
    return {"node_a": node_a, "node_b": node_b, "diffs": diffs}


def _learner_metrics(learner_ids, days=30, conn=None):
    """Internal: compute per-learner metrics from raw data.
    Returns dict learner_id -> {attempts, passes, accuracy, misconceptions, quits, skills}
    """
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        out = {}
        if not learner_ids:
            return out

        # Fetch attempts in chunks (500)
        attempts_by = defaultdict(list)
        for i in range(0, len(learner_ids), 500):
            chunk = learner_ids[i:i + 500]
            ph = ",".join("?" * len(chunk))
            for r in conn.execute(
                f"SELECT learner_id, error_type, misconception_id, skill_id "
                f"FROM attempt WHERE learner_id IN ({ph}) AND timestamp >= ?",
                (*chunk, since),
            ).fetchall():
                attempts_by[r[0]].append({
                    "error_type": r[1],
                    "misconception_id": r[2],
                    "skill_id": r[3],
                })

        # Fetch quit events
        quits_by = defaultdict(int)
        for i in range(0, len(learner_ids), 500):
            chunk = learner_ids[i:i + 500]
            ph = ",".join("?" * len(chunk))
            for r in conn.execute(
                f"SELECT learner_id, event_type FROM learner_events "
                f"WHERE learner_id IN ({ph}) AND timestamp >= ?",
                (*chunk, since),
            ).fetchall():
                if r[1] == "QUIT_AFTER_VARIANTS":
                    quits_by[r[0]] += 1

        for lid in learner_ids:
            atts = attempts_by.get(lid, [])
            n = len(atts)
            passes = sum(1 for a in atts
                         if str(a["error_type"] or "").lower() in ("none", "match"))
            mids = Counter(a["misconception_id"] for a in atts if a["misconception_id"])
            skills = set(a["skill_id"] for a in atts if a["skill_id"])
            out[lid] = {
                "attempts": n,
                "passes": passes,
                "accuracy": (passes / n) if n else 0.0,
                "misconception_count": sum(mids.values()),
                "top_misconception": mids.most_common(1)[0][0] if mids else None,
                "quits": quits_by.get(lid, 0),
                "skills": list(skills),
            }
        return out
    finally:
        if close_after:
            conn.close()


def slice_learners(node_id, where=None, days=30, conn=None):
    """Filter learners in a node by per-learner metrics, aggregate the result.

    Cost: O(filtered_attempts) - reads raw attempts for the node's members.

    where: dict metric -> (op, value), op in {'<','<=','>','>=','=='}
           valid metrics: attempts, passes, accuracy, misconception_count, quits
    Example: {'accuracy': ('<', 0.3), 'attempts': ('>=', 10)}

    Returns synthetic node dict (same shape as get_node) with an 'applied_filter'.
    """
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        members = list_descendant_learners(node_id, conn=conn)
        if not members:
            return {
                "node_id": node_id,
                "learner_count": 0,
                "error": "node has no members",
                "applied_filter": where or {},
            }

        metrics_by = _learner_metrics(members, days=days, conn=conn)

        def _match(lid, m):
            for key, (op, val) in (where or {}).items():
                actual = m.get(key)
                if actual is None:
                    return False
                if op == "<" and not actual < val: return False
                if op == "<=" and not actual <= val: return False
                if op == ">" and not actual > val: return False
                if op == ">=" and not actual >= val: return False
                if op == "==" and not actual == val: return False
            return True

        filtered = [lid for lid, m in metrics_by.items() if _match(lid, m)]
        if not filtered:
            return {
                "node_id": node_id,
                "learner_count": 0,
                "active_count": 0,
                "attempt_count": 0,
                "pass_count": 0,
                "applied_filter": where or {},
                "note": "no learners matched the filter",
            }

        attempts = sum(metrics_by[lid]["attempts"] for lid in filtered)
        passes = sum(metrics_by[lid]["passes"] for lid in filtered)

        return {
            "node_id": node_id,
            "learner_count": len(filtered),
            "active_count": sum(1 for lid in filtered if metrics_by[lid]["attempts"] > 0),
            "attempt_count": attempts,
            "pass_count": passes,
            "applied_filter": where or {},
            "learner_ids": sorted(filtered),
            "sample_size": len(filtered),
        }
    finally:
        if close_after:
            conn.close()


def correlate(node_id, metric_a, metric_b, days=30, conn=None):
    """Correlation between two per-learner metrics within a node.

    Cost: O(learners) - reads raw attempts for all node members.

    valid metrics: attempts, passes, accuracy, misconception_count, quits

    Returns Pearson r, n, and interpretation hint.
    """
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        members = list_descendant_learners(node_id, conn=conn)
        if len(members) < 3:
            return {
                "error": "insufficient learners",
                "n": len(members),
                "minimum_required": 3,
            }

        metrics_by = _learner_metrics(members, days=days, conn=conn)

        valid = [
            (lid, m) for lid, m in metrics_by.items()
            if m.get(metric_a) is not None and m.get(metric_b) is not None
        ]
        if len(valid) < 3:
            return {"error": "insufficient valid pairs", "n": len(valid)}

        xs = [m[metric_a] for _, m in valid]
        ys = [m[metric_b] for _, m in valid]
        n = len(xs)

        mx = sum(xs) / n
        my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        dx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
        dy = (sum((y - my) ** 2 for y in ys)) ** 0.5

        warnings_list = []
        if n < 10:
            warnings_list.append(f"small_sample: n={n} (recommend n>=10)")

        if dx == 0 or dy == 0:
            r = 0.0
            note = "zero variance in one metric — correlation undefined"
            warnings_list.append("zero_variance: one or both metrics constant")
        else:
            r = num / (dx * dy)
            note = ""
            if abs(r) < 0.1:
                note = "negligible correlation"
            elif abs(r) < 0.3:
                note = "weak correlation"
            elif abs(r) < 0.7:
                note = "moderate correlation"
            else:
                note = "strong correlation"
            if r > 0:
                note += " (positive)"
            elif r < 0:
                note += " (negative)"

        zeros_a = sum(1 for x in xs if x == 0)
        zeros_b = sum(1 for y in ys if y == 0)
        if zeros_a / n > 0.5:
            warnings_list.append(
                f"structural_artifact: {zeros_a}/{n} learners have {metric_a}=0"
            )
        if zeros_b / n > 0.5:
            warnings_list.append(
                f"structural_artifact: {zeros_b}/{n} learners have {metric_b}=0"
            )

        if warnings_list and abs(r) > 0.7 and dx > 0 and dy > 0:
            note = ("strong correlation (positive)" if r > 0
                    else "strong correlation (negative)")
            note += " BUT LIKELY SPURIOUS — see warnings"

        return {
            "node_id": node_id,
            "metric_a": metric_a,
            "metric_b": metric_b,
            "n": n,
            "pearson_r": round(r, 4),
            "note": note,
            "warnings": warnings_list,
            "caveat": (
                "Correlation is not causation. Any proposed causal claim "
                "requires a controlled test, not this number."
            ),
        }
    finally:
        if close_after:
            conn.close()
