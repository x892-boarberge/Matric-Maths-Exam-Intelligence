"""Add the two missing quadratic generators AND register them."""
from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

# --- 1. Insert the two functions just before TEMPLATES ---
FUNCS = '''

def gen_quadratic_standard_factorable(count=50, seed=101):
    """x^2 + bx + c = 0 with integer roots."""
    import random
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 40:
        tries += 1
        r1 = rng.randint(-9, 9)
        r2 = rng.randint(-9, 9)
        if r1 == 0 or r2 == 0 or r1 == r2:
            continue
        key = tuple(sorted((r1, r2)))
        if key in seen:
            continue
        seen.add(key)
        b = -(r1 + r2)
        c = r1 * r2
        parts = ["x^2"]
        if b != 0:
            if b == 1:
                parts.append("+ x")
            elif b == -1:
                parts.append("- x")
            else:
                parts.append(f"{b:+d}x")
        if c != 0:
            parts.append(f"{c:+d}")
        expr = " ".join(parts)
        out.append({
            "problem": f"Solve {expr} = 0",
            "steps": [
                f"Standard form: {expr} = 0",
                f"Find two numbers that multiply to {c} and add to {b}.",
                f"That gives (x - ({r1}))(x - ({r2})) = 0",
                f"x = {r1}",
                f"x = {r2}",
                f"Answer: x = {r1} or x = {r2}",
            ],
            "note": "Always remember: b = -(sum of roots) and c = (product of roots).",
        })
    return out


def gen_quadratic_formula(count=50, seed=102):
    """ax^2 + bx + c = 0 with a > 1 — needs the formula."""
    import random
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 40:
        tries += 1
        a = rng.choice([2, 3, 4, 5])
        b = rng.randint(-9, 9)
        c = rng.randint(-9, 9)
        if b == 0 or c == 0:
            continue
        disc = b * b - 4 * a * c
        if disc <= 0 or int(disc ** 0.5) ** 2 == disc:
            continue
        key = (a, b, c)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "problem": f"Solve {a}x^2 {b:+d}x {c:+d} = 0 (correct to TWO decimal places)",
            "steps": [
                f"Standard form: {a}x^2 {b:+d}x {c:+d} = 0",
                "Formula: x = (-b +/- sqrt(b^2 - 4ac)) / 2a",
                f"Substitute: a = {a}, b = {b}, c = {c}",
                f"Discriminant: b^2 - 4ac = {disc}",
                "Keep full accuracy until the final two-decimal answer.",
            ],
            "note": "Always remember: write the formula, then substitute, then compute. Brackets around every negative.",
        })
    return out
'''

anchor = "TEMPLATES = {"
if anchor in src and "def gen_quadratic_standard_factorable" not in src:
    src = src.replace(anchor, FUNCS + "\n\n" + anchor, 1)
    print("Inserted 2 function definitions before TEMPLATES")
elif "def gen_quadratic_standard_factorable" in src:
    print("Functions already present")
else:
    print("WARN: TEMPLATES anchor not found")

# --- 2. Register both in TEMPLATES (using stats_iqr as anchor) ---
old_reg = '"stats_iqr":                     (gen_stats_iqr, 50),\n}'
new_reg = '''"stats_iqr":                     (gen_stats_iqr, 50),
    "quadratic_standard_factorable": (gen_quadratic_standard_factorable, 50),
    "quadratic_formula":             (gen_quadratic_formula, 50),
}'''

if '"quadratic_standard_factorable":' not in src.split("TEMPLATES = {")[1].split("}")[0] if "TEMPLATES = {" in src else True:
    if old_reg in src:
        src = src.replace(old_reg, new_reg, 1)
        print("Registered both templates")
    else:
        print("WARN: registration anchor not found")
else:
    print("Already registered")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)