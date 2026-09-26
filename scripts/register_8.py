"""Register the 8 generators using the actual dict end as anchor."""
from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

# Check if already registered
if '"cubic_concave"' in src and '"stats_sd_written"' in src:
    print("Already registered")
    raise SystemExit(0)

# Actual anchor — the dict ends with stats_iqr then closing brace
old = '''    "stats_iqr":                     (gen_stats_iqr, 50),
}'''

new = '''    "stats_iqr":                     (gen_stats_iqr, 50),
    "cubic_concave":                 (gen_cubic_concave_v2, 50),
    "cubic_increasing":              (gen_cubic_increasing_v2, 50),
    "cubic_intercept":               (gen_cubic_intercept_v2, 50),
    "probability_conditional":       (gen_probability_conditional_v2, 50),
    "quadratic_sequence_n":          (gen_quadratic_sequence_n_v2, 50),
    "analytical_translation":        (gen_analytical_translation_v2, 50),
    "stats_sd_written":              (gen_stats_sd_v2, 50),
    "stats_regression_written":      (gen_stats_regression_predict_v2, 50),
}'''

if old in src:
    src = src.replace(old, new, 1)
    print("Registered 8 templates")
else:
    print("WARN: anchor not found")
    raise SystemExit(1)

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)