from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

if "quadratic_standard_factorable" in src.split("TEMPLATES = {")[1][:2000]:
    print("Already registered")
    raise SystemExit(0)

old = '    "quadratic_factored":            (gen_quadratic_factored, 200),'
new = '''    "quadratic_factored":            (gen_quadratic_factored, 200),
    "quadratic_standard_factorable": (gen_quadratic_standard_factorable, 50),'''

if old in src:
    src = src.replace(old, new, 1)
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Registered quadratic_standard_factorable (50 variants)")
else:
    print("WARN: anchor not found")