"""
template_jitter.py — generic variant engine for P1 question templates.

A template declares, per subquestion:
  - prompt_template:  string with {placeholder} slots
  - ranges:           dict {placeholder: [candidate values]}
  - expected_fn:      string with {placeholder} slots, OR "__solve__"
                      for the special simultaneous-solve case
  - steps:            list of memo-step strings with {placeholder} slots
  - marks:            int
  - skill_id:         str
  - validator:        optional name of a shape validator

The engine samples parameters, applies derived values, validates, and
formats the strings. No per-question Python needed.

Shape validators currently available:
  - "simultaneous": for a*x + y = k and y^2 + xy = m — requires the
    resulting quadratic to have a perfect-square discriminant.
"""
from __future__ import annotations
from pathlib import Path
import math
import random


# ============================================================
# Formatting helpers
# ============================================================

def _signed_term(coef, variable=""):
    if coef == 0:
        return ""
    sign = "+" if coef > 0 else "-"
    mag = abs(coef)
    if variable:
        if mag == 1:
            return f"{sign} {variable}"
        return f"{sign} {mag}{variable}"
    return f"{sign} {mag}"


def _factor(root):
    """Return (x + 2) / (x - 5) / (x) — never (x - (-2))."""
    if root == 0:
        return "(x)"
    if root > 0:
        return f"(x - {root})"
    return f"(x + {abs(root)})"


def _fmt_num(v):
    """Format a rational as 'int' or 'a/b'."""
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    if isinstance(v, tuple) and len(v) == 2:
        num, den = v
        if den == 1:
            return str(num)
        return f"{num}/{den}"
    return str(v)


def _fraction_from_quadratic(A, B, s):
    """Return tuple (num, den) reduced for (-B + s) / (2A)."""
    num = -B + s
    den = 2 * A
    if den < 0:
        num, den = -num, -den
    g = math.gcd(abs(num), abs(den))
    if g:
        num //= g
        den //= g
    return (num, den)


# ============================================================
# Derived-parameter application
# ============================================================

def _apply_derived(p):
    p = dict(p)
    if "r1" in p and "r2" in p:
        p.setdefault("b", -(p["r1"] + p["r2"]))
        p.setdefault("c", p["r1"] * p["r2"])
        p["b_terms"] = _signed_term(p["b"], "x")
        p["c_terms"] = _signed_term(p["c"])
        p["factor_r1"] = _factor(p["r1"])
        p["factor_r2"] = _factor(p["r2"])
    return p


# ============================================================
# Validators
# ============================================================

def _validate_simultaneous(p):
    a, k, m = p.get("a"), p.get("k"), p.get("m")
    if not all(isinstance(v, int) for v in (a, k, m)):
        return False
    A = a * a - a
    if A == 0:
        return False
    B = k - 2 * a * k
    C = k * k - m
    D = B * B - 4 * A * C
    if D < 0:
        return False
    s = math.isqrt(D)
    return s * s == D


VALIDATORS = {
    "simultaneous": _validate_simultaneous,
}


# ============================================================
# Special expected answers
# ============================================================

def _solve_simultaneous(a, k, m):
    """Return the (x, y) pairs for a*x + y = k, y^2 + xy = m as a string."""
    A = a * a - a
    B = k - 2 * a * k
    C = k * k - m
    D = B * B - 4 * A * C
    s = math.isqrt(D)
    pairs = []
    for sign in (1, -1):
        x = _fraction_from_quadratic(A, B, sign * s)
        # y = k - a*x
        y_num = k * x[1] - a * x[0]
        y_den = x[1]
        g = math.gcd(abs(y_num), abs(y_den))
        if g:
            y_num //= g
            y_den //= g
        y = (y_num, y_den)
        pairs.append((x, y))
    # Format: (x = 4, y = -5) or (x = 1/2, y = 2)
    parts = []
    for (xn, xd), (yn, yd) in pairs:
        parts.append(f"(x = {_fmt_num((xn, xd))}, y = {_fmt_num((yn, yd))})")
    return " or ".join(parts)


# ============================================================
# Engine
# ============================================================

def _sample(ranges, rng):
    return {k: rng.choice(v) for k, v in ranges.items()}


def jitter_template(template, seed=None, max_attempts=5000):
    rng = random.Random(seed)
    filled = {
        "source": template["source"],
        "stem": template.get("stem", ""),
        "subquestions": [],
        "scenario": "p1_template",
    }
    for sq in template["subquestions"]:
        ranges = sq.get("ranges", {}) or {}
        placed = False
        for _ in range(max_attempts):
            raw = _sample(ranges, rng) if ranges else {}
            params = _apply_derived(raw)
            validator_name = sq.get("validator")
            if validator_name and not VALIDATORS[validator_name](params):
                continue
            try:
                prompt = sq["prompt_template"].format(**params)
                exp_fn = sq["expected_fn"]
                if exp_fn == "__solve__":
                    # Special: for a*x + y = k, y^2 + xy = m
                    expected = _solve_simultaneous(
                        params["a"], params["k"], params["m"])
                else:
                    expected = exp_fn.format(**params)
                steps = [s.format(**params) for s in sq.get("steps", [])]
            except (KeyError, ValueError):
                continue
            filled["subquestions"].append({
                "n": sq["n"],
                "prompt": prompt,
                "expected": expected,
                "steps": steps,
                "marks": sq["marks"],
                "skill_id": sq["skill_id"],
                "params": params,
            })
            placed = True
            break
        if not placed:
            filled["subquestions"].append({
                "n": sq["n"],
                "prompt": "(jitter failed — constraints too tight)",
                "expected": "", "steps": [],
                "marks": sq["marks"], "skill_id": sq["skill_id"], "params": {},
            })
    filled["total_marks"] = sum(s["marks"] for s in filled["subquestions"])
    return filled

def _human(coef, var=""):
    """'+ 3x' / '- 3x' / '- x' / '+ 3' / '' — with the leading sign
    always present and no double-signs like '+ -'. Returns '' for 0."""
    if coef == 0:
        return ""
    sign = "+" if coef > 0 else "-"
    mag = abs(coef)
    if var:
        if mag == 1:
            return f"{sign} {var}"
        return f"{sign} {mag}{var}"
    return f"{sign} {mag}"


def _poly_disp(a_coef, b_coef, c_coef, var="x"):
    """Return '2x^2 + 3x - 5' style. Suppresses coefficient of 1 and term 0."""
    parts = []
    if a_coef != 0:
        if a_coef == 1:
            parts.append(f"{var}^2")
        elif a_coef == -1:
            parts.append(f"-{var}^2")
        else:
            parts.append(f"{a_coef}{var}^2")
    if b_coef != 0:
        s = _human(b_coef, var)
        if parts:
            parts.append(s)
        else:
            parts.append(s.lstrip("+ "))
    if c_coef != 0:
        s = _human(c_coef)
        if parts:
            parts.append(s)
        else:
            parts.append(s.lstrip("+ "))
    return " ".join(parts) if parts else "0"


def _fnum_h(v):
    """Format a number nicely: 3, -3, 3.5, 3/2 (as fraction string if given tuple)."""
    if isinstance(v, tuple):
        n, d = v
        if d == 1: return str(n)
        return f"{n}/{d}"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)

def _f_disp_parabola(a, p, q):
    if a == 1: head = ""
    elif a == -1: head = "-"
    else: head = f"{a}"
    inner = f"(x + {abs(p)})" if p < 0 else (f"(x - {p})" if p != 0 else "(x)")
    return f"{head}{inner}^2" + (" " + _human(q) if q != 0 else "")


def _g_disp_line(m, c):
    if m == 1: head = "x"
    elif m == -1: head = "-x"
    else: head = f"{m}x"
    if c == 0: return head
    return f"{head} {_human(c)}"

def _rand(v):
    """South African number format: 35801.67 -> '35 801.67'."""
    if isinstance(v, str):
        return v
    if isinstance(v, int):
        return f"{v:,}".replace(",", " ")
    if isinstance(v, float):
        if v.is_integer():
            return f"{int(v):,}".replace(",", " ")
        return f"{v:,.2f}".replace(",", " ")
    return str(v)


def _ordinal(n):
    """1 -> 1st, 2 -> 2nd, 21 -> 21st, 11 -> 11th."""
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def _num_clean(v):
    """R1800.0 -> 'R1 800'."""
    if isinstance(v, float) and v.is_integer():
        return _rand(int(v))
    return _rand(v)

