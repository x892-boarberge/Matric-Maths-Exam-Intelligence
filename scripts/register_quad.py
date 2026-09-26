from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

old = '''    "stats_regression_written":      (gen_stats_regression_predict_v2, 50),
}'''

new = '''    "stats_regression_written":      (gen_stats_regression_predict_v2, 50),
    "quadratic_standard_factorable": (gen_quadratic_standard_factorable, 50),
    "quadratic_formula":             (gen_quadratic_formula, 50),
}'''

if old in src and '"quadratic_standard_factorable":' not in src.split("TEMPLATES = {")[1].split("\n}")[0]:
    src = src.replace(old, new, 1)
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Registered both templates")
    print("Syntax OK")
else:
    print("Anchor not found or already registered")