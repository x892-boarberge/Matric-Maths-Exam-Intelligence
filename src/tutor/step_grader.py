from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = ROOT / "data" / "processed" / "memo_step_marks" / "memo_step_marks_2023_P1.csv"


def load_steps(csv_path: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    path = csv_path or DEFAULT_CSV
    by_q: dict[str, list[dict[str, Any]]] = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            qid = row["question_id"].strip()
            by_q.setdefault(qid, []).append({
                "index": int(row["step_index"]),
                "desc": row["step_description"].strip(),
                "marks": int(row["marks"]),
                "memo_line": row["memo_line"].strip(),
                "forms": [x.strip() for x in row["acceptable_forms"].split("|") if x.strip()],
                "skill_id": row["skill_id"].strip(),
                "method_tag": row["method_tag"].strip(),
                "method_group": row.get("method_group", "A").strip(),
                "is_final": str(row.get("is_final", "false")).strip().lower() == "true",
            })
    for qid in by_q:
        by_q[qid].sort(key=lambda s: s["index"])
    return by_q


_SEP = re.compile(r"\s*(?:,|\bor\b|;|\band\b)\s*")
_METHOD_MARKERS = re.compile(r"sqrt|\u00b1|\+/-|/2a|b2-4ac|b\^2|\\pm|\u221a")


def _norm(s: str) -> str:
    s = s.lower().strip()
    s = s.replace("\u00d7", "*").replace("\u2212", "-").replace("\u2013", "-")
    s = s.replace("\u2234", " ").replace("\u2235", " ")
    s = re.sub(r"^\s*(therefore|so|hence|thus)\b\s*", "", s)
    return s


def _tokens(s: str) -> list[str]:
    parts = _SEP.split(_norm(s))
    return sorted(re.sub(r"\s+", "", p) for p in parts if p.strip())


def _line_matches(line: str, forms: list[str]) -> bool:
    lt = _tokens(line)
    if not lt:
        return False
    for form in forms:
        if _tokens(form) == lt:
            return True
    return False


def grade_steps(question_id: str, learner_lines: list[str], csv_path: Path | None = None) -> dict[str, Any]:
    steps_map = load_steps(csv_path)
    steps = steps_map.get(question_id, [])
    if not steps:
        return {
            "question_id": question_id,
            "total_marks": 0,
            "awarded_marks": 0,
            "steps": [],
            "feedback": "No step scheme for " + question_id,
        }
    used: set[int] = set()
    results = []
    awarded = 0

    for step in steps:
        matched = False
        matched_line = None
        for i, line in enumerate(learner_lines):
            if i in used:
                continue
            if _line_matches(line, step["forms"]):
                matched = True
                matched_line = line
                used.add(i)
                awarded += step["marks"]
                break
        results.append({
            "index": step["index"],
            "desc": step["desc"],
            "marks": step["marks"],
            "matched": matched,
            "learner_line": matched_line,
            "is_final": step.get("is_final", False),
        })

    # --- UNCERTAIN detection -------------------------------------------------
    # If the final step matched (answer is right) but there are leftover
    # learner lines containing method-signalling tokens (sqrt, +/-, formula
    # markers), the unmatched steps likely used an alternate valid method.
    final_matched = any(r["matched"] and r["is_final"] for r in results)
    unmatched_lines = [ln for i, ln in enumerate(learner_lines) if i not in used]
    has_method_evidence = any(_METHOD_MARKERS.search(ln) for ln in unmatched_lines)

    for r in results:
        if r["matched"]:
            r["match_status"] = "MATCHED"
        elif final_matched and has_method_evidence:
            r["match_status"] = "UNCERTAIN"
        else:
            r["match_status"] = "NOT_MATCHED"

    total = sum(s["marks"] for s in steps)
    missing = [r for r in results if r["match_status"] == "NOT_MATCHED"]
    uncertain = [r for r in results if r["match_status"] == "UNCERTAIN"]

    if not missing and not uncertain:
        feedback = "Full marks: %d/%d" % (awarded, total)
    elif uncertain and not missing:
        bits = ["cannot verify '%s' (alternate method used)" % u["desc"] for u in uncertain]
        feedback = "%d/%d. " % (awarded, total) + "; ".join(bits)
    else:
        bits = ["missed '%s' (%d mark)" % (m["desc"], m["marks"]) for m in missing]
        if uncertain:
            bits.append("cannot verify " + ", ".join("'%s'" % u["desc"] for u in uncertain))
        feedback = "%d/%d. " % (awarded, total) + "; ".join(bits)

    return {
        "question_id": question_id,
        "total_marks": total,
        "awarded_marks": awarded,
        "steps": results,
        "feedback": feedback,
    }


if __name__ == "__main__":
    demo = grade_steps("2023_P1_Q1.1.1", ["(x+4)(x-3)=0", "x=-4 or x=3"])
    print(demo["feedback"])
    for s in demo["steps"]:
        print(s)

    print()
    alt = grade_steps(
        "2023_P1_Q1.1.1",
        ["x = (-1 +/- sqrt(49))/2", "x = (-1 +/- 7)/2", "x = 3 or x = -4"],
    )
    print(alt["feedback"])
    for s in alt["steps"]:
        print(s)