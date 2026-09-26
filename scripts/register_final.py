from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

# Use the actual last entry as anchor
old = '"stats_iqr":                     (gen_stats_iqr, 50),\n}'

if '"cubic_concave":' in src.split("TEMPLATES = {")[1].split("}")[0]:
    print("Already registered in TEMPLATES")
    raise SystemExit(0)

new = '''"stats_iqr":                     (gen_stats_iqr, 50),
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
    print("Anchor not found — searching")
    idx = src.rfind('"stats_iqr"')
    print("Context:", repr(src[idx:idx+120]))
    raise SystemExit(1)

ast.parse(src)
P.write_text(src, encoding="utf-8")
print("Syntax OK")