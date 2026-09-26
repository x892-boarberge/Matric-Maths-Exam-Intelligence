"""Add 8 missing generators — one script, all at once."""
from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

NEW = '''

# ==================================================================
# Fill-in generators — added to close the variant audit gaps
# ==================================================================

def gen_cubic_concave(count=50, seed=201):
    """f(x) = ax^3 + bx^2, find where concave down or up."""
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([1, 2, -1, -2])
        b = rng.randint(-9, 9)
        if b == 0:
            continue
        # f''(x) = 6ax + 2b
        cv = -2 * b / (6 * a)
        direction = "down" if a < 0 else "down" if a > 0 else "down"
        # Actually: concave down when f''(x) < 0
        if a > 0:
            interval = f"x < {cv:.2f}"
        else:
            interval = f"x > {cv:.2f}"
        out.append({
            "problem": f"Find where f(x) = {a}x^3 + {b}x^2 is concave down.",
            "steps": [
                f"Find f'(x) = {3*a}x^2 + {2*b}x",
                f"Find f''(x) = {6*a}x + {2*b}",
                f"Concave down when f''(x) < 0.",
                f"Critical value of f'': x = {cv:.2f}",
                f"Answer: concave down for {interval}",
            ],
            "note": "Always remember: concave down means f''(x) < 0, concave up means f''(x) > 0.",
        })
    return out


def gen_cubic_increasing(count=50, seed=202):
    """f(x) = x^3 + bx + c, find where increasing."""
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 10:
        tries += 1
        # Use f(x) = x^3 - 3a^2 x form: f' = 3x^2 - 3a^2 = 3(x-a)(x+a)
        a = rng.randint(1, 5)
        key = a
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "problem": f"Find the interval where f(x) = x^3 - {3*a*a}x is increasing.",
            "steps": [
                f"f'(x) = 3x^2 - {3*a*a}",
                "Increasing when f'(x) > 0.",
                f"Critical values: x = -{a} and x = {a}",
                f"Answer: x < -{a} or x > {a}",
            ],
            "note": "Always remember: increasing means f'(x) > 0. Use a sign line to check intervals.",
        })
    return out


def gen_cubic_intercept(count=50, seed=203):
    """Factored cubic — find x-intercepts."""
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 10:
        tries += 1
        r1 = rng.randint(-6, 6)
        r2 = rng.randint(-6, 6)
        r3 = rng.randint(-6, 6)
        if r1 == r2 or r1 == r3 or r2 == r3:
            continue
        key = tuple(sorted([r1, r2, r3]))
        if key in seen:
            continue
        seen.add(key)
        a = rng.choice([1, -1])
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
                "Each factor gives one root.",
                f"x = {r1}",
                f"x = {r2}",
                f"x = {r3}",
                f"Answer: ({r1}; 0), ({r2}; 0), ({r3}; 0)",
            ],
            "note": "Always remember: a cubic has at most 3 x-intercepts. Write them as coordinates.",
        })
    return out


def gen_probability_conditional(count=50, seed=204):
    """P(B | A) = P(A and B) / P(A)."""
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
            "note": "Always remember: conditional probability divides by the 'given' event.",
        })
    return out


def gen_quadratic_sequence_n(count=50, seed=205):
    """T_n = n^2 + bn + c, find n given T_n."""
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
                f"Set T_n = {T}: n^2 {b:+d}n {c:+d} = {T}",
                f"n^2 {b:+d}n {c - T:+d} = 0",
                f"Factorise or use the formula.",
                f"Positive integer solution: n = {n_target}",
            ],
            "note": "Always remember: reject non-positive n. Term numbers are positive integers.",
        })
    return out


def gen_analytical_translation(count=50, seed=206):
    """Translate point by vector, or describe translation."""
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
                "Translation: add the vector to the coordinates.",
                f"x' = {x1} + ({dx}) = {x2}",
                f"y' = {y1} + ({dy}) = {y2}",
                f"Answer: A'({x2}; {y2})",
            ],
            "note": "Always remember: right and up are positive; left and down are negative.",
        })
    return out


def gen_stats_sd(count=50, seed=207):
    """Standard deviation from a small dataset."""
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
                "Compute squared deviations from the mean.",
                f"Variance = {var:.2f}",
                f"Standard deviation = sqrt(variance) = {sd:.2f}",
            ],
            "note": "Always remember: find the mean first, then each deviation, then the variance, then the SD.",
        })
    return out


def gen_stats_regression_predict(count=50, seed=208):
    """Given regression line, predict y."""
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
                f"Substitute x = {x} into y = {a} + {b}x.",
                f"y = {a} + ({b})({x})",
                f"Answer: y = {y}",
            ],
            "note": "Always remember: substitute before computing. Show the substitution line.",
        })
    return out

'''

anchor = "TEMPLATES = {"
if anchor in src:
    src = src.replace(anchor, NEW + "\n" + anchor, 1)
    print("Inserted 8 fill-in generators")
else:
    print("WARN: TEMPLATES anchor not found")

# Register all in TEMPLATES
old_reg = '    "quadratic_formula":             (gen_quadratic_formula, 50),'
new_reg = '''    "quadratic_formula":             (gen_quadratic_formula, 50),
    "cubic_concave":                 (gen_cubic_concave, 50),
    "cubic_increasing":              (gen_cubic_increasing, 50),
    "cubic_intercept":               (gen_cubic_intercept, 50),
    "probability_conditional":       (gen_probability_conditional, 50),
    "quadratic_sequence_n":          (gen_quadratic_sequence_n, 50),
    "analytical_translation":        (gen_analytical_translation, 50),
    "stats_sd_written":              (gen_stats_sd, 50),
    "stats_regression_written":      (gen_stats_regression_predict, 50),'''

if old_reg in src and "cubic_concave" not in src.split("TEMPLATES = {")[1][:3000]:
    src = src.replace(old_reg, new_reg, 1)
    print("Registered all 8 in TEMPLATES")
else:
    print("WARN: registration anchor not found or already registered")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)