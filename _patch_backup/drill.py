"""
Drill engine — practice mode (v2, holistic rewrite).

Anchor → attempt → grade → save attempt → sibling on fail → loop → mastery.

Works identically for every topic. No answer leaks. No note spam.
"""
from __future__ import annotations

import json
import random
import uuid
from typing import Optional

from .schemas import Problem, WorkingSubmission, WorkingStep
from . import analogue_library
from .template_router import route_template
from .presentation_matcher import check_presentation, format_note
from .math_grader import grade, diagnose_wrong, MatchKind
from .step_grader import grade_steps as grade_steps_fn, grade_steps_inline
from .step_schemes import build_scheme
from .diagnosis import diagnose


# ============================================================
# LaTeX → plain text (MathQuill → memo-gradeable strings)
# ============================================================
import re as _re_latex


_LATEX_MAP = [
    (r"\left", ""), (r"\right", ""),
    (r"\times", "*"), (r"\div", "/"), (r"\cdot", "*"),
    (r"\pm", "+-"),
    (r"\leq", "<="), (r"\geq", ">="), (r"\neq", "!="),
    (r"\le", "<="), (r"\ge", ">="), (r"\ne", "!="),
    (r"\infty", "inf"), (r"\to", "->"),
    (r"\Rightarrow", "=>"), (r"\Leftarrow", "<="),
    (r"\therefore", "therefore"), (r"\because", "because"),
    (r"\alpha", "alpha"), (r"\beta", "beta"), (r"\gamma", "gamma"),
    (r"\theta", "theta"), (r"\pi", "pi"), (r"\sigma", "sigma"),
    (r"\Delta", "Delta"), (r"\Omega", "Omega"),
    (r"\sum", "sum"), (r"\int", "int"),
    (r"\sin", "sin"), (r"\cos", "cos"), (r"\tan", "tan"),
    (r"\log", "log"), (r"\ln", "ln"),
    (r"\,", " "), (r"\;", " "), (r"\!", ""), (r"\ ", " "),
]


# ============================================================
# Corpus + intervention loaders (activated)
# ============================================================
import csv as _csv_mod

_CORPUS_CACHE = None
_INTERVENTIONS_CACHE = None


def _load_diagnostic_corpus():
    """Read diagnostic_errors_with_skill.csv into {skill_id: {...}} once."""
    global _CORPUS_CACHE
    if _CORPUS_CACHE is not None:
        return _CORPUS_CACHE
    from pathlib import Path as _P
    root = _P(__file__).resolve().parents[2]
    path = root / "data" / "processed" / "diagnostics" / "diagnostic_errors_with_skill.csv"
    idx = {}
    if not path.exists():
        _CORPUS_CACHE = idx
        return idx
    try:
        with path.open(encoding="utf-8", errors="ignore", newline="") as f:
            reader = _csv_mod.DictReader(f)
            for row in reader:
                skill = (row.get("skill_id") or "").strip()
                if not skill:
                    continue
                cls   = (row.get("error_class") or "general").strip().lower()
                year  = (row.get("year") or "").strip()
                text  = (row.get("error_text") or "").strip()
                sug   = (row.get("suggestion_text") or "").strip()
                entry = idx.setdefault(skill, {
                    "counts": {},
                    "years": set(),
                    "sample_text": "",
                    "sample_year": "",
                    "suggestions": [],
                    "all_samples": [],
                })
                entry["counts"][cls] = entry["counts"].get(cls, 0) + 1
                if year:
                    entry["years"].add(year)
                if text:
                    entry.setdefault("all_samples", []).append({
                        "text": text[:400],
                        "year": year,
                        "subquestion_ref": (row.get("subquestion_ref") or "").strip(),
                        "question_number": (row.get("question_number") or "").strip(),
                    })
                if not entry["sample_text"] and text:
                    entry["sample_text"] = text[:400]
                    entry["sample_year"] = year
                if sug and len(entry["suggestions"]) < 3:
                    entry["suggestions"].append(sug[:200])
    except Exception:
        pass
    _CORPUS_CACHE = idx
    return idx


_SHAPE_KEYWORDS = {
    # template shape → words we look for in the DBE error text
    "factorable": ("factor", "bracket", "expand", "roots", "product", "sum"),
    "formula":    ("formula", "discriminant", "substitut", "b^2", "b²", "standard form"),
    "complete_square": ("complet", "square"),
    "inequality": ("inequal", "number line", "interval", "direction"),
}


def _score_sample(sample, shape, anchor_subq=""):
    """Score a corpus sample against a shape. Higher = better match.

    Priority (strongest first):
      1. subquestion_ref matches the anchor's subquestion
      2. keyword hits in the text for this shape
      3. nothing → score 0
    """
    if not sample:
        return 0
    score = 0
    ref = (sample.get("subquestion_ref") or "").strip()
    if anchor_subq and ref and ref == anchor_subq:
        score += 10
    elif anchor_subq and ref and ref.startswith(anchor_subq.split(".")[0] + "."):
        score += 4

    text = sample.get("text", "") or ""
    low = text.lower()
    if shape in _SHAPE_KEYWORDS:
        kws = _SHAPE_KEYWORDS[shape]
        score += sum(1 for kw in kws if kw.lower() in low)

    # Penalise samples that clearly belong to a *different* shape
    if shape == "factorable":
        # formula-style samples should be penalised
        if "quadratic formula" in low or "b^2" in low or "b²" in low:
            score -= 5
    elif shape == "formula":
        # factor-style samples should be penalised
        if "factoris" in low or "factor" in low and "formula" not in low:
            score -= 3
    return score


def _shape_for_template(template_id):
    """Map a template_id to a shape key used by corpus filtering."""
    if not template_id:
        return None
    if "standard_factorable" in template_id or "factored" in template_id:
        return "factorable"
    if "quadratic_formula" in template_id:
        return "formula"
    if "quadratic_inequality" in template_id:
        return "inequality"
    if "complete" in template_id:
        return "complete_square"
    return None


def corpus_for_skill(skill_id, shape=None, anchor_subq=""):
    """Return a compact corpus summary. If `shape` is given, prefer DBE
    samples whose text actually matches that shape (e.g. factorable vs
    formula). Falls back to the global top when the shape filter is empty.
    """
    idx = _load_diagnostic_corpus()
    entry = idx.get(skill_id)
    if not entry:
        return None
    counts = entry["counts"]
    if not counts:
        return None

    # If we have samples for this skill, choose one that matches the shape
    # AND (when possible) the anchor's subquestion.
    samples = entry.get("all_samples") or []
    if samples and shape and shape in _SHAPE_KEYWORDS:
        ranked = sorted(
            samples,
            key=lambda s: _score_sample(s, shape, anchor_subq),
            reverse=True,
        )
        best_score = _score_sample(ranked[0], shape, anchor_subq) if ranked else 0
        if best_score >= 1:
            chosen = ranked[0]
        else:
            chosen = None  # no confident match — do not quote anything
    elif samples and not shape:
        # no shape info — use the first stored sample
        chosen = samples[0]
    else:
        chosen = {"text": entry.get("sample_text", ""),
                  "year": entry.get("sample_year", "")}

    top_class = max(counts, key=counts.get)
    out = {
        "total_errors":   sum(counts.values()),
        "top_error_class": top_class,
        "top_error_count": counts[top_class],
        "class_counts":    counts,
        "years_span":      f"{min(entry['years'])}–{max(entry['years'])}" if entry["years"] else "",
        "years_count":     len(entry["years"]),
        "shape":           shape or "",
    }
    if chosen and chosen.get("text"):
        out["sample_text"] = chosen["text"]
        out["sample_year"] = chosen.get("year", "")
        out["sample_subquestion_ref"] = chosen.get("subquestion_ref", "")
    # if no shape-matched sample exists, we simply omit the sample entirely.
    return out


def _load_interventions():
    """Load the N08 intervention library once via the existing loader."""
    global _INTERVENTIONS_CACHE
    if _INTERVENTIONS_CACHE is not None:
        return _INTERVENTIONS_CACHE
    try:
        from .n08_loader import load_n08_library
        lib = load_n08_library()
        _INTERVENTIONS_CACHE = lib
    except Exception:
        _INTERVENTIONS_CACHE = None
    return _INTERVENTIONS_CACHE


_MISCONCEPTION_ALIASES = {
    "M_ALG_SIGN_FLIP_FACTOR":  "M_SIGN_ERROR_FACTORISATION",
    "M_ALG_STANDARD_FORM":     "M_SIGN_ERROR_FACTORISATION",
    "M_ALG_DISCRIMINANT_SIGN": "M_SIGN_ERROR_FACTORISATION",
}


def intervention_for_misconception(misconception_id):
    """Return {pattern, intervention_id} or None. Falls back to aliases."""
    if not misconception_id:
        return None
    lib = _load_interventions()
    if lib is None:
        return None

    def _lookup(mid):
        try:
            return lib.by_misconception.get(mid)
        except Exception:
            return None

    entry = _lookup(misconception_id)
    if not entry:
        alias = _MISCONCEPTION_ALIASES.get(misconception_id)
        if alias:
            entry = _lookup(alias)
    if not entry:
        # keyword fallback: try to match a prefix / substring
        try:
            for mid, e in lib.by_misconception.items():
                if mid.split("_", 2)[:2] == misconception_id.split("_", 2)[:2]:
                    entry = e
                    break
        except Exception:
            entry = None
    if not entry:
        return None
    return {
        "intervention_id":      entry.get("intervention_id", ""),
        "intervention_pattern": entry.get("intervention_pattern", ""),
        "matched_misconception": entry.get("misconception_id", misconception_id),
    }


def _latex_to_plain(s: str) -> str:
    """Turn MathQuill-style LaTeX into text the memo grader can compare."""
    if not s:
        return s
    out = s

    # \frac{a}{b}  →  (a)/(b)   — repeat for nested fractions
    frac = _re_latex.compile(r"\\frac\{([^{}]*)\}\{([^{}]*)\}")
    while frac.search(out):
        out = frac.sub(r"(\1)/(\2)", out)

    # \sqrt{a}  or  \sqrt[n]{a}  →  sqrt(a)
    rt = _re_latex.compile(r"\\sqrt(?:\[[^\]]*\])?\{([^{}]*)\}")
    while rt.search(out):
        out = rt.sub(r"sqrt(\1)", out)

    # ^{x} → ^x  and  _{x} → _x
    out = _re_latex.sub(r"\^\{([^{}]*)\}", r"^\1", out)
    out = _re_latex.sub(r"_\{([^{}]*)\}", r"_\1", out)

    # \text{...} → the text itself
    out = _re_latex.sub(r"\\text\{([^{}]*)\}", r"\1", out)

    # \hat{A} → A_hat  ·  \bar{x} → x_bar
    out = _re_latex.sub(r"\\hat\{([^{}]*)\}", r"\1_hat", out)
    out = _re_latex.sub(r"\\bar\{([^{}]*)\}", r"\1_bar", out)

    # simple command replacements
    for pat, rep in _LATEX_MAP:
        out = out.replace(pat, rep)

    # collapse whitespace
    out = _re_latex.sub(r"\s+", " ", out).strip()
    return out


SITTING_SIZE = 5
PASS_THRESHOLD = 4


# ============================================================
# Line provider — CLI uses input(); web server sets a callback
# ============================================================
_LINE_PROVIDER = None



# ============================================================
# Character-level normaliser — makes Unicode math match ASCII
# ============================================================
_UNICODE_FIX = {
    "\u2212": "-",   # − minus sign
    "\u2013": "-",   # – en dash
    "\u2014": "-",   # — em dash
    "\u00d7": "*",   # × multiplication
    "\u00f7": "/",   # ÷ division
    "\u2264": "<=",  # ≤
    "\u2265": ">=",  # ≥
    "\u2260": "!=",  # ≠
    "\u2192": "->",  # →
    "\u21d2": "=>",  # ⇒
    "\u2234": "therefore",
    "\u2235": "because",
    "\u03b1": "alpha", "\u03b2": "beta", "\u03b8": "theta",
    "\u03c0": "pi",    "\u03c3": "sigma", "\u221e": "inf",
    "\u221a": "sqrt",
}


def _normalise(s: str) -> str:
    """Flatten to a canonical form the memo grader can compare."""
    if not s:
        return ""
    out = s
    for k, v in _UNICODE_FIX.items():
        out = out.replace(k, v)
    # collapse whitespace, lowercase, drop decorative spaces around symbols
    import re as _rn
    out = _rn.sub(r"\s+", "", out).lower()
    out = out.replace("or", "|")
    return out


def set_line_provider(fn):
    """When set, _collect_working calls fn(prompt) instead of input(prompt)."""
    global _LINE_PROVIDER
    _LINE_PROVIDER = fn


def _read_line(prompt: str) -> str:
    if _LINE_PROVIDER is not None:
        return _LINE_PROVIDER(prompt)
    return input(prompt)


# ============================================================
# Pool helpers
# ============================================================
def _template_path_for_anchor(problem_id: str):
    """Map an anchor problem_id to its DBE template JSON path."""
    from pathlib import Path as _P
    _root = _P(__file__).resolve().parents[2]
    tdir = _root / "data" / "processed" / "tutor" / "question_templates"
    parts = str(problem_id).split("_")
    if len(parts) < 3:
        return None
    year, paper = parts[0], parts[1]
    qpart = parts[2].split(".")[0]  # 'Q1.1.1' -> 'Q1'
    p = tdir / f"template_{year}_{paper}_{qpart}.json"
    return p if p.exists() else None


def _anchor_template_metadata(problem_id: str):
    """Return the template dict for an anchor problem_id, or None."""
    tp = _template_path_for_anchor(problem_id)
    if not tp:
        return None
    try:
        import json as _json
        return _json.loads(tp.read_text(encoding="utf-8"))
    except Exception:
        return None


def _try_get_anchor_diagram_image(problem_id: str):
    """Return the parent paper's page-image path for this anchor,
    if the template carries one."""
    t = _anchor_template_metadata(problem_id)
    if not t:
        return None
    img = t.get("diagram_image")
    if not img:
        return None
    from pathlib import Path as _P
    root = _P(__file__).resolve().parents[2]
    p = root / img
    return str(p) if p.exists() else None


def _try_render_anchor_diagram(problem_id: str):
    """Preferred: parent page image. Fallback: rendered spec."""
    t = _anchor_template_metadata(problem_id)
    if not t:
        return None
    d = t.get("diagram")
    s = t.get("diagram_spec")
    page = _try_get_anchor_diagram_image(problem_id)
    if page:
        return page
    if d and s:
        try:
            from pathlib import Path as _P
            from tutor import diagram_dispatcher as _disp
            root = _P(__file__).resolve().parents[2]
            cache = root / "data" / "processed" / "diagrams" / "drill_cache"
            cache.mkdir(parents=True, exist_ok=True)
            safe = str(problem_id).replace(".", "_").replace("/", "_")
            out = cache / f"{safe}.png"
            _disp.render_diagram(d, out_path=out, **s)
            return str(out)
        except Exception:
            pass
    return None


_SKILL_DIAGRAM_INDEX = None


def _load_skill_diagram_index():
    global _SKILL_DIAGRAM_INDEX
    if _SKILL_DIAGRAM_INDEX is None:
        import json as _json
        from pathlib import Path as _P
        root = _P(__file__).resolve().parents[2]
        p = root / "data" / "processed" / "tutor" / "skill_diagram_index.json"
        _SKILL_DIAGRAM_INDEX = (
            _json.loads(p.read_text(encoding="utf-8"))
            if p.exists() else {}
        )
    return _SKILL_DIAGRAM_INDEX


def _reference_diagram_for_skill(skill_id: str):
    """Return a parent page image path for a variant of this skill."""
    index = _load_skill_diagram_index()
    entries = index.get(skill_id, [])
    if not entries:
        return None
    from pathlib import Path as _P
    root = _P(__file__).resolve().parents[2]
    for e in entries:
        img = e.get("image")
        if not img:
            continue
        p = root / img
        if p.exists():
            return str(p)
    return None


def _load_pool(template_id: str):
    return analogue_library.POOL.get(template_id, [])


def _extract_expected(analogue: dict) -> str:
    steps = analogue.get("steps", [])
    if not steps:
        return ""
    last = str(steps[-1])
    if ":" in last:
        last = last.split(":", 1)[1]
    return last.strip()


def _analogue_to_problem(analogue: dict, template_id: str, skill_id: str) -> Problem:
    expected = _extract_expected(analogue)
    scheme = build_scheme(template_id, analogue, expected)
    return Problem(
        problem_id=f"drill_{template_id}_{uuid.uuid4().hex[:6]}",
        skill_id=skill_id,
        topic="",
        subtopic="",
        structure_type="routine_calculation",
        prompt=analogue["problem"],
        expected_answer=expected,
        topic_v2=None,
        step_scheme=scheme,
    )


# ============================================================
# Working input
# ============================================================
def _collect_working(q_num: int, total: int):
    steps = []
    print()
    print(f"  Question {q_num} of {total}")
    print("  Show your working. 'done' to submit, 'help' for a worked example,")
    print("  'next' to skip this question, 'end' to finish this sitting,")
    print("  'menu' to pick a different topic, 'q' to quit the tutor.")
    print()
    while True:
        idx = len(steps) + 1
        try:
            raw = _read_line(f"    Line {idx}: ").rstrip()
        except (EOFError, KeyboardInterrupt):
            return None
        s = raw.strip()
        if not s:
            continue
        low = s.lower()
        if low in ("q", "quit", "exit"):
            return None
        if low in ("next", "skip", "n"):
            return "NEXT"
        if low in ("menu", "topics", "back", "topics:"):
            return "MENU"
        if low in ("end", "stop", "enough"):
            return "END"
        if low in ("help", "answer", "hint"):
            return "HELP"
        if low in ("more", "another"):
            return "MORE"
        if low in ("done", "submit"):
            if not steps:
                print("    (type at least one line, 'help', or 'q' to quit)")
                continue
            return WorkingSubmission(
                steps=[WorkingStep(index=i + 1, raw_text=t) for i, t in enumerate(steps)],
                source="typed",
                final_answer=steps[-1],
            )
        if low.startswith("answer:"):
            ans = s[len("answer:"):].strip()
            if ans:
                return WorkingSubmission(
                    steps=[WorkingStep(index=1, raw_text=ans)],
                    source="typed",
                    final_answer=ans,
                )
        steps.append(s)


# ============================================================
# Sibling example — same template, different variant
# ============================================================
def _show_sibling(pool, shown_keys):
    candidates = [a for a in pool if analogue_library.analogue_key(a) not in shown_keys]
    if not candidates:
        candidates = pool
    if not candidates:
        return None
    ex = random.choice(candidates)
    print()
    print("  Let's look at a similar one first.")
    print()
    print(f"    Problem: {ex['problem']}")
    for s in ex.get("steps", []):
        print(f"      {s}")
    if ex.get("note"):
        print(f"    Note: {ex['note']}")
    shown_keys.add(analogue_library.analogue_key(ex))
    return ex




def _pick_sibling_for_anchor(anchor, exclude_keys=None):
    """Return one worked variant for this anchor's template, or None.

    Used by the web path: when the learner gets it wrong, they see a
    fully worked sibling problem from the same template — problem,
    steps, and note — exactly as the CLI does.
    """
    try:
        template_id = route_template(anchor.skill_id, anchor.prompt)
        if not template_id:
            return None
        pool = _load_pool(template_id)
        if not pool:
            return None
        exclude = exclude_keys or set()
        candidates = [a for a in pool
                      if analogue_library.analogue_key(a) not in exclude]
        if not candidates:
            candidates = pool
        import random as _r
        ex = _r.choice(candidates)
        return {
            "problem": ex.get("problem", ""),
            "steps":   list(ex.get("steps", [])),
            "note":    ex.get("note", ""),
            "key":     analogue_library.analogue_key(ex),
        }
    except Exception:
        return None


# ============================================================
# Warm diagnosis message
# ============================================================
def _speak_diagnosis(kind: str):
    if kind == "sign_flip":
        print()
        print("  I see the shape of the working. The sign on one root looks")
        print("  flipped — the number is right, the sign isn't. Worth a look.")
    elif kind == "partial":
        print()
        print("  One of the roots is right. The other is missing or different.")
        print("  Both matter for this question.")
    else:
        print()
        print("  There's something off. Let's look at a similar one together.")


# ============================================================
# Record attempt into the store
# ============================================================
def _save_attempt(store, session_id, learner_id, skill_id,
                  response, rule_id, error_type,
                  misconception_id=None, hint_level=None):
    try:
        store.save_attempt(
            session_id=session_id,
            learner_id=learner_id,
            skill_id=skill_id,
            response=response[:500],
            diagnosis_rule_id=rule_id or "",
            misconception_id=misconception_id,
            hint_level=hint_level,
            error_type=error_type,
        )
    except Exception:
        pass


# ============================================================
# Mastery summary
# ============================================================
def _speak_mastery(skill_id, template_id, questions_correct, total_questions,
                   topic_label, questions_skipped=0):
    print()
    print("=" * 60)
    print(f"  Drill complete — {template_id}")
    line = f"  Correct: {questions_correct}/{total_questions}"
    if questions_skipped:
        line += f"   (skipped: {questions_skipped})"
    print(line)
    print("=" * 60)
    print()
    if questions_correct >= PASS_THRESHOLD:
        print(f"  The method held together across the variants, {topic_label}.")
        print("  That is the point of the drill.")
    elif questions_skipped and questions_correct > 0:
        print(f"  You moved on from {questions_skipped} of them. That is your call.")
        print("  Come back to this pattern when you feel like it.")
    else:
        print(f"  You got {questions_correct} of {total_questions}. That is close.")
        print("  One more sitting and the method will lock in.")
    print()
    print("  Disclaimer — practice is one thing, exam is another. In the exam")
    print("  you'll be marked strictly against the DBE memo. Same method, but")
    print("  line by line, in their format.")


import re as _re


def _corpus_id_to_memo_id(problem_id: str) -> str:
    """2023_P1_Q1_1.1.1 -> 2023_P1_Q1.1.1 (drop underscore + repeated digit)."""
    if not problem_id or problem_id.startswith("drill_"):
        return ""
    return _re.sub(r"Q(\d+)_\1\.", r"Q\1.", problem_id)


def _step_feedback(problem_id: str, learner_lines: list[str]) -> dict | None:
    """Return step-grader result for the anchor, or None if not applicable."""
    memo_id = _corpus_id_to_memo_id(problem_id)
    if not memo_id:
        return None
    try:
        r = grade_steps_fn(memo_id, learner_lines)
    except Exception:
        return None
    if r["total_marks"] == 0:
        return None
    return r


def _print_step_feedback(result: dict) -> None:
    """Format the step result for the CLI."""
    awarded = result["awarded_marks"]
    total = result["total_marks"]
    steps = result["steps"]

    missing = [s for s in steps if s.get("match_status") == "NOT_MATCHED"]
    uncertain = [s for s in steps if s.get("match_status") == "UNCERTAIN"]

    if not missing and not uncertain:
        print(f"  Full method shown — memo awards {total}/{total}.")
        return

    print(f"  Memo would award {awarded}/{total}.")
    for s in missing:
        mark_word = "mark" if s["marks"] == 1 else "marks"
        print(f"    You skipped: {s['desc']}  ({s['marks']} {mark_word})")
        forms = s.get("forms") or []
        if forms:
            print(f"      The memo would show:   {forms[0]}")
    for u in uncertain:
        print(f"    Cannot verify: {u['desc']}")
    print("    (In the exam, markers award marks per step.)")


# ============================================================
# Auto-outcome measurement
# ============================================================
def _close_open_interventions(store, learner_id, skill_id, step_result,
                               current_qid, session_id):
    """Record whether each open intervention is now satisfied."""
    try:
        open_invs = store.interventions.list_open(learner_id, skill_id)
    except Exception:
        return
    if not open_invs:
        return

    step_status = {}
    if step_result is not None:
        for s in step_result.get("steps", []):
            step_status[int(s.get("index", -1))] = s.get("match_status")

    for inv in open_invs:
        try:
            ctx = json.loads(inv.get("context") or "{}")
        except Exception:
            ctx = {}
        step_index = ctx.get("step_index")

        if step_index is not None and int(step_index) in step_status:
            status = step_status[int(step_index)]
            if status == "MATCHED":
                result = "improved"
            elif status == "NOT_MATCHED":
                result = "unchanged"
            else:
                continue
            evidence = {
                "measured_via": "step_grader",
                "step_index": int(step_index),
                "current_qid": current_qid,
                "session_id": session_id,
            }
        else:
            result = "improved"
            evidence = {
                "measured_via": "answer_match",
                "current_qid": current_qid,
                "session_id": session_id,
            }

        try:
            store.interventions.record_outcome(
                intervention_id=inv["intervention_id"],
                learner_id=learner_id,
                result=result,
                measurement_kind="follow_up",
                evidence=evidence,
            )
        except Exception:
            pass


# ============================================================
# Main drill
# ============================================================
def run(engine, store, learner_id, session_id, anchor, logger=None,
        interactive_input=True, sitting_number=1):
    template_id = route_template(anchor.skill_id, anchor.prompt)
    if template_id is None:
        print(f"  (No template for skill {anchor.skill_id} — skipping.)")
        return {"sittings_passed": 0, "correct": 0, "total": 0, "exit_reason": "no_template"}

    pool = _load_pool(template_id)
    if not pool:
        print(f"  (No variants for {template_id} — skipping.)")
        return {"sittings_passed": 0, "correct": 0, "total": 0, "exit_reason": "empty_pool"}

    topic_label = anchor.topic or anchor.skill_id.split(".")[0]

    print()
    print("=" * 60)
    print(f"  Drill: {anchor.skill_id}")
    if sitting_number > 1:
        print(f"  Sitting {sitting_number}")
    print(f"  Template: {template_id}  ({len(pool)} variants)")
    print("=" * 60)

    sequence = []
    anchor_ok = bool(anchor.expected_answer and anchor.expected_answer.strip())
    if anchor_ok:
        sequence.append({"type": "anchor", "problem": anchor})

    cycle = pool.copy()
    random.shuffle(cycle)
    cycle_idx = 0
    shown_variant_keys = set()

    while len(sequence) < SITTING_SIZE:
        if cycle_idx >= len(cycle):
            cycle_idx = 0
            random.shuffle(cycle)
        analogue = cycle[cycle_idx]
        cycle_idx += 1
        key = analogue_library.analogue_key(analogue)
        if key in shown_variant_keys:
            continue
        shown_variant_keys.add(key)
        sequence.append({
            "type": "variation",
            "problem": _analogue_to_problem(analogue, template_id, anchor.skill_id),
        })

    questions_correct = 0
    questions_first_try = 0
    questions_skipped = 0
    questions_attempted = 0
    total_attempts = 0
    shown_note_ids = set()
    shown_sibling_keys = set()

    for i, item in enumerate(sequence, 1):
        drill_problem = item["problem"]

        print()
        print("-" * 60)
        if item["type"] == "anchor":
            _diag = _try_render_anchor_diagram(drill_problem.problem_id)
            if _diag:
                print(f"  Diagram: {_diag}")
                print()
        else:
            _ref = _reference_diagram_for_skill(drill_problem.skill_id)
            if _ref:
                print(f"  Reference diagram: {_ref}")
                print("  (Same shape, different numbers.)")
                print()
        print(f"  Problem: {drill_problem.prompt}")
        if item["type"] == "anchor":
            print("  (This is the original question you picked.)")
        print("-" * 60)

        attempts_on_this_q = 0
        while True:
            if not interactive_input:
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": total_attempts, "exit_reason": "non_interactive"}

            submission = _collect_working(i, SITTING_SIZE)

            if submission is None:
                _close_early(questions_correct, i - 1)
                _try_recompute_mastery(store, learner_id, anchor.skill_id)
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": total_attempts, "exit_reason": "quit"}

            if submission == "MENU":
                print()
                print("  Back to the topic menu. Pick anything you like.")
                _try_recompute_mastery(store, learner_id, anchor.skill_id)
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": questions_attempted,
                        "skipped": questions_skipped,
                        "exit_reason": "menu"}

            if submission == "END":
                questions_attempted += 1
                print()
                print("  Good. Free will beats force. Ending the sitting here.")
                _try_recompute_mastery(store, learner_id, anchor.skill_id)
                print()
                print(f"  This sitting: {questions_correct} correct, "
                      f"{questions_skipped} skipped, "
                      f"{questions_attempted - questions_correct - questions_skipped} left.")
                return {"sittings_passed": 0, "correct": questions_correct,
                        "total": questions_attempted,
                        "skipped": questions_skipped,
                        "exit_reason": "learner_end"}

            if submission == "NEXT":
                questions_skipped += 1
                questions_attempted += 1
                print()
                print("  Moving on. You can come back to this pattern any time.")
                break

            if submission == "HELP" or submission == "MORE":
                _show_sibling(pool, shown_sibling_keys)
                print()
                print("  Try the question again when ready — or type 'next' to move on.")
                continue

            from . import slash_commands as _sc

            _steps = getattr(submission, "steps", None) or []
            _first_raw = ""
            if _steps and hasattr(_steps[0], "raw_text"):
                _first_raw = _steps[0].raw_text.strip()

            if _sc.is_help(_first_raw) and len(_steps) == 1:
                print(_sc.HELP_TEXT)
                continue

            for _s in _steps:
                if hasattr(_s, "raw_text"):
                    _s.raw_text = _sc.expand(_s.raw_text)

            attempts_on_this_q += 1
            total_attempts += 1
            learner_text = submission.joined()

            result = grade(learner_text, drill_problem.expected_answer)

            if result.kind == MatchKind.MATCH:
                questions_correct += 1
                questions_attempted += 1
                if attempts_on_this_q == 1:
                    questions_first_try += 1

                _save_attempt(store, session_id, learner_id, anchor.skill_id,
                              learner_text, f"D_{result.matcher}", "none")

                print()
                print(f"  ✓ Correct.  ({questions_correct}/{i} this sitting)")

                learner_lines_for_steps = [s.raw_text for s in submission.steps]
                step_result = _step_feedback(
                    drill_problem.problem_id,
                    learner_lines_for_steps,
                )
                if step_result is None and getattr(drill_problem, "step_scheme", None):
                    try:
                        step_result = grade_steps_inline(
                            drill_problem.step_scheme,
                            learner_lines_for_steps,
                        )
                    except Exception:
                        step_result = None
                if step_result is not None:
                    _print_step_feedback(step_result)
                    try:
                        missing = [
                            s for s in step_result.get("steps", [])
                            if s.get("match_status") == "NOT_MATCHED"
                        ]
                        for m in missing:
                            store.interventions.log(
                                learner_id=learner_id,
                                skill_id=anchor.skill_id,
                                action_type="memo_line_shown",
                                action_desc="Showed memo version of missed step: " + m["desc"],
                                question_id=drill_problem.problem_id,
                                session_id=session_id,
                                context={"step_index": m["index"],
                                         "step_desc": m["desc"]},
                            )
                    except Exception:
                        pass
                    _close_open_interventions(
                        store, learner_id, anchor.skill_id, step_result,
                        drill_problem.problem_id, session_id,
                    )

                try:
                    notes = check_presentation(
                        [s.raw_text for s in submission.steps],
                        topic=anchor.topic_v2, max_notes=5,
                    )
                    for n in notes:
                        if n.rule_id in shown_note_ids:
                            continue
                        shown_note_ids.add(n.rule_id)
                        print(format_note(n))
                        break
                except Exception:
                    pass
                break

            if result.kind == MatchKind.UNCERTAIN:
                print()
                print("  I want to be sure this is the shape the memo expects.")
                _show_sibling(pool, shown_sibling_keys)
                print()
                print("  Try the same question again — or type 'next' to move on.")
                continue

            kind = diagnose_wrong(learner_text, drill_problem.expected_answer)

            misconception_id = None
            try:
                diag = diagnose(anchor.skill_id, learner_text,
                                drill_problem.expected_answer)
                if diag and diag.misconception_id:
                    misconception_id = diag.misconception_id
            except Exception:
                pass

            _save_attempt(store, session_id, learner_id, anchor.skill_id,
                          learner_text, "D_NO_MATCH",
                          (kind or "unknown"), misconception_id)

            try:
                if (kind or "unknown") == "unknown":
                    store.discoveries.record(
                        learner_id=learner_id,
                        skill_id=anchor.skill_id,
                        question_id=drill_problem.problem_id,
                        learner_lines=[s.raw_text for s in submission.steps],
                        expected_answer=drill_problem.expected_answer,
                        session_id=session_id,
                    )
            except Exception:
                pass

            _speak_diagnosis(kind or "unknown")
            if misconception_id:
                print(f"  Noticed: {misconception_id}")

            try:
                notes = check_presentation(
                    [s.raw_text for s in submission.steps],
                    topic=anchor.topic_v2, max_notes=5,
                )
                for n in notes:
                    if n.rule_id in shown_note_ids:
                        continue
                    shown_note_ids.add(n.rule_id)
                    print(format_note(n))
                    break
            except Exception:
                pass

            _show_sibling(pool, shown_sibling_keys)
            print()
            print("  Try the question again — or type 'next' to move on.")

    passed = questions_correct >= PASS_THRESHOLD
    _speak_mastery(anchor.skill_id, template_id,
                   questions_correct, SITTING_SIZE, topic_label,
                   questions_skipped=questions_skipped)

    _try_recompute_mastery(store, learner_id, anchor.skill_id)

    try:
        m = store.get_mastery(learner_id, anchor.skill_id)
        print(f"  Mastery: {m['mastery_state']}  |  Sittings passed: {m['sittings_passed']}")
    except Exception:
        pass

    if interactive_input:
        print()
        print("  Options:")
        print("    Enter / y  →  another sitting on this skill")
        print("    menu       →  pick a different topic")
        print("    q          →  quit")
        again = input("  > ").strip().lower()
        if again in ("", "y", "yes"):
            return run(engine, store, learner_id, session_id, anchor,
                       logger=logger, interactive_input=interactive_input,
                       sitting_number=sitting_number + 1)
        if again in ("menu", "m"):
            _try_recompute_mastery(store, learner_id, anchor.skill_id)
            return {"sittings_passed": 1 if passed else 0,
                    "correct": questions_correct, "total": SITTING_SIZE,
                    "exit_reason": "menu",
                    "template_id": template_id,
                    "sitting_number": sitting_number}

    return {
        "sittings_passed": 1 if passed else 0,
        "correct": questions_correct,
        "total": SITTING_SIZE,
        "first_try": questions_first_try,
        "attempts": total_attempts,
        "exit_reason": "completed",
        "template_id": template_id,
        "sitting_number": sitting_number,
    }


def _try_recompute_mastery(store, learner_id, skill_id):
    try:
        store.recompute_mastery(learner_id, skill_id)
    except Exception:
        pass


def _close_early(questions_correct, questions_attempted):
    print()
    print("=" * 60)
    print(f"  Session closed.  {questions_correct}/{questions_attempted} correct.")
    print("  Progress saved.")
    print("=" * 60)


# ============================================================
# Web entry point — grade ONE submission against ONE anchor
# ============================================================
def _sign_mismatch_only(learner, expected):
    """True if learner and expected differ ONLY in the signs of some numbers."""
    import re as _rs
    def nums(s):
        return _rs.findall(r"-?\d+(?:\.\d+)?", s)
    l = nums(learner); e = nums(expected)
    if len(l) != len(e) or not l:
        return False
    diffs = 0
    for a, b in zip(l, e):
        if a == b:
            continue
        if a.lstrip("-") == b.lstrip("-"):
            diffs += 1
        else:
            return False
    return diffs >= 1


def _make_sign_flip_diagnosis(learner, expected):
    return (
        f"You wrote: {learner}.  The memo has: {expected}.  "
        "The numbers match — one sign is wrong. "
        "When a term crosses the equals sign, its sign flips."
    )


def _make_diagnosis_sentence(learner, expected, kind, misid):
    if kind == "sign_flip":
        return _make_sign_flip_diagnosis(learner, expected)
    if kind == "partial":
        return "One root is right. The other is missing or wrong."
    base = f"Your answer ({learner}) does not match the memo ({expected})."
    if misid:
        base += f"  Noticed: {misid}."
    return base


# ============================================================
import re as _diag_re


_FACTORED = _diag_re.compile(
    r"\(\s*x\s*([+-])\s*(\d+)\s*\)\s*\(\s*x\s*([+-])\s*(\d+)\s*\)\s*=\s*0"
)
_SET_ZERO = _diag_re.compile(
    r"x\s*([+-])\s*(\d+)\s*=\s*0.*?x\s*([+-])\s*(\d+)\s*=\s*0"
)
_ROOTS = _diag_re.compile(
    r"x\s*=\s*(-?\d+)\s*(?:or|,)\s*x\s*=\s*(-?\d+)"
)
_REASONING = _diag_re.compile(
    r"(?:multiply|add|product|sum|times|×|×).*(?:\d).*(?:\d)",
    _diag_re.IGNORECASE,
)


def _sign_const(sign, num):
    return int(num) if sign == "+" else -int(num)


def _diagnose_factorable_line(text, meta):
    """Return a per-line diagnosis dict for one learner line."""
    s = (text or "").strip()
    if not s:
        return None

    # Try factored form
    m = _FACTORED.search(s)
    if m:
        p_l = _sign_const(m.group(1), m.group(2))
        q_l = _sign_const(m.group(3), m.group(4))
        sum_l = p_l + q_l
        prod_l = p_l * q_l
        b = meta.get("b"); c = meta.get("c")
        if sum_l == b and prod_l == c:
            msg = (f"Correct factorisation. "
                   f"Bracket constants {p_l} and {q_l} "
                   f"sum to {b} and multiply to {c}.")
            return {"line": s, "as": "factorise", "verdict": "correct", "message": msg}
        # Distinguish sign-only vs total mismatch
        msg = (f"You used bracket constants {p_l} and {q_l}. "
               f"Their sum is {sum_l} (should be {b}). "
               f"Their product is {prod_l} (should be {c}).")
        if abs(p_l) == abs(meta["p"]) or abs(q_l) == abs(meta["q"]):
            msg += " One of the constants has the right size but the wrong sign."
        return {"line": s, "as": "factorise", "verdict": "wrong", "message": msg}

    # Try set-each-factor
    m = _SET_ZERO.search(s)
    if m:
        p_l = _sign_const(m.group(1), m.group(2))
        q_l = _sign_const(m.group(3), m.group(4))
        if p_l == meta["p"] and q_l == meta["q"]:
            return {"line": s, "as": "set-each-factor", "verdict": "correct",
                    "message": "Correct — each bracket set to zero."}
        return {"line": s, "as": "set-each-factor", "verdict": "wrong",
                "message": f"These do not match the memo factorisation. "
                           f"The memo brackets have constants {meta['p']} and {meta['q']}."}

    # Try roots
    m = _ROOTS.search(s)
    if m:
        lr1, lr2 = int(m.group(1)), int(m.group(2))
        if {lr1, lr2} == {meta["r1"], meta["r2"]}:
            return {"line": s, "as": "roots", "verdict": "correct",
                    "message": "Correct roots."}
        return {"line": s, "as": "roots", "verdict": "wrong",
                "message": (f"Your roots are {lr1} and {lr2}. "
                            f"The memo has {meta['r1']} and {meta['r2']}.")}

    # Reasoning / working line
    if _REASONING.search(s):
        return {"line": s, "as": "reasoning", "verdict": "note",
                "message": "Working noted — this is not a memo step, no mark attached."}

    return {"line": s, "as": "unknown", "verdict": "note",
            "message": "Cannot classify this line."}


def _diagnose_factorable(learner_lines, meta):
    """Run per-line diagnosis for a factorable-quadratic attempt."""
    out = []
    factorise_was_wrong = False
    for line in learner_lines:
        d = _diagnose_factorable_line(line, meta)
        if not d:
            continue
        # If factorise was wrong, note the downstream effect
        if d["as"] == "roots" and d["verdict"] == "wrong" and factorise_was_wrong:
            d["message"] += (" Your roots match your own factorisation, "
                             "but both inherit the error from the line above.")
        if d["as"] == "factorise" and d["verdict"] == "wrong":
            factorise_was_wrong = True
        out.append(d)
    return out


# ============================================================
# Step-oriented diagnostic engine (factorable quadratics)
# ============================================================
import re as _diag_re

_FACTORED = _diag_re.compile(
    r"\(\s*x\s*([+-])\s*(\d+)\s*\)\s*\(\s*x\s*([+-])\s*(\d+)\s*\)\s*=\s*0"
)
_SET_ZERO = _diag_re.compile(
    r"x\s*([+-])\s*(\d+)\s*=\s*0\s*(?:or|,)\s*x\s*([+-])\s*(\d+)\s*=\s*0"
)
_ROOTS = _diag_re.compile(
    r"x\s*=\s*(-?\d+)\s*(?:or|,)\s*x\s*=\s*(-?\d+)"
)
_REASONING = _diag_re.compile(
    r"(?:multiply|add|product|sum|times|\u00d7).*(?:\d).*(?:\d)",
    _diag_re.IGNORECASE,
)


def _sign_const(sign, num):
    return int(num) if sign == "+" else -int(num)


def _classify_all(text, meta):
    """Every memo-step classification a single learner line contains."""
    s = (text or "").strip()
    if not s:
        return []
    results = []

    m = _FACTORED.search(s)
    if m:
        p_l = _sign_const(m.group(1), m.group(2))
        q_l = _sign_const(m.group(3), m.group(4))
        if p_l + q_l == meta["b"] and p_l * q_l == meta["c"]:
            results.append({"kind": "factorise", "correct": True, "line": s})
        else:
            results.append({
                "kind": "factorise", "correct": False, "line": s,
                "reason": (f"Your bracket constants are {p_l} and {q_l}. "
                           f"Their sum is {p_l + q_l} (should be {meta['b']}). "
                           f"Their product is {p_l * q_l} (should be {meta['c']})."),
            })

    m = _SET_ZERO.search(s)
    if m:
        p_l = _sign_const(m.group(1), m.group(2))
        q_l = _sign_const(m.group(3), m.group(4))
        if {p_l, q_l} == {meta["p"], meta["q"]}:
            results.append({"kind": "setzero", "correct": True, "line": s})
        else:
            results.append({
                "kind": "setzero", "correct": False, "line": s,
                "reason": (f"These do not match the memo's factorisation. "
                           f"The memo brackets have constants {meta['p']} and {meta['q']}."),
            })

    m = _ROOTS.search(s)
    if m:
        lr1, lr2 = int(m.group(1)), int(m.group(2))
        if {lr1, lr2} == {meta["r1"], meta["r2"]}:
            results.append({"kind": "roots", "correct": True, "line": s})
        else:
            results.append({
                "kind": "roots", "correct": False, "line": s,
                "reason": (f"Your roots are {lr1} and {lr2}. "
                           f"The memo has {meta['r1']} and {meta['r2']}."),
            })

    if not results and _REASONING.search(s):
        results.append({"kind": "reasoning", "line": s})
    return results


def _diagnose_factorable_steps(learner_lines, meta):
    """Per-memo-step verdict for a factorable-quadratic attempt."""
    # derive expected strings if the meta dict came from the pool without them
    if "expected_factorised" not in meta:
        def _br(k):
            if k == 0: return "(x)"
            return f"(x - {k})" if k > 0 else f"(x + {abs(k)})"
        def _sz(k):
            if k == 0: return "x = 0"
            return f"x - {k} = 0" if k > 0 else f"x + {abs(k)} = 0"
        meta = dict(meta)
        meta["expected_factorised"] = f"{_br(meta['p'])}{_br(meta['q'])} = 0"
        meta["expected_setzero"]    = f"{_sz(meta['p'])}  or  {_sz(meta['q'])}"
        meta["expected_roots"]      = f"x = {meta['r1']} or x = {meta['r2']}"

    all_c = []
    for line in learner_lines:
        all_c.extend(_classify_all(line, meta))

    def find(kind):
        return next((c for c in all_c if c.get("kind") == kind), None)

    steps = []

    # Step 1 — Factorise
    f = find("factorise")
    if f and f["correct"]:
        steps.append({"step": 1, "name": "Factorise", "marks": 1,
                      "status": "CORRECT", "message": "", "evidence": f["line"]})
    elif f:
        steps.append({"step": 1, "name": "Factorise", "marks": 1,
                      "status": "WRONG", "message": f["reason"], "evidence": f["line"]})
    else:
        steps.append({"step": 1, "name": "Factorise", "marks": 1,
                      "status": "MISSING",
                      "message": (f"You didn't show the factored form. "
                                  f"The memo wants a line like: {meta['expected_factorised']}."),
                      "evidence": ""})

    # Step 2 — Set each factor to zero
    z = find("setzero")
    r = find("roots")
    if z and z["correct"]:
        steps.append({"step": 2, "name": "Set each factor to zero", "marks": 1,
                      "status": "CORRECT", "message": "", "evidence": z["line"]})
    elif z:
        steps.append({"step": 2, "name": "Set each factor to zero", "marks": 1,
                      "status": "WRONG", "message": z["reason"], "evidence": z["line"]})
    elif r:
        steps.append({"step": 2, "name": "Set each factor to zero", "marks": 1,
                      "status": "MISSING",
                      "message": (f"You went from brackets straight to the roots. "
                                  f"The memo wants each factor set to zero, "
                                  f"e.g. {meta['expected_setzero']}."),
                      "evidence": ""})
    else:
        steps.append({"step": 2, "name": "Set each factor to zero", "marks": 1,
                      "status": "MISSING",
                      "message": (f"You didn't set each factor to zero. "
                                  f"The memo wants a line like: {meta['expected_setzero']}."),
                      "evidence": ""})

    # Step 3 — Both roots
    if r and r["correct"]:
        steps.append({"step": 3, "name": "Write both roots", "marks": 1,
                      "status": "CORRECT", "message": "", "evidence": r["line"]})
    elif r:
        msg = r["reason"]
        if f and not f["correct"]:
            msg += " These match your own factorisation, but the factorisation was wrong."
        steps.append({"step": 3, "name": "Write both roots", "marks": 1,
                      "status": "WRONG", "message": msg, "evidence": r["line"]})
    else:
        steps.append({"step": 3, "name": "Write both roots", "marks": 1,
                      "status": "MISSING",
                      "message": (f"The final roots line is missing or incomplete. "
                                  f"The memo wants both solutions, e.g. {meta['expected_roots']}."),
                      "evidence": ""})

    return steps


def _derive_meta_from_prompt(prompt):
    """Parse 'x^2 + bx + c = 0' and return the meta dict with roots.

    Works for any factorable quadratic — no pool lookup needed.
    Returns None if the roots are not integers or the pattern doesn't match.
    """
    import re as _rp
    import math as _math
    s = (prompt or "").replace(" ", "")
    m = _rp.search(r"x\^2([+-]?\d*)x([+-]?\d+)=0", s)
    if not m:
        return None
    b_str, c_str = m.group(1), m.group(2)
    if b_str in ("", "+"):
        b = 1
    elif b_str == "-":
        b = -1
    else:
        try:
            b = int(b_str)
        except ValueError:
            return None
    try:
        c = int(c_str)
    except ValueError:
        return None
    disc = b * b - 4 * c
    if disc < 0:
        return None
    sd = _math.isqrt(disc)
    if sd * sd != disc:
        return None
    if (b + sd) % 2 != 0:
        return None
    r1 = (-b + sd) // 2
    r2 = (-b - sd) // 2
    if r1 * r2 != c or r1 + r2 != -b:
        return None
    p, q = -r1, -r2
    return {"r1": r1, "r2": r2, "b": b, "c": c, "p": p, "q": q}


def _find_meta_for_anchor(anchor):
    """Return meta for the anchor. Derives from the prompt first;
    falls back to a pool lookup only if derivation fails."""
    try:
        tid = route_template(anchor.skill_id, anchor.prompt)
        if tid != "quadratic_standard_factorable":
            return None

        derived = _derive_meta_from_prompt(anchor.prompt)
        if derived:
            return derived

        pool = _load_pool(tid)
        if not pool:
            return None
        s = anchor.prompt.replace(" ", "")
        m = _diag_re.search(r"x\^2([+-]?\d*)x([+-]?\d+)=0", s)
        if not m:
            return pool[0].get("meta")
        b_str, c_str = m.group(1), m.group(2)
        try:
            b = 1 if b_str == "" else (-1 if b_str == "-" else int(b_str))
            c = int(c_str)
        except Exception:
            return pool[0].get("meta")
        for v in pool:
            meta = v.get("meta")
            if meta and meta.get("b") == b and meta.get("c") == c:
                return meta
        return pool[0].get("meta")
    except Exception:
        return None


def grade_submission(store, learner_id, session_id, anchor,
                     learner_lines, sbc_message=""):
    """Grade one keyboard submission. Return a marker-style verdict."""
    from . import slash_commands as _sc

    expanded = [_sc.expand(line) if line else "" for line in learner_lines]

    if sbc_message.strip():
        try:
            store.interventions.log(
                learner_id=learner_id, skill_id=anchor.skill_id,
                action_type="sbc_message",
                action_desc=sbc_message.strip()[:400],
                question_id=anchor.problem_id, session_id=session_id,
                context={"source": "keyboard"},
            )
        except Exception:
            pass

    plain_lines = [_latex_to_plain(x) for x in expanded]
    final_answer = plain_lines[-1].strip() if plain_lines else ""

    # strict number-set check before trusting the matcher's UNCERTAIN
    def _nums(s):
        import re as _rn
        return [int(x) for x in _rn.findall(r"-?\d+", s or "")]
    def _signless(s):
        return set(abs(n) for n in _nums(s))

    _learner_nums = _signless(final_answer)
    _expected_nums = _signless(anchor.expected_answer)
    _num_set_matches = _learner_nums == _expected_nums and bool(_expected_nums)

    # strict: sign-only mismatch is a real error, not ambiguous form
    sign_only = _sign_mismatch_only(final_answer, anchor.expected_answer)

    try:
        result = grade(final_answer, anchor.expected_answer)
    except Exception as e:
        return {"match": "error", "message": f"grader failed: {e}",
                "raw_lines": expanded, "your_working": plain_lines,
                "mark": {"awarded": 0, "total": 0}, "memo_steps": [],
                "diagnosis": f"Grader error: {e}",
                "tanaka_message": "", "mastery": None, "sibling": None}

    _tid_shape = _shape_for_template(route_template(anchor.skill_id, anchor.prompt))
    # derive the anchor's subquestion from its problem_id: 2023_P1_Q1.1.1 → "1.1.1"
    import re as _re_sub
    _m = _re_sub.search(r"Q\d+\.(\d+(?:\.\d+)*)", anchor.problem_id or "")
    _anchor_subq = _m.group(1) if _m else ""
    corpus_ctx = corpus_for_skill(anchor.skill_id, shape=_tid_shape, anchor_subq=_anchor_subq)
    # per-step diagnosis for factorable quadratics
    meta = _find_meta_for_anchor(anchor)
    step_diagnosis = []
    if meta:
        try:
            step_diagnosis = _diagnose_factorable_steps(plain_lines, meta)
        except Exception:
            step_diagnosis = []

    # universal misconception detection — runs regardless of which branch
    # decides the verdict. Errors here are silent; diagnosis is best-effort.
    misconception_id = None
    intervention = None
    try:
        _diag = diagnose(anchor.skill_id, final_answer, anchor.expected_answer)
        if _diag and getattr(_diag, "misconception_id", None):
            misconception_id = _diag.misconception_id
            intervention = intervention_for_misconception(misconception_id)
    except Exception:
        pass


    outcome = {
        "match": None,
        "raw_lines": expanded,
        "your_working": plain_lines,
        "step_diagnosis": step_diagnosis,
        "corpus_context": corpus_ctx,
        "intervention": intervention,
        "misconception_id": misconception_id,
        "step_feedback": None,
        "memo_steps": [],
        "mark": {"awarded": 0, "total": 0},
        "diagnosis": "",
        "tanaka_message": "",
        "mastery": None,
        "sibling": None,
    }

    # step grader runs for MATCH and NO_MATCH both
    step_result = _step_feedback(anchor.problem_id, plain_lines)
    if step_result is None and getattr(anchor, "step_scheme", None):
        try:
            step_result = grade_steps_inline(anchor.step_scheme, plain_lines)
        except Exception:
            step_result = None

    if step_result is not None:
        outcome["mark"] = {
            "awarded": step_result["awarded_marks"],
            "total":   step_result["total_marks"],
        }
        outcome["memo_steps"] = [
            {"index": s.get("index"), "desc": s.get("desc"),
             "marks": s.get("marks"), "status": s.get("match_status"),
             "first_form": (s.get("forms") or [None])[0]}
            for s in step_result.get("steps", [])
        ]

    if sign_only:
        outcome["match"] = "NO_MATCH"
        _save_attempt(store, session_id, learner_id, anchor.skill_id,
                      final_answer, "D_sign_flip", "sign_flip")
        outcome["diagnosis"] = _make_sign_flip_diagnosis(final_answer,
                                                         anchor.expected_answer)

        try:
            store.discoveries.record(
                learner_id=learner_id, skill_id=anchor.skill_id,
                question_id=anchor.problem_id, learner_lines=plain_lines,
                expected_answer=anchor.expected_answer, session_id=session_id,
            )
        except Exception:
            pass
        sib = _pick_sibling_for_anchor(anchor)
        if sib: outcome["sibling"] = sib

    elif result.kind == MatchKind.MATCH:
        outcome["match"] = "MATCH"
        _save_attempt(store, session_id, learner_id, anchor.skill_id,
                      final_answer, "D_match", "none")

        if step_result is not None:
            try:
                for m in step_result.get("steps", []):
                    if m.get("match_status") == "NOT_MATCHED":
                        store.interventions.log(
                            learner_id=learner_id, skill_id=anchor.skill_id,
                            action_type="memo_line_shown",
                            action_desc="Showed memo version of missed step: " + m["desc"],
                            question_id=anchor.problem_id, session_id=session_id,
                            context={"step_index": m["index"], "step_desc": m["desc"]},
                        )
            except Exception:
                pass
            _close_open_interventions(store, learner_id, anchor.skill_id,
                                      step_result, anchor.problem_id, session_id)

        if step_result is None:
            outcome["diagnosis"] = "Answer matches the memo."
        elif step_result["awarded_marks"] == step_result["total_marks"]:
            outcome["diagnosis"] = "Full method. All memo steps shown."
        else:
            missing = [s["desc"] for s in step_result.get("steps", [])
                       if s.get("match_status") == "NOT_MATCHED"]
            outcome["diagnosis"] = (
                "Answer is right, but the method is incomplete. Missing: "
                + "; ".join(missing) + "."
            )

    elif result.kind == MatchKind.UNCERTAIN and not _num_set_matches:
        # Numbers differ from expected → wrong answer, not ambiguous form
        outcome["match"] = "NO_MATCH"
        outcome["diagnosis"] = (
            f"Your final answer ({final_answer}) does not match the memo "
            f"({anchor.expected_answer})."
        )
        sib = _pick_sibling_for_anchor(anchor)
        if sib: outcome["sibling"] = sib

    elif result.kind == MatchKind.UNCERTAIN:
        outcome["match"] = "UNCERTAIN"
        outcome["diagnosis"] = (
            "Your working does not clearly match the memo's expected form. "
            "Check the notation."
        )
        sib = _pick_sibling_for_anchor(anchor)
        if sib: outcome["sibling"] = sib

    else:
        outcome["match"] = "NO_MATCH"
        try:
            kind = diagnose_wrong(final_answer, anchor.expected_answer) or "unknown"
        except Exception:
            kind = "unknown"
        misid = None
        try:
            diag = diagnose(anchor.skill_id, final_answer, anchor.expected_answer)
            if diag and diag.misconception_id:
                misid = diag.misconception_id
        except Exception:
            pass
        _save_attempt(store, session_id, learner_id, anchor.skill_id,
                      final_answer, "D_NO_MATCH", kind, misid)
        if kind == "unknown":
            try:
                store.discoveries.record(
                    learner_id=learner_id, skill_id=anchor.skill_id,
                    question_id=anchor.problem_id, learner_lines=plain_lines,
                    expected_answer=anchor.expected_answer, session_id=session_id,
                )
            except Exception:
                pass
        outcome["diagnosis"] = _make_diagnosis_sentence(
            final_answer, anchor.expected_answer, kind, misid)
        sib = _pick_sibling_for_anchor(anchor)
        if sib: outcome["sibling"] = sib

    _try_recompute_mastery(store, learner_id, anchor.skill_id)
    try:
        m = store.get_mastery(learner_id, anchor.skill_id)
        outcome["mastery"] = {"state": m.get("mastery_state"),
                              "passed": m.get("sittings_passed", 0)}
    except Exception:
        outcome["mastery"] = None

    # ── override with step_diagnosis when available ──
    if step_diagnosis:
        awarded = sum(1 for d in step_diagnosis if d["status"] == "CORRECT")
        total   = sum(d["marks"] for d in step_diagnosis)
        outcome["mark"] = {"awarded": awarded, "total": total}

        wrong = [d for d in step_diagnosis
                 if d["status"] in ("WRONG", "MISSING")]
        if not wrong:
            outcome["diagnosis"] = "Full method. All memo steps shown."
        else:
            outcome["diagnosis"] = wrong[0]["message"]

        if awarded == total:
            outcome["match"] = "MATCH"
            outcome["sibling"] = None
        elif _num_set_matches and awarded >= 1:
            outcome["match"] = "MATCH"
        else:
            outcome["match"] = "NO_MATCH"

    return outcome


