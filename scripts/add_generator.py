"""Append quadratic_standard_factorable generator."""
from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

if "def gen_quadratic_standard_factorable" in src:
    print("Already present")
    raise SystemExit(0)

NEW = '''

def _quad_term(b, c):
    """Format x^2 + bx + c for display."""
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
    return " ".join(parts)


def gen_quadratic_standard_factorable(count=50, seed=101):
    """x^2 + bx + c = 0 where b, c are integers and roots are integers."""
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
        out.append({
            "problem": "Solve " + _quad_term(b, c) + " = 0",
            "steps": [
                "Standard form: " + _quad_term(b, c) + " = 0",
                "Factorise the quadratic:",
                f"  Find two numbers that multiply to {c} and add to {b}.",
                f"  That gives (x - ({r1}))(x - ({r2})) = 0",
                f"x - ({r1}) = 0  gives  x = {r1}",
                f"x - ({r2}) = 0  gives  x = {r2}",
                f"Answer:  x = {r1}  or  x = {r2}",
            ],
            "note": "Always remember: b = -(sum of roots) and c = (product of roots).",
        })
    return out

'''

anchor = "TEMPLATES = {"
if anchor in src:
    src = src.replace(anchor, NEW + "\n" + anchor, 1)
    print("Inserted gen_quadratic_standard_factorable")
else:
    print("WARN: TEMPLATES anchor not found")

# Register in TEMPLATES
old_reg = '"quadratic_formula":              (gen_quadratic_formula, 50),'
new_reg = '''"quadratic_formula":              (gen_quadratic_formula, 50),
    "quadratic_standard_factorable":  (gen_quadratic_standard_factorable, 50),'''

if old_reg in src and "quadratic_standard_factorable" not in src.split("TEMPLATES = {")[1][:1500]:
    src = src.replace(old_reg, new_reg, 1)
    print("Registered in TEMPLATES")
elif "quadratic_standard_factorable" in src.split("TEMPLATES = {")[1][:1500] if "TEMPLATES = {" in src else False:
    print("Already registered")
else:
    print("WARN: registration anchor not found")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK, file written")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)