"""
Build step schemes from template + analogue, for drill variants.

Each builder returns a list of step dicts compatible with step_grader:
    index, desc, marks, forms, match_mode, is_final

Currently covers the quadratic family (factored / standard-factorable / formula).
Other templates return None and are skipped by the drill.
"""
from __future__ import annotations

import re
from typing import Optional


def _parse_roots(expected: str) -> list[str]:
    """Pull two numbers from an answer like 'x = -3 or x = 5' or 'x=-3 or x=5'."""
    if not expected:
        return []
    # Normalise
    s = expected.lower().replace(" ", "")
    # Common patterns
    nums = re.findall(r"x=(-?\d+(?:\.\d+)?)", s)
    if len(nums) >= 2:
        return [nums[0], nums[1]]
    # Try "x = a; x = b"
    nums = re.findall(r"(-?\d+(?:\.\d+)?)", s)
    if len(nums) >= 2:
        return [nums[0], nums[1]]
    return []


def _xterm_from_root(r: str) -> str:
    """For root r, produce 'x - r' or 'x + r'."""
    if r.startswith("-"):
        return f"x + {r[1:]}"
    return f"x - {r}"


def _build_factored(problem: str, expected: str) -> Optional[list[dict]]:
    """Factored-form quadratic: (x+a)(x+b)=0. Two marks: one per root."""
    roots = _parse_roots(expected)
    if len(roots) < 2:
        return None
    r1, r2 = roots[0], roots[1]
    return [
        {
            "index": 1, "desc": f"Root x = {r1}", "marks": 1,
            "forms": [f"x = {r1}", f"x={r1}", f"x = {r1} or x = {r2}"],
            "match_mode": "exact", "is_final": True, "method_group": "A",
        },
        {
            "index": 2, "desc": f"Root x = {r2}", "marks": 1,
            "forms": [f"x = {r2}", f"x={r2}", f"x = {r1} or x = {r2}",
                      f"x = {r2} or x = {r1}"],
            "match_mode": "exact", "is_final": True, "method_group": "A",
        },
    ]


def _build_standard_factorable(problem: str, expected: str) -> Optional[list[dict]]:
    """Standard-form factorable: x^2 + bx + c = 0. Three marks."""
    roots = _parse_roots(expected)
    if len(roots) < 2:
        return None
    r1, r2 = roots[0], roots[1]
    # Factorise step: acceptable forms
    f1 = f"(x - {r1})(x - {r2}) = 0"
    f2 = f"(x - {r2})(x - {r1}) = 0"
    # Set-to-zero step
    z1 = f"{_xterm_from_root(r1)} = 0"
    z2 = f"{_xterm_from_root(r2)} = 0"
    # Roots step
    roots_form = f"x = {r1} or x = {r2}"
    roots_form_rev = f"x = {r2} or x = {r1}"
    return [
        {
            "index": 1, "desc": "Factorise the quadratic", "marks": 1,
            "forms": [f1, f2,
                      f"(x-{r1})(x-{r2})=0", f"(x-{r2})(x-{r1})=0",
                      f"(x + {-int(r1)})(x + {-int(r2)}) = 0"
                      if r1.lstrip('-').isdigit() and r2.lstrip('-').isdigit() else f1],
            "match_mode": "exact", "is_final": False, "method_group": "A",
        },
        {
            "index": 2, "desc": "Set each factor to zero", "marks": 1,
            "forms": [f"{z1} or {z2}", f"{z2} or {z1}", z1, z2],
            "match_mode": "exact", "is_final": False, "method_group": "A",
        },
        {
            "index": 3, "desc": "Write both roots", "marks": 1,
            "forms": [roots_form, roots_form_rev,
                      roots_form.replace(" ", ""), roots_form_rev.replace(" ", "")],
            "match_mode": "exact", "is_final": True, "method_group": "A",
        },
    ]


_BUILDERS = {
    "quadratic_factored": _build_factored,
    "quadratic_standard_factorable": _build_standard_factorable,
    # add more templates here as we cover them
}


def build_scheme(template_id: str, analogue: dict, expected_answer: str) -> Optional[list[dict]]:
    """Return a step scheme for the given analogue, or None if unsupported."""
    builder = _BUILDERS.get(template_id)
    if builder is None:
        return None
    problem = analogue.get("problem", "")
    try:
        return builder(problem, expected_answer)
    except Exception:
        return None
