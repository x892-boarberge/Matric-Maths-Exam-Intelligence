"""
Template router — decides which template_id to use for an anchor question.

Reads the static skill -> template map as default, then overrides
for skills that have multiple templates (currently only quadratic).

Public:
    route_template(skill_id, prompt) -> template_id or None
"""
import re
from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT / "data" / "processed" / "tutor" / "analogue_template_map.csv"


def _load_map():
    if not MAP_PATH.exists():
        return {}
    m = {}
    with open(MAP_PATH, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            sid = (row.get("skill_id") or "").strip()
            tid = (row.get("template_id") or "").strip()
            if sid and tid:
                m[sid] = tid
    return m


_MAP = _load_map()


def _is_already_factored(prompt: str) -> bool:
    """(x+5)(x-2) = 0"""
    return bool(re.search(r"\(\s*x\s*[+\-]\s*\d+\s*\)\s*\(\s*x\s*[+\-]\s*\d+\s*\)", prompt))


def _is_standard_form(prompt: str) -> bool:
    """x^2 + bx + c = 0 or ax^2 + bx + c = 0 with a=1."""
    return bool(re.search(r"\bx\s*\^?\s*2\s*[+\-]", prompt))


def _is_formula_question(prompt: str) -> bool:
    """Leading coefficient > 1 OR 'two decimal places'."""
    low = prompt.lower()
    if "two decimal" in low or "correct to" in low:
        return True
    if re.search(r"\b[2-9]\s*x\s*\^?\s*2", prompt):
        return True
    return False


def route_template(skill_id: str, prompt: str = ""):
    """Return the best template_id for this (skill, prompt)."""
    sid = str(skill_id or "").strip()
    if not sid:
        return None

    def _lookup(skill):
        """Exact key, else family prefix (algebra.quadratic.solve -> algebra.quadratic)."""
        tid = _MAP.get(skill)
        if tid:
            return tid
        if "." in skill:
            family = skill.rsplit(".", 1)[0]
            tid = _MAP.get(family)
            if tid:
                return tid
        return None

    # --- Quadratic solve — has multiple templates ---
    if sid == "algebra.quadratic.solve":
        if _is_formula_question(prompt):
            return "quadratic_formula"
        if _is_already_factored(prompt):
            return "quadratic_factored"
        if _is_standard_form(prompt):
            return "quadratic_standard_factorable"
        # Prompt shape could not be determined (empty, OCR-garbled, or
        # unusual wording). The family map holds multiple quadratic
        # templates and last-wins, so do NOT consult it here — it would
        # return whichever row happened to be last. Default to the most
        # general quadratic template instead.
        return "quadratic_standard_factorable"

    # --- Everything else — map with family-prefix fallback ---
    return _lookup(sid)


def all_routed_templates() -> list:
    return sorted(set(_MAP.values()) | {"quadratic_standard_factorable"})