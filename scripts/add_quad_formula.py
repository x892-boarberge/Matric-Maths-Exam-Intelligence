"""Add the missing gen_quadratic_formula function."""
from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

if "def gen_quadratic_formula" in src:
    print("Already defined")
    raise SystemExit(0)

NEW = '''

def gen_quadratic_formula(count=50, seed=102):
    """ax^2 + bx + c = 0 where a>1 and roots are non-integer — needs the formula."""
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
if anchor in src:
    src = src.replace(anchor, NEW + "\n" + anchor, 1)
    print("Inserted gen_quadratic_formula")
else:
    print("WARN: TEMPLATES anchor not found")

ast.parse(src)
P.write_text(src, encoding="utf-8")
print("Syntax OK")