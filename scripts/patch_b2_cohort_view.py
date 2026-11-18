"""patch_b2_cohort_view.py — swap generate_class_view for node-aware version."""
import re
import sys
import subprocess
from pathlib import Path

CLI = Path("scripts") / "cohort_view.py"
if not CLI.exists():
    print(f"ERROR: {CLI} not found")
    sys.exit(1)

src = CLI.read_text(encoding="utf-8")

if "def _render_from_node" in src:
    print("Already patched (found _render_from_node). Nothing to do.")
    sys.exit(0)

pat = re.compile(
    r"def generate_class_view\(learner_ids=None, days=30\):.*?(?=\ndef |\Z)",
    re.DOTALL,
)

NEW_CODE = '''def generate_class_view(learner_ids=None, days=30, use_node=None, node_id=None):
    """Generate class view.

    use_node:
      None  - auto: read node if fresh (<24h), else raw
      True  - force node (warns + falls back if stale/missing)
      False - force raw aggregation
    node_id: which node to read. Defaults to 'default_class'.
    """
    if use_node is True or (use_node is None and node_id):
        try:
            sys.path.insert(0, str(ROOT))
            from src.tutor.cohort_nodes import get_node, list_members
            target_node = node_id or "default_class"
            node = get_node(target_node)
            if node:
                computed = datetime.fromisoformat(node["computed_at"].replace("Z", "+00:00"))
                age = (datetime.now(timezone.utc) - computed).total_seconds()
                is_fresh = age < 86400
                if is_fresh:
                    members = list_members(target_node)
                    return _render_from_node(node, members, days)
                elif use_node is True:
                    print(f"  [node {target_node} is stale ({age/3600:.1f}h) - using raw]")
        except Exception as e:
            print(f"  [node read failed: {e} - falling back to raw]")

    ids, attempts_by, events_by, decisions_by = gather_cohort(learner_ids or [], days)

    if not ids:
        print("No learners found in database.")
        return None, None, None

    summaries = []
    for lid in ids:
        summaries.append(summarize_learner(
            lid, attempts_by.get(lid, []), events_by.get(lid, []),
            decisions_by.get(lid, []),
        ))

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    class_agg = aggregate_class(summaries, days)
    class_plan = build_class_plan(summaries, class_agg, days, data_version=ts)
    md = render_class_brief(class_plan)

    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    plan_path = PLANS_DIR / f"class_plan_{ts}.json"
    brief_path = REPORTS / f"class_brief_{ts}.md"

    plan_path.write_text(json.dumps(class_plan, indent=2), encoding="utf-8")
    brief_path.write_text(md, encoding="utf-8")

    return md, plan_path, brief_path


def _render_from_node(node, member_ids, days):
    """Render brief from node snapshot. O(1) path: one row read, one file write."""
    plan = {
        "plan_version": "1.3-node",
        "generated_at": node["computed_at"],
        "data_version": node["data_version"],
        "source": "node",
        "scope": "cohort",
        "window_days": days,
        "census_or_sample": "census",
        "class_size": node["learner_count"],
        "active_learners": node["active_count"],
        "inactive_learners": node["state_distribution"].get("inactive", 0),
        "summary": {
            "aggregate_accuracy": (
                node["pass_count"] / node["attempt_count"]
                if node["attempt_count"] else 0.0
            ),
            "aggregate_accuracy_ci": (0.0, 0.0),
            "census_or_sample": "census",
            "whole_class_issue_count": 0,
            "small_group_issue_count": 0,
            "needs_human_count": node["state_distribution"].get("needs_human", 0),
            "urgent_learner_count": node["state_distribution"].get("urgent", 0),
            "moderate_learner_count": node["state_distribution"].get("moderate", 0),
            "stable_learner_count": node["state_distribution"].get("stable", 0),
        },
        "conversation_summary": {
            "status": "not_yet_captured" if node.get("questions_asked") is None else "captured",
            "questions_asked": node.get("questions_asked"),
            "answers_given": node.get("answers_given"),
            "answer_acceptance_rate": node.get("answer_acceptance"),
            "improvement_after_answer": node.get("improvement_after"),
        },
        "class_wide_actions": [],
        "small_group_actions": [],
        "needs_human_learners": [],
        "individual_priorities": [],
        "stable_learners": [],
        "inactive_learners": [],
        "thresholds": node.get("threshold_snapshot", {}),
    }
    md = render_class_brief(plan)

    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    plan_path = PLANS_DIR / f"class_plan_{ts}.json"
    brief_path = REPORTS / f"class_brief_{ts}.md"
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    brief_path.write_text(md, encoding="utf-8")
    return md, plan_path, brief_path

'''

new_src, n = pat.subn(NEW_CODE, src, count=1)
if n == 0:
    print("FAIL: generate_class_view pattern didn't match")
    sys.exit(1)

CLI.write_text(new_src, encoding="utf-8")
print(f"OK - patched {CLI}")
print(f"  size: {len(src)} -> {len(new_src)} bytes")

# Compile check
r = subprocess.run([sys.executable, "-m", "py_compile", str(CLI)], capture_output=True)
if r.returncode == 0:
    print("  py_compile: PASS")
    sys.exit(0)
else:
    print(f"  py_compile: FAIL")
    print(r.stderr.decode())
    sys.exit(1)
