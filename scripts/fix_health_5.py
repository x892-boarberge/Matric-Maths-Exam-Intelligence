"""Fix all 5 health-check failures."""
from pathlib import Path
import ast

# ==================================================================
# FIX 1 — re-register quadratic_formula
# ==================================================================
P1 = Path("src/tutor/analogue_generators.py")
src1 = P1.read_text(encoding="utf-8-sig")

if '"quadratic_formula"' not in src1.split("TEMPLATES = {")[1][:2500]:
    old = '    "quadratic_standard_factorable": (gen_quadratic_standard_factorable, 50),'
    new = '''    "quadratic_standard_factorable": (gen_quadratic_standard_factorable, 50),
    "quadratic_formula":             (gen_quadratic_formula, 50),'''
    if old in src1:
        src1 = src1.replace(old, new, 1)
        ast.parse(src1)
        P1.write_text(src1, encoding="utf-8")
        print("FIX 1: re-registered quadratic_formula")
    else:
        print("FIX 1 WARN: registration anchor not found")
else:
    print("FIX 1: already registered")


# ==================================================================
# FIX 2, 3, 4, 5 — patch math_grader
# ==================================================================
P2 = Path("src/tutor/math_grader.py")
src2 = P2.read_text(encoding="utf-8-sig")

# --- FIX 2: smarter splitting — don't split on comma inside numbers ---
old_split = '''SPLIT_RE = re.compile(r"\\s*(?:,|;|\\bor\\b|\\band\\b)\\s*", re.IGNORECASE)'''
new_split = '''# Split on 'or' or 'and' or ';' or ', ' (comma followed by space and NOT digit)
SPLIT_RE = re.compile(r"\\s*;\\s*|\\s+\\bor\\b\\s+|\\s+\\band\\b\\s+|\\s*,\\s*(?![\\d])", re.IGNORECASE)'''

if old_split in src2:
    src2 = src2.replace(old_split, new_split, 1)
    print("FIX 2: tightened split — comma before digit is not a separator")
else:
    print("FIX 2 WARN: SPLIT_RE not found")

# --- FIX 3: fraction_decimal handles multi-part by delegating to parts ---
old_frac = '''def m_fraction_decimal(a: str, b: str):
    """3/4 ↔ 0.75, 12/35 ↔ 0.34 (with 2dp rounding tolerance)."""
    if not _HAS_SYMPY:
        return False, 0.0, ""
    ap = _parts(a)
    bp = _parts(b)
    if not ap or not bp:
        return False, 0.0, ""
    try:
        a_vals = [sp.sympify(p) for p in ap]
        b_vals = [sp.sympify(p) for p in bp]
    except Exception:
        return False, 0.0, ""
    if len(a_vals) != len(b_vals):
        return False, 0.0, ""
    remaining = list(b_vals)
    for av in a_vals:
        matched = False
        for bv in list(remaining):
            try:
                # Exact
                if sp.simplify(av - bv) == 0:
                    remaining.remove(bv)
                    matched = True
                    break
                # 2-decimal rounding tolerance
                if float(abs(float(av) - float(bv))) <= 0.005:
                    remaining.remove(bv)
                    matched = True
                    break
            except Exception:
                continue
        if not matched:
            return False, 0.0, ""
    if not remaining:
        return True, 0.88, "fraction/decimal equal"
    return False, 0.0, ""'''

new_frac = '''def m_fraction_decimal(a: str, b: str):
    """3/4 ↔ 0.75, multi-part with tolerance."""
    if not _HAS_SYMPY:
        return False, 0.0, ""
    ap = _parts(a)
    bp = _parts(b)
    if not ap or not bp:
        return False, 0.0, ""
    a_vals = []
    b_vals = []
    for p in ap:
        try:
            a_vals.append(sp.sympify(p))
        except Exception:
            return False, 0.0, ""
    for p in bp:
        try:
            b_vals.append(sp.sympify(p))
        except Exception:
            return False, 0.0, ""
    if len(a_vals) != len(b_vals):
        return False, 0.0, ""
    # Try each permutation-free match
    remaining = list(b_vals)
    for av in a_vals:
        matched = False
        for bv in list(remaining):
            try:
                if sp.simplify(av - bv) == 0:
                    remaining.remove(bv)
                    matched = True
                    break
                try:
                    if abs(float(av) - float(bv)) <= 0.005:
                        remaining.remove(bv)
                        matched = True
                        break
                except Exception:
                    pass
            except Exception:
                continue
        if not matched:
            return False, 0.0, ""
    if not remaining:
        return True, 0.88, "fraction/decimal equal"
    return False, 0.0, ""'''

if old_frac in src2:
    src2 = src2.replace(old_frac, new_frac, 1)
    print("FIX 3: fraction_decimal handles multi-part")
else:
    print("FIX 3 WARN: fraction_decimal anchor not found")

# --- FIX 4: symbolic — pre-declare common symbols ---
old_sym = '''def m_symbolic(a: str, b: str):
    """Symbolic expression — 'Tn = 2 + 5n' vs 'T_n = 5n + 2'."""
    if not _HAS_SYMPY:
        return False, 0.0, ""
    try:
        a_expr = _strip_label(_strip_subscripts(_normalise(a)))
        b_expr = _strip_label(_strip_subscripts(_normalise(b)))
        av = sp.sympify(a_expr)
        bv = sp.sympify(b_expr)
        if sp.simplify(av - bv) == 0:
            return True, 0.94, "symbolic equal"
    except Exception:
        pass
    return False, 0.0, ""'''

new_sym = '''def m_symbolic(a: str, b: str):
    """Symbolic expression — 'Tn = 2 + 5n' vs 'T_n = 5n + 2'."""
    if not _HAS_SYMPY:
        return False, 0.0, ""
    try:
        a_expr = _strip_label(_strip_subscripts(_normalise(a)))
        b_expr = _strip_label(_strip_subscripts(_normalise(b)))
        # Pre-declare single-letter and common variables
        local_dict = {
            "n": sp.Symbol("n"),
            "x": sp.Symbol("x"),
            "y": sp.Symbol("y"),
            "t": sp.Symbol("t"),
            "k": sp.Symbol("k"),
            "a": sp.Symbol("a"),
            "b": sp.Symbol("b"),
            "c": sp.Symbol("c"),
            "d": sp.Symbol("d"),
            "r": sp.Symbol("r"),
            "T": sp.Symbol("T"),
            "S": sp.Symbol("S"),
        }
        av = sp.sympify(a_expr, locals=local_dict)
        bv = sp.sympify(b_expr, locals=local_dict)
        if sp.simplify(av - bv) == 0:
            return True, 0.94, "symbolic equal"
    except Exception:
        pass
    return False, 0.0, ""'''

if old_sym in src2:
    src2 = src2.replace(old_sym, new_sym, 1)
    print("FIX 4: symbolic pre-declares symbols")
else:
    print("FIX 4 WARN: symbolic anchor not found")

# --- FIX 5: re-add diagnose_wrong ---
if "def diagnose_wrong(" not in src2:
    DIAG = '''

# ==================================================================
# diagnose_wrong — warm diagnosis for wrong answers
# ==================================================================

def diagnose_wrong(learner_text: str, expected_text: str) -> Optional[str]:
    """Warm-diagnosis signal for a wrong answer.

    Returns None if it looks correct.
    Returns 'sign_flip' if magnitudes match but signs differ.
    Returns 'partial' if a strict subset of roots is present.
    Returns 'unknown' otherwise.
    """
    if equivalent(learner_text, expected_text):
        return None

    # Best line from learner
    best_got = set()
    lines = learner_text.splitlines() if "\\n" in learner_text else [learner_text]
    for line in lines:
        g = set()
        for p in _parts(line):
            try:
                g.add(sp.sympify(p))
            except Exception:
                pass
        if len(g) > len(best_got):
            best_got = g

    want = set()
    for p in _parts(expected_text):
        try:
            want.add(sp.sympify(p))
        except Exception:
            pass

    if best_got and want:
        try:
            if {abs(x) for x in best_got} == {abs(x) for x in want} and best_got != want:
                return "sign_flip"
            if best_got < want and len(best_got) >= 1:
                return "partial"
        except Exception:
            pass

    return "unknown"
'''
    src2 = src2.rstrip() + DIAG
    print("FIX 5: re-added diagnose_wrong")
else:
    print("FIX 5: diagnose_wrong already present")

ast.parse(src2)
P2.write_text(src2, encoding="utf-8")
print()
print("math_grader.py written")