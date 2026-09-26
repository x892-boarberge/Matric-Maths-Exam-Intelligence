import sys
sys.path.insert(0, ".")
from src.tutor import analogue_generators as g

# Which function names are actually defined?
import inspect
defined = [name for name in dir(g) if name.startswith("gen_")]

for target in ["gen_cubic_concave", "gen_cubic_concave_v2",
               "gen_cubic_increasing", "gen_cubic_increasing_v2",
               "gen_cubic_intercept", "gen_cubic_intercept_v2",
               "gen_probability_conditional", "gen_probability_conditional_v2",
               "gen_quadratic_sequence_n", "gen_quadratic_sequence_n_v2",
               "gen_analytical_translation", "gen_analytical_translation_v2",
               "gen_stats_sd", "gen_stats_sd_v2",
               "gen_stats_regression_predict", "gen_stats_regression_predict_v2"]:
    print(f"  {target}: {target in defined}")

print()
# What does TEMPLATES actually register for these keys?
print("TEMPLATES entries:")
for key in ["cubic_concave", "cubic_increasing", "cubic_intercept",
            "probability_conditional", "quadratic_sequence_n",
            "analytical_translation", "stats_sd_written", "stats_regression_written"]:
    val = g.TEMPLATES.get(key)
    print(f"  {key}: {val}")