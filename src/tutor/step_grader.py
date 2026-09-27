from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CSV_DIR = ROOT / "data" / "processed" / "memo_step_marks"


def _load_one(path: Path, by_q: dict) -> None:
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            qid = row["question_id"].strip()
            if not qid:
                continue
            mg = (row.get("method_group") or "A").strip() or "A"
            by_q.setdefault(qid, []).append({
                "index": int(row["step_index"]),
                "desc": row["step_description"].strip(),
                "marks": int(row["marks"]),
                "memo_line": row["memo_line"].strip(),
                "forms": [x.strip() for x in row["acceptable_forms"].split("|") if x.strip()],
                "skill_id": row["skill_id"].strip(),
                "method_tag": row["method_tag"].strip(),
                "method_group": mg,
                "is_final": str(row.get("is_final", "false")).strip().lower() == "true",
            })


def load_steps(csv_path: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    by_q: dict[str, list[dict[str, Any]]] = {}
    if csv_path is not None:
        _load_one(csv_path, by_q)
    else:
        for p in sorted(CSV_DIR.glob("memo_step_marks_*.csv")):
            _load_one(p, by_q)
    for qid in by_q:
        by_q[qid].sort(key=lambda s: (s["method_group"], s["index"]))
    return by_q


_SEP = re.compile(r"\s*(?:,|\bor\b|;|\band\b)\s*")
_METHOD_MARKERS = re.compile(r"sqrt|\u00b1|\+/-|/2a|b2-4ac|b\^2|\\pm|\u221a|\u221a|\u00b1")


def _norm(s: str) -> str:
    s = s.lower().strip()
    s = s.replace("\u00d7", "*").replace("\u2212", "-").replace("\u2013", "-")
    s = s.replace("\u2234", " ").replace("\u2235", " ")
    s = re.sub(r"^\s*(therefore|so|hence|thus)\b\s*", "", s)
    s = re.sub(r"^=+\s*", "", s)  # strip leading '=' (continuation lines)
    s = s.replace("!=", "\u2260")  # != to ≠
    s = re.sub(r"(\d),(\d)", r"\1.\2", s)
    return s


def _tokens(s: str) -> list[str]:
    parts = _SEP.split(_norm(s))
    return sorted(re.sub(r"\s+", "", p) for p in parts if p.strip())


def _line_matches(line: str, forms: list[str], is_final: bool = False) -> bool:
    lt = _tokens(line)
    if not lt:
        return False
    lt_set = set(lt)
    for form in forms:
        ft = _tokens(form)
        if not ft:
            continue
        if is_final:
            if set(ft).issubset(lt_set):
                return True
        else:
            if ft == lt:
                return True
    return False


def _grade_group(steps, learner_lines):
    used: set[int] = set()
    results = []
    awarded = 0
    for step in steps:
        matched = False
        matched_line = None
        is_final = step.get("is_final", False)
        for i, line in enumerate(learner_lines):
            if i in used and not is_final:
                continue
            if _line_matches(line, step["forms"], is_final=is_final):
                matched = True
                matched_line = line
                if not is_final:
                    used.add(i)
                awarded += step["marks"]
                break
        results.append({
            "index": step["index"],
            "desc": step["desc"],
            "marks": step["marks"],
            "matched": matched,
            "learner_line": matched_line,
            "is_final": is_final,
        })
    return awarded, results, used


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

    groups: dict[str, list] = {}
    for s in steps:
        groups.setdefault(s["method_group"], []).append(s)

    best_awarded = -1
    best_results = None
    best_group = None
    for g_name, g_steps in groups.items():
        awarded, results, used = _grade_group(g_steps, learner_lines)
        if awarded > best_awarded:
            best_awarded = awarded
            best_results = results
            best_group = g_steps

    results = best_results
    awarded = best_awarded
    g_steps = best_group

    matched_values = {r["learner_line"] for r in results if r["matched"]}
    unmatched_lines = [ln for ln in learner_lines if ln not in matched_values]

    final_matched = any(r["matched"] and r["is_final"] for r in results)
    has_method_evidence = any(_METHOD_MARKERS.search(ln) for ln in unmatched_lines)

    for r in results:
        if r["matched"]:
            r["match_status"] = "MATCHED"
        elif final_matched and has_method_evidence:
            r["match_status"] = "UNCERTAIN"
        else:
            r["match_status"] = "NOT_MATCHED"

    total = sum(s["marks"] for s in g_steps)
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
