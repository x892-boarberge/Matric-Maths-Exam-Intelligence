"""Re-add the 8 generators (reverted by git checkout) — safe append."""
from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

# ============================================================
# 1. Append the 8 generator functions at the END of the file
# ============================================================
GENERATORS = '''

# ==================================================================
# Re-added generators (git checkout had reverted these)
# ==================================================================

def gen_cubic_concave_v2(count=50, seed=201):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([1, 2, -1, -2])
        b = rng.randint(-9, 9)
        if b == 0:
            continue
        cv = -2 * b / (6 * a)
        if a > 0:
            interval = f"x < {cv:.2f}"
        else:
            interval = f"x > {cv:.2f}"
        out.append({
            "problem": f"Find where f(x) = {a}x^3 + {b}x^2 is concave down.",
            "steps": [
                f"f'(x) = {3*a}x^2 + {2*b}x",
                f"f''(x) = {6*a}x + {2*b}",
                "Concave down when f''(x) < 0.",
                f"Critical value: x = {cv:.2f}",
                f"Answer: {interval}",
            ],
            "note": "Always remember: concave down means f''(x) < 0.",
        })
    return out


def gen_cubic_increasing_v2(count=50, seed=202):
    import random
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 30:
        tries += 1
        a = rng.randint(1, 10)
        c = rng.randint(-15, 15)
        key = (a, c)
        if key in seen:
            continue
        seen.add(key)
        c_term = f" + {c}" if c > 0 else (f" - {abs(c)}" if c < 0 else "")
        out.append({
            "problem": f"Find the interval where f(x) = x^3 - {3*a*a}x{c_term} is increasing.",
            "steps": [
                f"f'(x) = 3x^2 - {3*a*a}",
                "Increasing when f'(x) > 0.",
                f"Critical values: x = -{a} and x = {a}",
                f"Answer: x < -{a} or x > {a}",
            ],
            "note": "Always remember: increasing means f'(x) > 0. Use a sign line.",
        })
    return out


def gen_cubic_intercept_v2(count=50, seed=203):
    import random
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 10:
        tries += 1
        r1, r2, r3 = rng.randint(-6, 6), rng.randint(-6, 6), rng.randint(-6, 6)
        if r1 == r2 or r1 == r3 or r2 == r3:
            continue
        key = tuple(sorted([r1, r2, r3]))
        if key in seen:
            continue
        seen.add(key)
        terms = []
        for r in (r1, r2, r3):
            if r > 0:
                terms.append(f"(x - {r})")
            elif r < 0:
                terms.append(f"(x + {abs(r)})")
            else:
                terms.append("x")
        expr = "*".join(terms)
        out.append({
            "problem": f"Find the x-intercepts of f(x) = {expr}.",
            "steps": [
                "Set f(x) = 0.",
                f"x = {r1}",
                f"x = {r2}",
                f"x = {r3}",
                f"Answer: ({r1}; 0), ({r2}; 0), ({r3}; 0)",
            ],
            "note": "Always remember: cubic has at most 3 x-intercepts.",
        })
    return out


def gen_probability_conditional_v2(count=50, seed=204):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        pa = rng.choice([0.2, 0.3, 0.4, 0.5, 0.6])
        pab = rng.choice([0.05, 0.1, 0.15, 0.2, 0.25])
        if pab >= pa:
            continue
        out.append({
            "problem": f"P(A) = {pa}, P(A and B) = {pab}. Find P(B | A).",
            "steps": [
                "Formula: P(B | A) = P(A and B) / P(A)",
                f"= {pab} / {pa}",
                f"Answer: {pab/pa:.4f}",
            ],
            "note": "Always remember: divide by the given event.",
        })
    return out


def gen_quadratic_sequence_n_v2(count=50, seed=205):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        b = rng.randint(-8, 8)
        c = rng.randint(-20, 20)
        n_target = rng.randint(3, 15)
        T = n_target * n_target + b * n_target + c
        out.append({
            "problem": f"Quadratic sequence T_n = n^2 {b:+d}n {c:+d}. Find n if T_n = {T}.",
            "steps": [
                f"Set n^2 {b:+d}n {c:+d} = {T}",
                f"n^2 {b:+d}n {c - T:+d} = 0",
                "Factorise.",
                f"Positive integer solution: n = {n_target}",
            ],
            "note": "Always remember: reject non-positive n.",
        })
    return out


def gen_analytical_translation_v2(count=50, seed=206):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x1, y1 = rng.randint(-8, 8), rng.randint(-8, 8)
        dx, dy = rng.randint(-6, 6), rng.randint(-6, 6)
        if dx == 0 and dy == 0:
            continue
        x2, y2 = x1 + dx, y1 + dy
        out.append({
            "problem": f"Point A({x1}; {y1}) is translated by ({dx}; {dy}). Find A'.",
            "steps": [
                f"x' = {x1} + ({dx}) = {x2}",
                f"y' = {y1} + ({dy}) = {y2}",
                f"Answer: A'({x2}; {y2})",
            ],
            "note": "Always remember: right/up positive, left/down negative.",
        })
    return out


def gen_stats_sd_v2(count=50, seed=207):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        n = rng.choice([5, 7, 9])
        data = [rng.randint(1, 20) for _ in range(n)]
        mean = sum(data) / n
        var = sum((x - mean) ** 2 for x in data) / n
        sd = var ** 0.5
        out.append({
            "problem": f"Data: {', '.join(str(x) for x in data)}. Find the standard deviation.",
            "steps": [
                f"Mean = {sum(data)} / {n} = {mean:.2f}",
                "Compute squared deviations.",
                f"Variance = {var:.2f}",
                f"SD = sqrt(variance) = {sd:.2f}",
            ],
            "note": "Always remember: mean, deviations, variance, SD.",
        })
    return out


def gen_stats_regression_predict_v2(count=50, seed=208):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = round(rng.uniform(5, 50), 2)
        b = round(rng.uniform(-3, 3), 2)
        x = rng.randint(5, 50)
        y = round(a + b * x, 2)
        out.append({
            "problem": f"A least-squares regression line is y = {a} + {b}x. Predict y when x = {x}.",
            "steps": [
                f"y = {a} + ({b})({x})",
                f"Answer: y = {y}",
            ],
            "note": "Always remember: substitute before computing.",
        })
    return out

'''

# Append functions at end of file
src = src + GENERATORS
print("Appended 8 generator functions")

# ============================================================
# 2. Register them in TEMPLATES — add before the closing brace
# ============================================================
old_entries = '''    "quadratic_formula":             (gen_quadratic_formula, 50),
}'''
new_entries = '''    "quadratic_formula":             (gen_quadratic_formula, 50),
    "cubic_concave":                 (gen_cubic_concave_v2, 50),
    "cubic_increasing":              (gen_cubic_increasing_v2, 50),
    "cubic_intercept":               (gen_cubic_intercept_v2, 50),
    "probability_conditional":       (gen_probability_conditional_v2, 50),
    "quadratic_sequence_n":          (gen_quadratic_sequence_n_v2, 50),
    "analytical_translation":        (gen_analytical_translation_v2, 50),
    "stats_sd_written":              (gen_stats_sd_v2, 50),
    "stats_regression_written":      (gen_stats_regression_predict_v2, 50),
}'''

if old_entries in src:
    src = src.replace(old_entries, new_entries, 1)
    print("Registered 8 templates")
else:
    print("WARN: TEMPLATES anchor not found")
    # Try alternate form
    if '"quadratic_formula"' in src:
        idx = src.find('"quadratic_formula"')
        print(f"  Found at char {idx}")
        print(f"  Context: {src[idx:idx+200]!r}")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)